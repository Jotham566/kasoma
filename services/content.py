"""Content workflow: authorization, validation and audit share one transaction."""

import hashlib
import json
import math
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from services.content_contracts import (
    CHECKLIST,
    CatalogEntry,
    ContentContext,
    CreateDraft,
    DraftDocument,
    EditDraft,
    ReviewInput,
    ReviewView,
    Transition,
    VersionPage,
    VersionView,
)
from services.domain.content import (
    AuditLog,
    ContentEvent,
    ContentReceipt,
    ContentReview,
    Item,
    ItemMapping,
    ItemVersion,
)
from services.domain.curriculum import Competency, Concept, Level, Subject, Topic
from services.domain.flags import ContentFlag
from services.identity import IdentityError, IdentityService
from services.numeric import specification_errors
from services.staff import authorize

READ_ROLES = {"CONTENT_AUTHOR", "ACADEMIC_REVIEWER", "ADMIN"}
PUBLISHABLE_RIGHTS = {
    "ORIGINAL_KASOMA",
    "LICENSED",
    "PUBLIC_DOMAIN_CONFIRMED",
    "PERMISSION_CONFIRMED",
}


class ContentError(IdentityError):
    def __init__(self, code: str, fields: list[str] | None = None, status: int = 409) -> None:
        super().__init__(code, status)
        self.fields = fields or []


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class ContentService:
    def __init__(self, identity: IdentityService) -> None:
        self.identity = identity

    def view(self, db: Session, version: ItemVersion) -> VersionView:
        item = db.get(Item, version.item_id)
        if item is None:
            raise ContentError("RESOURCE_NOT_FOUND", status=404)
        return VersionView(
            id=version.id,
            item_id=item.id,
            subject_id=item.subject_id,
            author_id=version.author_id,
            version=version.version,
            revision=version.revision,
            status=version.status,
            document=DraftDocument.model_validate(version.document),
            requires_second_review=version.requires_second_review,
            approval_count=self.approvals(db, version),
            created_at=version.created_at,
            updated_at=version.updated_at,
        )

    def disputed(self, db: Session, item_id: UUID) -> bool:
        return (
            db.scalar(
                select(ContentFlag.id)
                .where(
                    ContentFlag.item_id == item_id,
                    ContentFlag.category.in_(["QUESTION_ERROR", "GRADE_DISPUTE", "UNSAFE_CONTENT"]),
                    ContentFlag.status != "DISMISSED",
                )
                .limit(1)
            )
            is not None
        )

    def approvals(self, db: Session, version: ItemVersion) -> int:
        return (
            db.scalar(
                select(func.count())
                .select_from(ContentReview)
                .where(
                    ContentReview.item_version_id == version.id,
                    ContentReview.review_round == version.review_round,
                    ContentReview.decision == "APPROVE",
                    ContentReview.content_hash == version.content_hash,
                )
            )
            or 0
        )

    def authorized_version(
        self, db: Session, actor: UUID, roles: set[str], version_id: UUID, lock: bool = False
    ) -> ItemVersion:
        query = select(ItemVersion).where(ItemVersion.id == version_id)
        version = db.scalar(query.with_for_update() if lock else query)
        if version is None or (roles <= {"CONTENT_AUTHOR"} and version.author_id != actor):
            raise ContentError("RESOURCE_NOT_FOUND", status=404)
        return version

    def context(self, token: str) -> ContentContext:
        with self.identity.transaction() as db:
            actor, roles = authorize(self.identity, db, token, READ_ROLES)
            subjects = list(
                db.scalars(
                    select(Subject)
                    .join(Level)
                    .where(Level.name == "S4", Subject.name.in_(["Mathematics", "Physics"]))
                )
            )
            topics = list(
                db.scalars(select(Topic).where(Topic.subject_id.in_([s.id for s in subjects])))
            )
            concepts = list(
                db.scalars(
                    select(Concept).where(
                        Concept.topic_id.in_([t.id for t in topics]), Concept.synthetic.is_(True)
                    )
                )
            )
            return ContentContext(
                actor_id=actor,
                roles=sorted(roles),
                subjects=[CatalogEntry(id=s.id, name=s.name) for s in subjects],
                topics=[CatalogEntry(id=t.id, name=t.name, parent_id=t.subject_id) for t in topics],
                concepts=[
                    CatalogEntry(
                        id=c.id,
                        name=c.name,
                        parent_id=c.topic_id,
                        syllabus_reference=c.syllabus_reference,
                    )
                    for c in concepts
                ],
                competencies=[
                    CatalogEntry(id=c.id, name=c.name) for c in db.scalars(select(Competency))
                ],
                checklist=sorted(CHECKLIST),
            )

    def list_versions(self, token: str, cursor: UUID | None, limit: int) -> VersionPage:
        with self.identity.transaction() as db:
            actor, roles = authorize(self.identity, db, token, READ_ROLES)
            query = select(ItemVersion).order_by(ItemVersion.id).limit(limit + 1)
            if not roles & {"ACADEMIC_REVIEWER", "ADMIN"}:
                query = query.where(ItemVersion.author_id == actor)
            if cursor:
                query = query.where(ItemVersion.id > cursor)
            versions = list(db.scalars(query))
            return VersionPage(
                data=[self.view(db, v) for v in versions[:limit]],
                next_cursor=versions[limit - 1].id if len(versions) > limit else None,
            )

    def get(self, token: str, version_id: UUID) -> VersionView:
        with self.identity.transaction() as db:
            actor, roles = authorize(self.identity, db, token, READ_ROLES)
            return self.view(db, self.authorized_version(db, actor, roles, version_id))

    def reviews(self, token: str, version_id: UUID) -> list[ReviewView]:
        with self.identity.transaction() as db:
            actor, roles = authorize(self.identity, db, token, READ_ROLES)
            self.authorized_version(db, actor, roles, version_id)
            return [
                ReviewView(
                    reviewer_id=r.reviewer_id,
                    decision=r.decision,
                    reason=r.reason,
                    checklist=r.checklist,
                    created_at=r.created_at,
                )
                for r in db.scalars(
                    select(ContentReview)
                    .where(ContentReview.item_version_id == version_id)
                    .order_by(ContentReview.created_at, ContentReview.id)
                )
            ]

    def validate(
        self, db: Session, subject_id: UUID, document: DraftDocument, complete: bool
    ) -> None:
        fields = []
        subject = db.scalar(
            select(Subject)
            .join(Level)
            .where(
                Subject.id == subject_id,
                Level.name == "S4",
                Subject.name.in_(["Mathematics", "Physics"]),
            )
        )
        if subject is None:
            fields.append("subject_id")
        topic = db.get(Topic, document.topic_id) if document.topic_id else None
        concept = db.get(Concept, document.concept_id) if document.concept_id else None
        if document.topic_id and (topic is None or topic.subject_id != subject_id):
            fields.append("topic_id")
        if document.concept_id and (
            concept is None or concept.topic_id != document.topic_id or not concept.synthetic
        ):
            fields.append("concept_id")
        mapping_ids = [m.competency_id for m in document.competency_mappings]
        known = set(db.scalars(select(Competency.id)))
        if len(mapping_ids) != len(set(mapping_ids)) or not set(mapping_ids) <= known:
            fields.append("competency_mappings")
        for prerequisite in document.prerequisite_concept_ids:
            valid = db.scalar(
                select(Concept)
                .join(Topic)
                .where(
                    Concept.id == prerequisite,
                    Topic.subject_id == subject_id,
                    Concept.synthetic.is_(True),
                )
            )
            if valid is None or prerequisite == document.concept_id:
                fields.append("prerequisite_concept_ids")
                break
        if document.equivalents:
            from services.reassessment_engine import near_duplicate, same_skill

            equivalent_ids = [claim.version_id for claim in document.equivalents]
            if len(equivalent_ids) != len(set(equivalent_ids)):
                fields.append("equivalents")
            for claim in document.equivalents:
                target = db.get(ItemVersion, claim.version_id)
                target_item = db.get(Item, target.item_id) if target else None
                if (
                    target is None
                    or target.status != "APPROVED"
                    or not target.synthetic
                    or target_item is None
                    or target_item.subject_id != subject_id
                ):
                    fields.append("equivalents")
                    continue
                other = DraftDocument.model_validate(target.document)
                if not same_skill(document, other) or near_duplicate(document.prompt, other.prompt):
                    fields.append("equivalents")
        if complete:
            for field in [
                "title",
                "prompt",
                "learning_outcome_reference",
                "worked_solution",
                "remediation",
                "source",
                "rights_evidence",
                "rights_conditions",
            ]:
                if not getattr(document, field).strip():
                    fields.append(field)
            if topic is None:
                fields.append("topic_id")
            if concept is None:
                fields.append("concept_id")
            elif document.learning_outcome_reference != concept.syllabus_reference:
                fields.append("learning_outcome_reference")
            if not mapping_ids or not math.isclose(
                sum(m.weight for m in document.competency_mappings), 1, abs_tol=1e-6
            ):
                fields.append("competency_mappings")
            if document.response_type in {"SINGLE_CHOICE", "MULTIPLE_CHOICE"}:
                choices = document.choices
                ids = {c.id for c in choices}
                if (
                    len(choices) < 2
                    or len(ids) != len(choices)
                    or any(not c.text.strip() for c in choices)
                ):
                    fields.append("choices")
                if document.response_type == "SINGLE_CHOICE":
                    if document.correct_choice_id not in ids:
                        fields.append("correct_choice_id")
                    if document.correct_choice_ids:
                        fields.append("correct_choice_ids")
                else:
                    if (
                        not document.correct_choice_ids
                        or not set(document.correct_choice_ids) <= ids
                    ):
                        fields.append("correct_choice_ids")
                    if document.correct_choice_id:
                        fields.append("correct_choice_id")
                if document.numeric_spec is not None:
                    fields.append("numeric_spec")
            else:
                if document.choices or document.correct_choice_id or document.correct_choice_ids:
                    fields.append("choices")
                if document.numeric_spec is None:
                    fields.append("numeric_spec")
                else:
                    fields.extend(
                        "numeric_spec." + f for f in specification_errors(document.numeric_spec)
                    )
            if document.rights_status not in PUBLISHABLE_RIGHTS:
                fields.append("rights_status")
        if fields:
            raise ContentError("CONTENT_VALIDATION_FAILED", sorted(set(fields)))

    def mapping_rows(self, db: Session, version: ItemVersion, document: DraftDocument) -> None:
        db.execute(delete(ItemMapping).where(ItemMapping.item_version_id == version.id))
        db.add_all(
            [
                ItemMapping(
                    item_version_id=version.id, competency_id=m.competency_id, weight=m.weight
                )
                for m in document.competency_mappings
            ]
        )
        db.flush()

    def audit(
        self,
        db: Session,
        actor: UUID,
        version: ItemVersion,
        action: str,
        reason: str,
        request_id: UUID,
        before: str | None,
    ) -> None:
        db.add(
            AuditLog(
                id=uuid4(),
                actor_id=actor,
                target_id=version.id,
                action=action,
                reason=reason,
                request_id=request_id,
                before_hash=before,
                after_hash=version.content_hash,
                created_at=self.identity.clock(),
            )
        )
        db.add(
            ContentEvent(
                id=uuid4(),
                item_version_id=version.id,
                type=action,
                version=1,
                request_id=request_id,
                created_at=self.identity.clock(),
            )
        )

    def replay(
        self, db: Session, actor: UUID, roles: set[str], key: UUID, fingerprint: str
    ) -> VersionView | None:
        receipt = db.get(ContentReceipt, (actor, key))
        if receipt:
            if receipt.request_hash != fingerprint:
                raise ContentError("IDEMPOTENCY_CONFLICT")
            return self.view(db, self.authorized_version(db, actor, roles, receipt.item_version_id))
        return None

    def create(self, token: str, body: CreateDraft, key: UUID, request_id: UUID) -> VersionView:
        with self.identity.transaction() as db:
            actor, roles = authorize(self.identity, db, token, {"CONTENT_AUTHOR"}, recent=True)
            fingerprint = digest({"action": "create", "body": body.model_dump(mode="json")})
            replay = self.replay(db, actor, roles, key, fingerprint)
            if replay:
                return replay
            self.validate(db, body.subject_id, body.document, complete=False)
            if not body.change_reason.strip():
                raise ContentError("CONTENT_VALIDATION_FAILED", ["change_reason"])
            now = self.identity.clock()
            second_review = body.document.high_risk
            if body.source_version_id:
                source = self.authorized_version(db, actor, roles, body.source_version_id)
                item = db.scalar(select(Item).where(Item.id == source.item_id).with_for_update())
                if (
                    item is None
                    or item.author_id != actor
                    or item.subject_id != body.subject_id
                    or source.status not in {"APPROVED", "RETIRED"}
                ):
                    raise ContentError("FORBIDDEN", status=403)
                pending = db.scalar(
                    select(ItemVersion.id).where(
                        ItemVersion.item_id == item.id,
                        ItemVersion.status.in_(["DRAFT", "IN_REVIEW"]),
                    )
                )
                if pending:
                    raise ContentError("VERSION_CONFLICT")
                version_number = (
                    db.scalar(
                        select(func.max(ItemVersion.version)).where(ItemVersion.item_id == item.id)
                    )
                    or 0
                ) + 1
                second_review = (
                    second_review or source.requires_second_review or self.disputed(db, item.id)
                )
            else:
                item = Item(id=uuid4(), subject_id=body.subject_id, author_id=actor, created_at=now)
                db.add(item)
                db.flush()
                version_number = 1
            document = body.document.model_dump(mode="json")
            version = ItemVersion(
                id=uuid4(),
                item_id=item.id,
                author_id=actor,
                version=version_number,
                revision=1,
                review_round=0,
                status="DRAFT",
                document=document,
                content_hash=digest(document),
                topic_id=body.document.topic_id,
                concept_id=body.document.concept_id,
                requires_second_review=second_review,
                synthetic=True,
                created_at=now,
                updated_at=now,
            )
            db.add(version)
            db.flush()
            self.mapping_rows(db, version, body.document)
            db.add(
                ContentReceipt(
                    actor_id=actor, key=key, request_hash=fingerprint, item_version_id=version.id
                )
            )
            self.audit(db, actor, version, "content.created", body.change_reason, request_id, None)
            db.flush()
            return self.view(db, version)

    def mutate(
        self,
        token: str,
        version_id: UUID,
        action: str,
        body: EditDraft | Transition | ReviewInput,
        key: UUID,
        request_id: UUID,
    ) -> VersionView:
        required = {"CONTENT_AUTHOR"} if action in {"edit", "submit"} else {"ACADEMIC_REVIEWER"}
        if action == "retire":
            required.add("ADMIN")
        with self.identity.transaction() as db:
            actor, roles = authorize(self.identity, db, token, required, recent=True)
            fingerprint = digest(
                {"action": action, "target": str(version_id), "body": body.model_dump(mode="json")}
            )
            replay = self.replay(db, actor, roles, key, fingerprint)
            if replay:
                return replay
            version = self.authorized_version(db, actor, roles, version_id, lock=True)
            if action in {"edit", "submit"} and version.author_id != actor:
                raise ContentError("FORBIDDEN", status=403)
            if version.revision != body.expected_revision:
                raise ContentError("VERSION_CONFLICT")
            reason = body.change_reason if isinstance(body, EditDraft) else body.reason
            if not reason.strip():
                raise ContentError("CONTENT_VALIDATION_FAILED", ["reason"])
            before = version.content_hash
            document = DraftDocument.model_validate(version.document)
            item = db.scalar(select(Item).where(Item.id == version.item_id).with_for_update())
            if item is None:
                raise ContentError("RESOURCE_NOT_FOUND", status=404)
            if action == "edit" and isinstance(body, EditDraft):
                if version.status != "DRAFT":
                    raise ContentError("VERSION_CONFLICT")
                self.validate(db, item.subject_id, body.document, complete=False)
                # Mapping triggers see DRAFT before the version row is changed.
                self.mapping_rows(db, version, body.document)
                version.document = body.document.model_dump(mode="json")
                version.content_hash = digest(version.document)
                version.topic_id, version.concept_id = (
                    body.document.topic_id,
                    body.document.concept_id,
                )
                version.requires_second_review |= body.document.high_risk
            elif action == "submit":
                if version.status != "DRAFT":
                    raise ContentError("VERSION_CONFLICT")
                self.validate(db, item.subject_id, document, complete=True)
                version.status = "IN_REVIEW"
                version.review_round += 1
            elif action == "review" and isinstance(body, ReviewInput):
                if version.author_id == actor:
                    raise ContentError("SELF_REVIEW_FORBIDDEN")
                if version.status != "IN_REVIEW":
                    raise ContentError("VERSION_CONFLICT")
                if db.scalar(
                    select(ContentReview.id).where(
                        ContentReview.item_version_id == version.id,
                        ContentReview.review_round == version.review_round,
                        ContentReview.reviewer_id == actor,
                    )
                ):
                    raise ContentError("DUPLICATE_REVIEW")
                if body.decision == "APPROVE":
                    for claim in document.equivalents:
                        target_version = db.get(ItemVersion, claim.version_id)
                        if target_version is not None and target_version.author_id == actor:
                            raise ContentError("SELF_REVIEW_FORBIDDEN")
                    self.validate(db, item.subject_id, document, complete=True)
                    if set(body.checklist) != CHECKLIST or len(body.checklist) != len(CHECKLIST):
                        raise ContentError("CONTENT_VALIDATION_FAILED", ["checklist"])
                db.add(
                    ContentReview(
                        id=uuid4(),
                        item_version_id=version.id,
                        reviewer_id=actor,
                        content_hash=version.content_hash,
                        review_round=version.review_round,
                        decision=body.decision,
                        checklist=body.checklist,
                        reason=reason,
                        created_at=self.identity.clock(),
                    )
                )
                db.flush()
                # Read before mutating: an autoflush must not persist review escalation
                # before the version revision is incremented below.
                second_review_required = (
                    version.requires_second_review
                    or body.require_second_review
                    or self.disputed(db, item.id)
                )
                approvals = self.approvals(db, version)
                version.requires_second_review = second_review_required
                if body.decision == "RETURN":
                    version.status = "DRAFT"
                elif approvals >= (2 if second_review_required else 1):
                    version.status = "APPROVED"
            elif action == "retire":
                if version.status != "APPROVED":
                    raise ContentError("VERSION_CONFLICT")
                version.status = "RETIRED"
            else:
                raise ContentError("VALIDATION_FAILED", status=422)
            version.revision += 1
            version.updated_at = self.identity.clock()
            db.flush()
            db.add(
                ContentReceipt(
                    actor_id=actor, key=key, request_hash=fingerprint, item_version_id=version.id
                )
            )
            self.audit(db, actor, version, "content." + action, reason, request_id, before)
            db.flush()
            return self.view(db, version)

    def eligible_version(
        self, db: Session, version_id: UUID, subject_id: UUID, synthetic: bool = False
    ) -> ItemVersion:
        """Internal selector for later assessment; no answer-bearing learner endpoint."""
        version = db.scalar(
            select(ItemVersion)
            .join(Item)
            .join(Subject)
            .join(Level)
            .where(
                ItemVersion.id == version_id,
                ItemVersion.status == "APPROVED",
                ItemVersion.synthetic == synthetic,
                Item.subject_id == subject_id,
                Subject.name.in_(["Mathematics", "Physics"]),
                Level.name == "S4",
            )
        )
        if version is None:
            raise ContentError("CONTENT_NOT_APPROVED", status=404)
        return version

    def assessment_candidates(
        self,
        db: Session,
        subject_id: UUID,
        topic_id: UUID,
        excluded: set[UUID],
        count: int,
        lock: bool = True,
    ) -> list[ItemVersion]:
        """Local synthetic planner; publication remains this module's authority."""
        versions = db.scalars(
            select(ItemVersion)
            .join(Item)
            .join(Subject)
            .join(Level)
            .where(
                Item.subject_id == subject_id,
                ItemVersion.topic_id == topic_id,
                ItemVersion.status == "APPROVED",
                ItemVersion.synthetic.is_(True),
                Subject.name.in_(["Mathematics", "Physics"]),
                Level.name == "S4",
                Item.id.not_in(excluded),
            )
            .order_by(Item.id, ItemVersion.version.desc())
        )
        result: list[ItemVersion] = []
        seen: set[UUID] = set()
        for version in versions:
            if version.item_id in seen:
                continue
            seen.add(version.item_id)
            document = DraftDocument.model_validate(version.document)
            if "WEB" not in document.channel_suitability:
                continue
            if lock:
                db.refresh(version, with_for_update=True)
            if version.status != "APPROVED":
                continue
            result.append(version)
            if len(result) == count:
                break
        return result

    def assessment_version(self, db: Session, version_id: UUID, subject_id: UUID) -> ItemVersion:
        version = self.eligible_version(db, version_id, subject_id, synthetic=True)
        db.refresh(version, with_for_update=True)
        if version.status != "APPROVED":
            raise ContentError("CONTENT_NOT_APPROVED", status=409)
        return version
