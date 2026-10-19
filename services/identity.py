"""Transactional identity/consent policies. All tests inject clock and OTP randomness."""

import hashlib
import hmac
import json
import re
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from cryptography.fernet import Fernet
from sqlalchemy import Engine, delete, func, select, text, update
from sqlalchemy.orm import Session

from services.config import Settings
from services.domain.curriculum import Level, Subject
from services.domain.identity import (
    AuthSession,
    Challenge,
    Consent,
    Identifier,
    IdentityEvent,
    LearnerProfile,
    LearnerSubject,
    RateBucket,
    User,
)
from services.identity_contracts import (
    ConsentInput,
    Credentials,
    OTPAccepted,
    OTPRequest,
    OTPVerify,
    ProfilePatch,
    ProfileView,
    SubjectView,
)
from services.otp_observation import OTPObserver, observe
from services.providers import MessagingProvider


class IdentityError(Exception):
    def __init__(self, code: str, status: int = 400) -> None:
        self.code, self.status = code, status


def normalize(value: str) -> tuple[str, str]:
    value = value.strip()
    if re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", value):
        return "EMAIL", value.lower()
    if re.fullmatch(r"\+[1-9][0-9]{7,14}", value):
        return "PHONE", value
    raise IdentityError("VALIDATION_FAILED", 422)


