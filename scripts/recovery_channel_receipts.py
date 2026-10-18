"""Original minimized held receipts confined to generated synthetic recovery databases."""

import re
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from services.data_request_contracts import DataRequestInput
from services.data_requests import DataRequestService
from services.domain.messaging import InboundMessage, OutboundMessage
from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.legal_hold_contracts import HoldInput
from services.legal_holds import LegalHoldService
from services.staff import provision


def populate_channel_receipts(identity: IdentityService, token: str) -> None:
    with Session(identity.engine) as db:
        database = db.scalar(text("SELECT current_database()"))
        if not re.fullmatch(r"kasoma_drill_src_[0-9a-f]{32}", database or ""):
            raise ValueError("Synthetic holds require an isolated recovery source")
        owner = identity.authenticate(db, token, recent=True).user_id
    now, incoming, outgoing = identity.clock(), uuid4(), uuid4()
    with Session(identity.engine) as db, db.begin():
        db.add(
            InboundMessage(
                id=incoming,
                message_hash=uuid4().hex,
                request_hash=uuid4().hex,
                request_id=uuid4(),
                sender_hash=uuid4().hex,
                sender_encrypted=None,
                actor_id=owner,
                command="HELP",
                code_hash=None,
                status_reference=None,
                delivery_status=None,
                reply_reference=None,
                reply_encrypted=None,
                provider_at=now,
                received_at=now,
                available_at=now,
                processed_at=now,
                status="PROCESSED",
                attempts=1,
                error_code=None,
            )
        )
        db.flush()
        db.add(
            OutboundMessage(
                id=outgoing,
                inbound_id=incoming,
                link_id=None,
                actor_id=owner,
                recipient_hash=uuid4().hex,
                recipient_encrypted=None,
                template="HELP",
                link_revision=None,
                session_item_id=None,
                attempt_id=None,
                menu_topic_ids=None,
                status="SENT",
                provider_id="fake-recovery-" + uuid4().hex,
                attempts=1,
                error_code=None,
                created_at=now,
                available_at=now,
                sent_at=now,
                status_at=None,
            )
        )
    requests = DataRequestService(identity)
    target = requests.create(
        token, DataRequestInput(kind="DELETE", affirmative=True), uuid4(), uuid4()
    ).id
    email = "recovery-channel-admin@example.invalid"
    challenge = identity.request_otp(
        OTPRequest(identifier=email, device_id=uuid4()), "synthetic-recovery-channel", None
    )
    admin = identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    ).access_token
    provision(identity, email, "ADMIN")
    requests.claim(admin, target, uuid4(), uuid4())
    original = identity.settings.channel_receipt_holds_enabled
    identity.settings.channel_receipt_holds_enabled = True
    try:
        for kind, source in [
            ("CHANNEL_INBOUND_RECEIPT", incoming),
            ("CHANNEL_OUTBOUND_RECEIPT", outgoing),
        ]:
            LegalHoldService(identity).create(
                admin,
                target,
                HoldInput.model_validate(
                    {
                        "record_type": kind,
                        "record_id": source,
                        "decision_reference": uuid4(),
                        "reason": "LEGAL_OBLIGATION",
                        "expires_at": now + timedelta(days=365),
                        "affirmative": True,
                    }
                ),
                uuid4(),
                uuid4(),
            )
    finally:
        identity.settings.channel_receipt_holds_enabled = original
