"""Synthetic encrypted objects held only in memory for the logical recovery drill."""

from dataclasses import dataclass, field
from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from scripts.recovery_channel_receipts import ChannelHoldAuthority
from services.data_request_contracts import DataRequestInput
from services.data_requests import DataRequestService
from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_artifacts import read_artifact
from services.export_jobs import queue
from services.export_processing import process_one
from services.identity import IdentityService
from services.legal_hold_contracts import HoldInput
from services.legal_holds import LegalHoldService


@dataclass(repr=False)
class RecoveryExport:
    objects: dict[tuple[UUID, UUID], bytes] = field(default_factory=dict)
    target: UUID | None = None
    frozen: bytes = b""

    def put(self, generation: UUID, object_id: UUID, ciphertext: bytes) -> None:
        self.objects[generation, object_id] = ciphertext

    def get(self, generation: UUID, object_id: UUID) -> bytes:
        return self.objects[generation, object_id]

    def read(self, identity: IdentityService) -> bytes:
        # Read-only verification: do not create auth/rate/audit rows in either database.
        with Session(identity.engine) as db:
            request = db.get(DataRequest, self.target)
            job = db.get(ExportJob, self.target)
            generation = db.get(ExportGeneration, job.generation_id) if job else None
            if (
                request is None
                or job is None
                or job.status != "READY"
                or job.grant_family is not None
                or job.grant_authenticated_at is not None
                or generation is None
                or generation.encrypted_manifest is None
                or generation.published_at != request.completed_at
                or generation.digest != request.export_digest
            ):
                raise RuntimeError("Synthetic export publication evidence is incomplete")
            raw = b"".join(
                read_artifact(
                    identity.decrypt(generation.encrypted_manifest).encode(),
                    identity,
                    lambda object_id: self.get(generation.id, object_id),
                    request_id=request.id,
                    generation_id=generation.id,
                )
            )
            if len(raw) != generation.size:
                raise RuntimeError("Synthetic export length mismatch")
            return raw

    def verify(self, identity: IdentityService) -> None:
        if not self.frozen or self.read(identity) != self.frozen:
            raise RuntimeError("Restored synthetic export bytes differ")


def populate_export(
    identity: IdentityService, token: str, authority: ChannelHoldAuthority
) -> RecoveryExport:
    state = RecoveryExport()
    state.target = (
        DataRequestService(identity)
        .create(token, DataRequestInput(kind="EXPORT", affirmative=True), uuid4(), uuid4())
        .id
    )
    queue(identity, token, state.target, uuid4(), uuid4())
    if not process_one(identity, state):
        raise RuntimeError("Synthetic export could not be prepared")
    state.frozen = state.read(identity)
    # The existing independent synthetic case authorizes this exact original receipt.
    holds = LegalHoldService(identity)
    admin = authority.token.get_secret_value()
    references = holds.export_sources(admin, authority.request_id, state.target, None, 50, uuid4())
    original = identity.settings.export_evidence_holds_enabled
    identity.settings.export_evidence_holds_enabled = True
    try:
        holds.create(
            admin,
            authority.request_id,
            HoldInput(
                record_type="DATA_REQUEST_RECEIPT",
                record_id=references.receipt_ids[0],
                decision_reference=uuid4(),
                reason="LEGAL_OBLIGATION",
                expires_at=identity.clock() + timedelta(days=1),
                affirmative=True,
            ),
            uuid4(),
            uuid4(),
        )
    finally:
        identity.settings.export_evidence_holds_enabled = original
    return state