class IdentityService:
    def __init__(
        self,
        engine: Engine,
        settings: Settings,
        email: MessagingProvider,
        sms: MessagingProvider,
        clock: Callable[[], datetime] | None = None,
        code: Callable[[], str] | None = None,
    ) -> None:
        self.engine, self.settings, self.email, self.sms = engine, settings, email, sms
        self.clock = clock or (lambda: datetime.now(UTC))
        self.code = code or (lambda: f"{secrets.randbelow(1_000_000):06d}")
        self.cipher = Fernet(settings.identity_encryption_key.get_secret_value().encode())
        self.key = settings.identity_lookup_key.get_secret_value().encode()

    def digest(self, purpose: str, value: str) -> str:
        return hmac.new(self.key, f"{purpose}:{value}".encode(), hashlib.sha256).hexdigest()

    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self.cipher.decrypt(value.encode()).decode()

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        with Session(self.engine) as db:
            try:
                yield db
            except IdentityError:
                # Failed guesses and refresh-reuse revocations must survive rejection.
                db.commit()
                raise
            else:
                db.commit()

    def lock(self, db: Session, key: str) -> None:
        number = int(self.digest("lock", key)[:15], 16)
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": number})

    def event(self, db: Session, user: UUID, action: str, request_id: str) -> None:
        db.add(
            IdentityEvent(
                id=uuid4(),
                user_id=user,
                type=action,
                version=1,
                payload={"request_id": request_id},
                created_at=self.clock(),
            )
        )

    def rate(self, db: Session, key: str, limit: int, seconds: int) -> bool:
        key = self.digest("rate", key)
        self.lock(db, key)
        bucket = db.scalar(select(RateBucket).where(RateBucket.key == key).with_for_update())
        now = self.clock()
        if bucket is None:
            bucket = RateBucket(key=key, count=0, expires_at=now + timedelta(seconds=seconds))
            db.add(bucket)
        elif bucket.expires_at <= now:
            bucket.count, bucket.expires_at = 0, now + timedelta(seconds=seconds)
        bucket.count += 1
        db.flush()
        return bucket.count <= limit

    def authenticate(self, db: Session, token: str | None, recent: bool = False) -> AuthSession:
        if not token:
            raise IdentityError("AUTH_REQUIRED", 401)
        session = db.scalar(
            select(AuthSession).where(AuthSession.access_hash == self.digest("access", token))
        )
        if session is None:
            raise IdentityError("AUTH_REQUIRED", 401)
        self.lock(db, str(session.user_id))
        db.refresh(session)
        user = db.get(User, session.user_id)
        if (
            session.revoked_at
            or session.rotated_at
            or session.access_expires_at <= self.clock()
            or user is None
            or user.status != "ACTIVE"
        ):
            raise IdentityError("AUTH_REQUIRED", 401)
        if recent and session.authenticated_at + timedelta(minutes=10) <= self.clock():
            raise IdentityError("REAUTH_REQUIRED", 401)
        return session

    def request_otp(
        self, body: OTPRequest, peer: str, token: str | None, *, observer: OTPObserver | None = None
    ) -> OTPAccepted:
        kind, identifier = normalize(body.identifier)
        lookup = self.digest("identifier", identifier)
        challenge_id = uuid4()
        with self.transaction() as db:
            owner = None
            if body.purpose != "LOGIN":
                owner = self.authenticate(db, token, recent=True).user_id
            now = self.clock()
            permitted = [
                self.rate(db, "peer:" + peer, 20, 3600),
                self.rate(db, "device:" + str(body.device_id), 10, 3600),
                self.rate(db, "identifier:" + lookup, 5, 3600),
                self.rate(db, "cooldown:" + lookup, 1, 60),
            ]
            if not all(permitted):
                return OTPAccepted(challenge_id=challenge_id)
            if body.purpose == "GUARDIAN" and db.scalar(
                select(Identifier.id).where(
                    Identifier.user_id == owner, Identifier.lookup_hash == lookup
                )
            ):
                return OTPAccepted(challenge_id=challenge_id)
            code = self.code()
            db.add(
                Challenge(
                    id=challenge_id,
                    purpose=body.purpose,
                    user_id=owner,
                    policy_version=self.settings.consent_policy_version,
                    type=kind,
                    lookup_hash=lookup,
                    encrypted_identifier=self.encrypt(identifier),
                    code_hash=self.digest(str(challenge_id), code),
                    attempts=0,
                    expires_at=now + timedelta(minutes=10),
                )
            )
        try:
            provider = self.email if kind == "EMAIL" else self.sms
            provider.send(identifier, f"Kasoma {body.purpose} code: {code}. Expires in 10 minutes.")
        except Exception:
            observe(observer, "EMAIL" if kind == "EMAIL" else "SMS", "FAILED")
            # No provider exception/body may reach logs or expose whether delivery succeeded.
            with self.transaction() as db:
                db.execute(delete(Challenge).where(Challenge.id == challenge_id))
        else:
            observe(observer, "EMAIL" if kind == "EMAIL" else "SMS", "RETURNED")
        return OTPAccepted(challenge_id=challenge_id)

    def consume(
        self, db: Session, body: OTPVerify, purposes: set[str], owner: UUID | None
    ) -> Challenge:
        challenge = db.scalar(
            select(Challenge).where(Challenge.id == body.challenge_id).with_for_update()
        )
        if (
            challenge is None
            or challenge.consumed_at
            or challenge.expires_at <= self.clock()
            or challenge.purpose not in purposes
            or challenge.user_id != owner
        ):
            raise IdentityError("OTP_INVALID")
        if challenge.attempts >= 5:
            raise IdentityError("OTP_RATE_LIMITED", 429)
        challenge.attempts += 1
        if not hmac.compare_digest(challenge.code_hash, self.digest(str(challenge.id), body.code)):
            raise IdentityError("OTP_INVALID")
        challenge.consumed_at = self.clock()
        challenge.code_hash = "consumed"
        return challenge

    def credentials(self, db: Session, user: UUID, old: AuthSession | None = None) -> Credentials:
        access, refresh = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
        now = self.clock()
        db.add(
            AuthSession(
                id=uuid4(),
                user_id=user,
                family=old.family if old else uuid4(),
                access_hash=self.digest("access", access),
                refresh_hash=self.digest("refresh", refresh),
                authenticated_at=old.authenticated_at if old else now,
                access_expires_at=now + timedelta(minutes=15),
                expires_at=old.expires_at if old else now + timedelta(days=30),
            )
        )
        return Credentials(access_token=access, refresh_token=refresh)

    def verify(self, body: OTPVerify, token: str | None, request_id: str) -> Credentials:
        with self.transaction() as db:
            owner = (
                self.authenticate(db, token, recent=True).user_id
                if body.purpose == "LINK"
                else None
            )
            challenge = self.consume(db, body, {"LINK"} if owner else {"LOGIN"}, owner)
            self.lock(db, challenge.lookup_hash)
            identifier = db.scalar(
                select(Identifier).where(
                    Identifier.type == challenge.type,
                    Identifier.lookup_hash == challenge.lookup_hash,
                )
            )
            if identifier and owner and identifier.user_id != owner:
                raise IdentityError("IDENTIFIER_UNAVAILABLE", 409)
            if identifier:
                user = identifier.user_id
                existing_user = db.get(User, user)
                if existing_user is None or existing_user.status != "ACTIVE":
                    raise IdentityError("AUTH_REQUIRED", 401)
            else:
                user = owner or uuid4()
                if not owner:
                    db.add(User(id=user, status="ACTIVE", created_at=self.clock()))
                    db.flush()
                    self.event(db, user, "registration.completed", request_id)
                db.add(
                    Identifier(
                        id=uuid4(),
                        user_id=user,
                        type=challenge.type,
                        normalized_value_encrypted=challenge.encrypted_identifier,
                        lookup_hash=challenge.lookup_hash,
                        verified_at=self.clock(),
                    )
                )
            self.event(db, user, "identity.verified", request_id)
            return self.credentials(db, user)

    def refresh(self, token: str) -> Credentials:
        with self.transaction() as db:
            old = db.scalar(
                select(AuthSession).where(AuthSession.refresh_hash == self.digest("refresh", token))
            )
            if old is None:
                raise IdentityError("AUTH_REQUIRED", 401)
            self.lock(db, str(old.user_id))
            db.refresh(old)
            if old.rotated_at:
                db.execute(
                    update(AuthSession)
                    .where(AuthSession.family == old.family)
                    .values(revoked_at=self.clock())
                )
                raise IdentityError("AUTH_REQUIRED", 401)
            user = db.get(User, old.user_id)
            if (
                old.revoked_at
                or old.expires_at <= self.clock()
                or not user
                or user.status != "ACTIVE"
            ):
                raise IdentityError("AUTH_REQUIRED", 401)
            old.rotated_at = self.clock()
            return self.credentials(db, old.user_id, old)

    def logout(self, token: str, all_sessions: bool, request_id: str) -> None:
        with self.transaction() as db:
            current = self.authenticate(db, token)
            condition = (
                AuthSession.user_id == current.user_id
                if all_sessions
                else (AuthSession.family == current.family)
            )
            db.execute(update(AuthSession).where(condition).values(revoked_at=self.clock()))
            self.event(db, current.user_id, "identity.logout", request_id)

    def subjects(self) -> list[SubjectView]:
        with Session(self.engine) as db:
            return [
                SubjectView(id=s.id, name=s.name)
                for s in db.scalars(
                    select(Subject)
                    .join(Level)
                    .where(Level.name == "S4", Subject.name.in_(["Mathematics", "Physics"]))
                )
            ]

    def profile(self, db: Session, user_id: UUID) -> ProfileView:
        user = db.get(User, user_id)
        if user is None:
            raise IdentityError("AUTH_REQUIRED", 401)
        required = {"PROFILE"}
        if user.birth_date:
            today = self.clock().date()
            age = (
                today.year
                - user.birth_date.year
                - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
            )
            required = {"SELF"} if age >= 18 else {"GUARDIAN", "ASSENT"}
        active = set(
            db.scalars(
                select(Consent.consent_type).where(
                    Consent.user_id == user_id,
                    Consent.revoked_at.is_(None),
                    Consent.policy_version == self.settings.consent_policy_version,
                )
            )
        )
        subjects = list(
            db.scalars(select(LearnerSubject.subject_id).where(LearnerSubject.user_id == user_id))
        )
        missing = sorted(required - active)
        return ProfileView(
            id=user_id,
            display_name=self.decrypt(user.display_name) if user.display_name else None,
            birth_date=user.birth_date,
            subject_ids=subjects,
            consent_required=missing,
            learning_allowed=not missing and bool(subjects),
            policy_version=self.settings.consent_policy_version,
            identifier_count=db.scalar(
                select(func.count()).select_from(Identifier).where(Identifier.user_id == user_id)
            )
            or 0,
        )

    def me(self, token: str) -> ProfileView:
        with self.transaction() as db:
            return self.profile(db, self.authenticate(db, token).user_id)

    def require_learning(self, token: str) -> UUID:
        profile = self.me(token)
        if not profile.learning_allowed:
            raise IdentityError("CONSENT_REQUIRED", 403)
        return profile.id

    def update_profile(self, token: str, body: ProfilePatch, request_id: str) -> ProfileView:
        with self.transaction() as db:
            current = self.authenticate(db, token, recent=True)
            user = db.get(User, current.user_id)
            if user is None:
                raise IdentityError("AUTH_REQUIRED", 401)
            if user.birth_date and body.birth_date != user.birth_date:
                raise IdentityError("BIRTH_DATE_LOCKED", 409)
            if body.birth_date >= self.clock().date() or not body.display_name.strip():
                raise IdentityError("VALIDATION_FAILED", 422)
            allowed = {s.id for s in self.subjects()}
            if not set(body.subject_ids) <= allowed or len(set(body.subject_ids)) != len(
                body.subject_ids
            ):
                raise IdentityError("VALIDATION_FAILED", 422)
            level = db.scalar(select(Level).where(Level.name == "S4"))
            if level is None:
                raise IdentityError("SERVICE_UNAVAILABLE", 503)
            user.birth_date, user.display_name = (
                body.birth_date,
                self.encrypt(body.display_name.strip()),
            )
            if db.get(LearnerProfile, user.id) is None:
                db.add(LearnerProfile(user_id=user.id, level_id=level.id))
                db.flush()
            db.execute(delete(LearnerSubject).where(LearnerSubject.user_id == user.id))
            db.add_all([LearnerSubject(user_id=user.id, subject_id=s) for s in body.subject_ids])
            self.event(db, user.id, "profile.updated", request_id)
            db.flush()
            return self.profile(db, user.id)

    def consent(self, token: str, body: ConsentInput, key: UUID, request_id: str) -> ProfileView:
        with self.transaction() as db:
            current = self.authenticate(db, token, recent=True)
            user_id = current.user_id
            fingerprint = self.digest("consent-request", body.model_dump_json())
            previous = db.scalar(
                select(Consent).where(Consent.user_id == user_id, Consent.idempotency_key == key)
            )
            if previous:
                if previous.request_hash != fingerprint:
                    raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
                return self.profile(db, user_id)
            profile = self.profile(db, user_id)
            if body.policy_version != profile.policy_version:
                raise IdentityError("VERSION_CONFLICT", 409)
            if profile.birth_date is None:
                raise IdentityError("CONSENT_REQUIRED", 403)
            evidence = None
            if body.consent_type == "WITHDRAW":
                db.execute(
                    update(Consent)
                    .where(Consent.user_id == user_id, Consent.revoked_at.is_(None))
                    .values(revoked_at=self.clock())
                )
            else:
                if body.consent_type not in profile.consent_required:
                    raise IdentityError("VALIDATION_FAILED", 422)
                if body.consent_type == "GUARDIAN":
                    if not (
                        body.guardian_name
                        and body.guardian_name.strip()
                        and body.guardian_relationship
                        and body.guardian_relationship.strip()
                        and body.challenge_id
                        and body.code
                    ):
                        raise IdentityError("VALIDATION_FAILED", 422)
                    challenge = self.consume(
                        db,
                        OTPVerify(challenge_id=body.challenge_id, code=body.code),
                        {"GUARDIAN"},
                        user_id,
                    )
                    if challenge.policy_version != profile.policy_version:
                        raise IdentityError("VERSION_CONFLICT", 409)
                    if db.scalar(
                        select(Identifier.id).where(
                            Identifier.user_id == user_id,
                            Identifier.lookup_hash == challenge.lookup_hash,
                        )
                    ):
                        raise IdentityError("VALIDATION_FAILED", 422)
                    evidence = self.encrypt(
                        json.dumps(
                            {
                                "guardian_name": body.guardian_name,
                                "relationship": body.guardian_relationship,
                                "contact": self.decrypt(challenge.encrypted_identifier),
                                "verification_method": "OTP",
                                "challenge_id": str(challenge.id),
                            }
                        )
                    )
            db.add(
                Consent(
                    id=uuid4(),
                    user_id=user_id,
                    consent_type=body.consent_type,
                    basis="synthetic-development-declaration",
                    policy_version=body.policy_version,
                    evidence_encrypted=evidence,
                    granted_at=self.clock(),
                    revoked_at=self.clock() if body.consent_type == "WITHDRAW" else None,
                    idempotency_key=key,
                    request_hash=fingerprint,
                )
            )
            self.event(db, user_id, "consent.changed", request_id)
            db.flush()
            return self.profile(db, user_id)
