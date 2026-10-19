"""ADR-066: fixture clocks/normal response boundaries; no performance claim from mocks."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest
from pydantic import SecretStr

from scripts import objective_load as load
from scripts import temporal_history as temporal
from services.assessment_contracts import DiagnosticReceipt, DiagnosticView, GradeView
from services.identity_contracts import Credentials

ANCHOR = datetime(2026, 10, 19, 12, tzinfo=UTC)


def scaffold(monkeypatch, *, bad_receipt=False, bad_completion=False, bad_grade=False):
    subjects = {"Mathematics": uuid4(), "Physics": uuid4()}
    events = defaultdict(list)
    original = SimpleNamespace(
        engine=object(),
        settings=object(),
        clock=lambda: ANCHOR,
        subjects=lambda: [SimpleNamespace(id=value, name=name) for name, value in subjects.items()],
    )

    def identity(engine, settings, email, sms, *, clock, code):
        owner = SimpleNamespace(engine=engine, settings=settings, clock=clock, code=code)
        events["owners"].append(owner)
        return owner

    monkeypatch.setattr(temporal, "IdentityService", identity)

    class Assessment:
        def __init__(self, owner):
            self.owner = owner
            self.diagnostics = SimpleNamespace(start=self.diagnostic)
            self.sessions = {}

        def diagnostic(self, token, body, key, request):
            target = uuid4()
            self.sessions[target] = "DIAGNOSTIC"
            events["diagnostics"].append((body.subject_id, self.owner.clock(), id(self.owner)))
            return SimpleNamespace(id=target)

        def topics(self, token, subject):
            return [
                SimpleNamespace(id=uuid4(), name=name)
                for name in ("Algebra", "Mechanics", "Electricity and Magnetism")
            ]

        def start(self, token, body, key, request):
            target = uuid4()
            self.sessions[target] = "REVISION"
            events["revisions"].append((body.subject_id, self.owner.clock(), id(self.owner)))
            return SimpleNamespace(id=target)

        def next_item(self, token, target, request):
            return SimpleNamespace(
                session_item_id=uuid4(), response_spec=SimpleNamespace(type="SINGLE_CHOICE")
            )

        def submit(self, token, target, body, key, request):
            kind = self.sessions[target]
            events["answers"].append((kind, self.owner.clock()))
            if kind == "DIAGNOSTIC":
                return (
                    Mock(spec=GradeView) if bad_receipt else DiagnosticReceipt(attempt_id=uuid4())
                )
            expected = int(body.response.choice_id == "A")
            return Mock(
                spec=GradeView,
                score=(1 - expected if bad_grade else expected),
                mastery_update_status="COMPLETED",
            )

        def get(self, token, target):
            return Mock(
                spec=DiagnosticView,
                status=("ACTIVE" if bad_completion else "COMPLETED"),
                answered_count=15,
                result=SimpleNamespace(skills=["synthetic"]),
            )

    monkeypatch.setattr(temporal, "AssessmentService", Assessment)

    def login(owner, index):
        if owner is original:
            events["current_auth_history_counts"].append(len(events["revisions"]))
        events[index].append((owner.clock(), id(owner)))
        return Credentials(
            access_token=f"synthetic-access-{index}-{len(events[index])}",
            refresh_token="synthetic-refresh",
        )

    return original, subjects, events, login


def test_independent_chronological_clocks_complete_diagnostics_and_reauthenticate_now(monkeypatch):
    identity, subjects, events, login = scaffold(monkeypatch)
    credentials = [Credentials(access_token="old", refresh_token="old") for _ in range(4)]
    tokens, plans = temporal.prepare(
        identity, credentials, ANCHOR, login, load.fixture_response, load.history_correct
    )
    assert len(events["diagnostics"]) == 4 and len(events["revisions"]) == 40
    assert len(events["answers"]) == 4 * 65
    assert len({owner for _, _, owner in events["diagnostics"]}) == 4
    for index in range(4):
        times = [at for at, _ in events[index]]
        assert times == [
            ANCHOR - timedelta(days=91),
            *[ANCHOR - timedelta(days=age) for age in temporal.REVISION_AGES],
            ANCHOR,
        ]
        assert events[index][-1][1] == id(identity)
        assert tokens[index] == credentials[index].access_token
        assert plans[index]["subject_id"] == str(
            subjects["Mathematics" if index % 2 == 0 else "Physics"]
        )
    assert identity.clock() == ANCHOR
    assert events["current_auth_history_counts"] == [40] * 4


@pytest.mark.parametrize(
    "bad,reason",
    [
        ("bad_receipt", "answer was not sealed"),
        ("bad_completion", "did not complete normally"),
        ("bad_grade", "did not match fixture"),
    ],
)
def test_invalid_domain_outcome_fails_without_fabricating_history(monkeypatch, bad, reason):
    identity, _, _, login = scaffold(monkeypatch, **{bad: True})
    with pytest.raises(ValueError, match=reason):
        temporal.prepare(
            identity,
            [Credentials(access_token="old", refresh_token="old")],
            ANCHOR,
            login,
            load.fixture_response,
            load.history_correct,
        )


@pytest.mark.parametrize("anchor,credentials", [(datetime(2026, 10, 19), [Mock()]), (ANCHOR, [])])
def test_invalid_fixture_boundary_refused_before_subject_query(anchor, credentials):
    identity = Mock()
    with pytest.raises(ValueError, match="aware anchor and learners"):
        temporal.prepare(identity, credentials, anchor, Mock(), Mock(), Mock())
    identity.subjects.assert_not_called()


def composition_session(
    monkeypatch, *, missing_age=False, diagnostic_count=30, owners=2, unexpected=False
):
    rows = [("REVISION", ANCHOR - timedelta(days=age), 10) for age in temporal.REVISION_AGES]
    if missing_age:
        rows.pop()
    rows.append(("DIAGNOSTIC", ANCHOR - timedelta(days=91), diagnostic_count))
    if unexpected:
        rows.append(("REVISION", ANCHOR + timedelta(days=1), 1))
    session = MagicMock()
    session.__enter__.return_value.execute.return_value = rows
    session.__enter__.return_value.scalar.side_effect = [2, owners]
    monkeypatch.setattr(temporal, "Session", lambda engine: session)
    return session


def test_composition_requires_all_ages_and_completed_unique_diagnostics(monkeypatch):
    composition_session(monkeypatch)
    result = temporal.composition(Mock(), ANCHOR, 2)
    assert result == {
        "history_diagnostic_sessions": 2,
        "history_diagnostic_answers": 30,
        "history_revision_age_counts": {str(age): 10 for age in temporal.REVISION_AGES},
        "history_diagnostic_age_days": 91,
    }
    assert sum(result["history_revision_age_counts"].values()) == 100


@pytest.mark.parametrize(
    "changed",
    [{"missing_age": True}, {"diagnostic_count": 29}, {"owners": 1}, {"unexpected": True}],
)
def test_incomplete_or_unexpected_composition_never_counts_as_acceptance(monkeypatch, changed):
    composition_session(monkeypatch, **changed)
    with pytest.raises(ValueError, match="Temporal"):
        temporal.composition(Mock(), ANCHOR, 2)


@pytest.mark.parametrize(
    "changed",
    [
        {"app_env": "production"},
        {
            "database_url": SecretStr(
                "postgresql+psycopg://kasoma:secret@remote.invalid:55432/kasoma"
            )
        },
        {
            "database_url": SecretStr(
                "postgresql+psycopg://kasoma:secret@localhost:55432/kasoma?options=unsafe"
            )
        },
    ],
)
def test_temporal_profile_inherits_refusal_before_any_resource(settings, monkeypatch, changed):
    source = settings.model_copy(
        update={
            "app_env": "development",
            "database_url": SecretStr("postgresql+psycopg://kasoma:secret@localhost:55432/kasoma"),
        }
    )
    connect = Mock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr(load, "create_engine", connect)
    with pytest.raises(ValueError):
        load.run(source.model_copy(update=changed), temporal_history=True)
    connect.assert_not_called()
