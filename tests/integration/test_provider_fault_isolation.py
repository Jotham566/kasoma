"""ADR-050: stalled fake inference cannot hold web reads or publish failed evidence."""

from concurrent.futures import ThreadPoolExecutor, wait
from threading import Event
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.domain.assessment import Grade
from services.domain.grading_audits import GradingAuditAssignment, GradingPublication
from services.domain.grading_work import GradingWorkRow
from services.domain.mastery import MasteryEvidence
from services.providers import FakeModelProvider
from services.short_text_processor import ShortTextProcessor
from tests.integration.test_short_text_flow import save_short, start_short
from tests.integration.test_short_text_flow import short_text as short_text_fixture

short_text = short_text_fixture
pytestmark = pytest.mark.integration


@pytest.mark.parametrize("fault", ["TIMEOUT", "UNAVAILABLE", "FALLBACK"])
def test_stalled_fake_call_allows_fifty_web_reads_then_one_neutral_outcome(
    short_text, fault, caplog
):
    identity, client, actors, plan, policy, _ = short_text
    session, item = start_short(short_text)
    key = str(uuid4())
    pending = save_short(short_text, session, item, key).json()
    entered, release = Event(), Event()

    class StalledProvider(FakeModelProvider):
        def execute(self, task):
            entered.set()
            assert release.wait(timeout=15), "Synthetic provider barrier was not released"
            return super().execute(task)

    fixtures = []
    if fault == "TIMEOUT":
        fixtures = [TimeoutError("CANARY synthetic provider diagnostic")]
    elif fault == "UNAVAILABLE":
        fixtures = [RuntimeError("CANARY synthetic provider diagnostic")]
    gateway = StalledProvider(fixtures)
    processor = ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    )

    def read(index):
        if index % 3 == 0:
            response = client.get(pending["poll_url"], headers=actors["learner"])
            assert response.status_code == 200
            assert response.json() == pending
        elif index % 3 == 1:
            response = client.get(
                "/api/v1/me/progress",
                headers=actors["learner"],
                params={"subject_id": plan["subject_id"]},
            )
            assert response.status_code == 200
            assert response.json()["subject"]["evidence_count"] == 0
        else:
            response = client.get(
                "/api/v1/me/session-history",
                headers=actors["learner"],
                params={"subject_id": plan["subject_id"]},
            )
            assert response.status_code == 200
            assert len(response.json()["data"]) == 1
            assert response.json()["data"][0]["answered_count"] == 1
        assert "CANARY" not in response.text

    with ThreadPoolExecutor(max_workers=1) as workers:
        processing = workers.submit(processor.process_one)
        readers = ThreadPoolExecutor(max_workers=50)
        try:
            assert entered.wait(timeout=3)
            requests = [readers.submit(read, index) for index in range(50)]
            _, blocked = wait(requests, timeout=8)
            # This is a deadlock guard, not a 500-ms latency or scale acceptance claim.
            assert not blocked, "Web reads waited for a stalled fake provider"
            for request in requests:
                request.result()
            assert not release.is_set() and not processing.done()
            with Session(identity.engine) as db:
                assert db.get(GradingWorkRow, UUID(pending["attempt_id"])).status == "RUNNING"
                assert db.get(Grade, UUID(pending["attempt_id"])) is None
        finally:
            release.set()
            readers.shutdown(wait=True, cancel_futures=True)
        assert processing.result(timeout=5)

    assert len(gateway.calls) == 1
    neutral = client.get(pending["poll_url"], headers=actors["learner"])
    assert neutral.status_code == 200 and neutral.json()["status"] == "LOW_CONFIDENCE"
    assert "score" not in neutral.json() and "points_awarded" not in neutral.text
    assert save_short(short_text, session, item, key).json() == neutral.json()
    assert not processor.process_one() and len(gateway.calls) == 1
    assert "CANARY" not in neutral.text and "CANARY" not in caplog.text
    with Session(identity.engine) as db:
        assert db.get(GradingWorkRow, UUID(pending["attempt_id"])).status == "LOW_CONFIDENCE"
        assert db.get(Grade, UUID(pending["attempt_id"])) is None
        for model in (MasteryEvidence, GradingPublication, GradingAuditAssignment):
            assert db.scalar(select(func.count()).select_from(model)) == 0
