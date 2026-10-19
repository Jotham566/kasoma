"""NFR-REL-002/SEC-002: isolated resource authority and bounded private backups."""

import json
import stat
import subprocess
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pydantic import SecretStr

from scripts.object_recovery_drill import backup_objects, drill, restore_objects, verify_faults
from scripts.recovery_containers import LABEL, OwnedServices, image_id, invocation_id
from services.export_artifacts import MAX_CIPHERTEXT_BYTES, ArtifactError

INVOCATION = "a" * 32
CID = "b" * 64
IMAGE = "sha256:" + "c" * 64


def inspection(*, cid=CID, label=INVOCATION, mounts=None, address="127.0.0.1", port="55433"):
    return json.dumps(
        [
            {
                "Id": cid,
                "Config": {"Labels": {LABEL: label}},
                "Mounts": mounts or [],
                "NetworkSettings": {"Ports": {"5432/tcp": [{"HostIp": address, "HostPort": port}]}},
                "State": {"Running": False},
            }
        ]
    )


@pytest.mark.parametrize(
    "value",
    ["postgres", "latest", "sha256:" + "a" * 63, "sha256:" + "A" * 64, "sha256:" + "a" * 64 + ";"],
)
def test_only_immutable_canonical_images(value):
    with pytest.raises(ValueError, match="IMAGE_INVALID"):
        image_id(value)
    assert image_id(IMAGE) == IMAGE


@pytest.mark.parametrize("value", ["", "a" * 31, "a" * 33, "A" * 32, "../" + "a" * 29])
def test_only_generated_invocations(value):
    with pytest.raises(ValueError, match="INVOCATION_INVALID"):
        invocation_id(value)


@pytest.mark.parametrize(
    "url,environment",
    [
        ("postgresql+psycopg://kasoma:secret@remote.invalid:55432/kasoma", "development"),
        ("postgresql+psycopg://kasoma:secret@localhost:5432/kasoma", "development"),
        ("postgresql+psycopg://kasoma:secret@localhost:55432/kasoma?options=unsafe", "development"),
        ("postgresql+psycopg://kasoma:secret@localhost:55432/kasoma", "production"),
    ],
)
def test_unsafe_profiles_never_resolve_images_or_create_services(
    settings, monkeypatch, url, environment
):
    tool = Mock(side_effect=AssertionError("must not run"))
    monkeypatch.setattr("scripts.object_recovery_drill.compose_image", tool)
    with pytest.raises(ValueError, match="standard local"):
        drill(settings.model_copy(update={"app_env": environment, "database_url": SecretStr(url)}))
    tool.assert_not_called()


def test_create_uses_immutable_image_private_environment_loopback_and_bounded_tmpfs(monkeypatch):
    calls = []

    def run(args, *, environment=None):
        calls.append((args, environment))
        return CID if args[1] == "create" else CID

    monkeypatch.setattr("scripts.recovery_containers.command", run)
    services = OwnedServices(INVOCATION)
    env = {
        "POSTGRES_USER": "kasoma",
        "POSTGRES_PASSWORD": "CANARY-private",
        "POSTGRES_DB": "generated",
    }
    services.create("source-db", IMAGE, env)
    args, passed = calls[0]
    assert passed == env and "CANARY-private" not in str(args)
    assert args[args.index("--publish") + 1] == "127.0.0.1::5432"
    assert args[args.index("--tmpfs") + 1] == "/var/lib/postgresql/data:rw,size=256m"
    assert "--pull=never" in args and args[-1] == IMAGE
    assert "--volume" not in args and "--mount" not in args
    assert services.created == {"source-db": CID} and not services.uncertain


@pytest.mark.parametrize(
    "part,environment",
    [
        ("postgres", {}),
        ("source-db", {"POSTGRES_PASSWORD": "x"}),
        ("source-objects", {"MINIO_ROOT_USER": "x", "MINIO_ROOT_PASSWORD": ""}),
    ],
)
def test_bad_creation_contract_never_calls_docker(monkeypatch, part, environment):
    tool = Mock()
    monkeypatch.setattr("scripts.recovery_containers.command", tool)
    with pytest.raises(ValueError):
        OwnedServices(INVOCATION).create(part, IMAGE, environment)
    tool.assert_not_called()


@pytest.mark.parametrize(
    "value",
    [
        inspection(cid="d" * 64),
        inspection(label="d" * 32),
        inspection(mounts=[{"Type": "volume", "Name": "developer"}]),
        inspection(mounts=[{"Type": "bind", "Source": "/private"}]),
        "[]",
    ],
)
def test_cleanup_requires_exact_created_id_label_and_no_persistent_mounts(monkeypatch, value):
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        return value

    monkeypatch.setattr("scripts.recovery_containers.command", run)
    services = OwnedServices(INVOCATION, {"source-db": CID})
    assert services.cleanup() == [f"kasoma-recovery-source-db-{INVOCATION}"]
    assert calls == [["docker", "inspect", CID]]


def test_partial_start_failure_preserves_returned_creation_authority(monkeypatch):
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        if args[1] == "create":
            return CID
        if args[1] == "start":
            raise RuntimeError("CANARY-private")
        return inspection()

    monkeypatch.setattr("scripts.recovery_containers.command", run)
    services = OwnedServices(INVOCATION)
    with pytest.raises(RuntimeError):
        services.create(
            "source-db",
            IMAGE,
            {"POSTGRES_USER": "kasoma", "POSTGRES_PASSWORD": "secret", "POSTGRES_DB": "generated"},
        )
    assert services.cleanup() == []
    assert calls[-1] == ["docker", "rm", "--force", CID]


def test_unknown_creation_reports_but_never_adopts_generated_name(monkeypatch):
    tool = Mock(return_value="truncated-id")
    monkeypatch.setattr("scripts.recovery_containers.command", tool)
    services = OwnedServices(INVOCATION)
    with pytest.raises(ValueError, match="CREATION_ID_UNAVAILABLE"):
        services.create(
            "source-objects",
            IMAGE,
            {"MINIO_ROOT_USER": "synthetic", "MINIO_ROOT_PASSWORD": "secret"},
        )
    assert services.created == {}
    assert services.cleanup() == [f"kasoma-recovery-source-objects-{INVOCATION}"]
    assert tool.call_count == 1


@pytest.mark.parametrize(
    "address,port",
    [
        ("0.0.0.0", "55433"),
        ("::", "55433"),
        ("127.0.0.1", "80"),
        ("127.0.0.1", "65536"),
        ("127.0.0.1", "bad"),
    ],
)
def test_only_bound_random_loopback_ports_are_used(monkeypatch, address, port):
    monkeypatch.setattr(
        "scripts.recovery_containers.command",
        lambda *a, **k: inspection(address=address, port=port),
    )
    with pytest.raises(ValueError):
        OwnedServices(INVOCATION, {"source-db": CID}).port("source-db")


def test_valid_port_and_owned_stop_verified(monkeypatch):
    tool = Mock(return_value=inspection())
    monkeypatch.setattr("scripts.recovery_containers.command", tool)
    services = OwnedServices(INVOCATION, {"source-db": CID})
    assert services.port("source-db") == 55433
    services.stop("source-db")
    assert ["docker", "stop", "--time", "10", CID] in [call.args[0] for call in tool.call_args_list]


def test_ciphertext_backup_is_private_bounded_and_read_without_source(tmp_path):
    source, destination = Mock(), Mock()
    generation, first, second = uuid4(), uuid4(), uuid4()
    raw = b"synthetic-authenticated-ciphertext"
    source.get.return_value = raw
    destination.get.return_value = raw
    refs = backup_objects(source, generation, (first, second), tmp_path)
    for target in (first, second):
        assert stat.S_IMODE((tmp_path / str(target)).stat().st_mode) == 0o600
    source.get.side_effect = AssertionError("source must be offline")
    assert restore_objects(destination, generation, refs, tmp_path) == len(raw) * 2
    assert destination.put.call_count == 2


@pytest.mark.parametrize("raw", [b"", b"x" * (MAX_CIPHERTEXT_BYTES + 1), "not-bytes"])
def test_oversized_or_invalid_source_never_writes_backup(tmp_path, raw):
    source = Mock()
    source.get.return_value = raw
    with pytest.raises(ValueError, match="OBJECT_SIZE_INVALID"):
        backup_objects(source, uuid4(), (uuid4(),), tmp_path)
    assert not list(tmp_path.iterdir())


def test_backup_inventory_bounds_and_duplicate_refs(tmp_path):
    source = Mock()
    target = uuid4()
    for refs in ((), (target, target), tuple(uuid4() for _ in range(257))):
        with pytest.raises(ValueError, match="INVENTORY_INVALID"):
            backup_objects(source, uuid4(), refs, tmp_path)
    source.get.assert_not_called()


@pytest.mark.parametrize("raw", [b"", b"too-long", b"x" * (MAX_CIPHERTEXT_BYTES + 1)])
def test_changed_backup_length_never_reaches_storage(tmp_path, raw):
    target, storage = uuid4(), Mock()
    (tmp_path / str(target)).write_bytes(raw)
    with pytest.raises(ValueError, match="OBJECT_SIZE_INVALID"):
        restore_objects(storage, uuid4(), ((target, 1),), tmp_path)
    storage.put.assert_not_called()


def test_restore_verifies_acknowledged_bytes(tmp_path):
    target, storage = uuid4(), Mock()
    (tmp_path / str(target)).write_bytes(b"x")
    storage.get.return_value = b"y"
    with pytest.raises(ValueError, match="COPY_MISMATCH"):
        restore_objects(storage, uuid4(), ((target, 1),), tmp_path)


def test_missing_corrupt_probe_restores_original_after_each_rejection():
    storage, state, identity = Mock(), Mock(), Mock()
    storage.get.return_value = b"ciphertext"
    state.storage = storage
    state.verify.side_effect = [
        ArtifactError("EXPORT_ARTIFACT_READ_FAILED"),
        None,
        ArtifactError("EXPORT_ARTIFACT_READ_FAILED"),
        None,
    ]
    generation, target = uuid4(), uuid4()
    verify_faults(identity, state, generation, target)
    assert state.verify.call_count == 4
    assert storage.put.call_args.args == (generation, target, b"ciphertext")


def test_fault_probe_rejects_false_positive_and_restores_owned_object():
    state, identity = Mock(), Mock()
    state.storage.get.return_value = b"ciphertext"
    with pytest.raises(ValueError, match="CORRUPT_OBJECT_ACCEPTED"):
        verify_faults(identity, state, uuid4(), uuid4())
    assert state.storage.put.call_args.args[-1] == b"ciphertext"


def test_failed_partial_resource_creation_is_minimized_and_cleaned(settings, monkeypatch):
    services = Mock()
    services.invocation = INVOCATION
    services.create.side_effect = subprocess.CalledProcessError(
        1, ["docker"], output="CANARY-private"
    )
    services.cleanup.return_value = []
    monkeypatch.setattr("scripts.object_recovery_drill.OwnedServices", lambda *a: services)
    monkeypatch.setattr("scripts.object_recovery_drill.compose_image", lambda *a: IMAGE)
    result = drill(
        settings.model_copy(
            update={
                "app_env": "development",
                "database_url": SecretStr(
                    "postgresql+psycopg://kasoma:synthetic@localhost:55432/kasoma"
                ),
            }
        )
    )
    assert result == {
        "status": "FAILED",
        "profile": "isolated-synthetic-db-objects-v1",
        "failed_stage": "CREATE_OWNED_SERVICES",
        "cleanup_failed": [],
    }
    services.cleanup.assert_called_once()
    assert "CANARY" not in str(result)


def test_resolve_approved_configured_image_to_local_immutable_id(monkeypatch):
    from scripts.recovery_containers import compose_image

    tool = Mock(
        side_effect=[
            json.dumps({"services": {"minio": {"image": "kasoma-minio:2025-09-07-source"}}}),
            IMAGE,
        ]
    )
    monkeypatch.setattr("scripts.recovery_containers.command", tool)
    assert compose_image("minio") == IMAGE
    assert tool.call_args.args[0] == [
        "docker",
        "image",
        "inspect",
        "--format",
        "{{.Id}}",
        "kasoma-minio:2025-09-07-source",
    ]


def test_changed_image_config_refused_before_inspection_or_pull(monkeypatch):
    from scripts.recovery_containers import compose_image

    tool = Mock(return_value=json.dumps({"services": {"minio": {"image": "unapproved:latest"}}}))
    monkeypatch.setattr("scripts.recovery_containers.command", tool)
    with pytest.raises(ValueError, match="IMAGE_UNAVAILABLE"):
        compose_image("minio")
    assert tool.call_count == 1


def test_fixture_log_suppression_restores_process_state_after_failure(caplog):
    from scripts.object_recovery_drill import quiet_fixture_events
    from services.observability import logger

    previous = logger.disabled
    with pytest.raises(RuntimeError):
        with quiet_fixture_events():
            logger.info("CANARY-fixture-event")
            raise RuntimeError("synthetic")
    assert logger.disabled == previous and "CANARY" not in caplog.text


@pytest.mark.parametrize(
    "name", ["kasoma", "kasoma_drill_src_" + "a" * 31, "kasoma_drill_dst_" + "a" * 32]
)
def test_same_database_preservation_verifier_rejects_unsafe_expected_name(monkeypatch, name):
    from scripts.recovery_channel_preservation import verify_preservation

    tool = Mock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr("scripts.recovery_channel_preservation.Session", tool)
    with pytest.raises(ValueError, match="Exact generated"):
        verify_preservation(Mock(), expected_source_database=name)
    tool.assert_not_called()


def test_same_database_preservation_verifier_checks_exact_actual_name(monkeypatch):
    from unittest.mock import MagicMock

    from scripts.recovery_channel_preservation import verify_preservation

    session = MagicMock()
    session.return_value.__enter__.return_value.scalar.return_value = "kasoma_drill_src_" + "b" * 32
    monkeypatch.setattr("scripts.recovery_channel_preservation.Session", session)
    with pytest.raises(ValueError, match="identity mismatch"):
        verify_preservation(Mock(), expected_source_database="kasoma_drill_src_" + "a" * 32)
    assert session.return_value.__enter__.return_value.scalar.call_count == 1


def test_object_readiness_retries_transport_and_nonready_without_busy_loop(monkeypatch):
    from unittest.mock import MagicMock

    import httpx

    from scripts.object_recovery_drill import wait_objects

    client = MagicMock()
    client.__enter__.return_value.get.side_effect = [
        httpx.ConnectError("CANARY-private"),
        Mock(status_code=503),
        Mock(status_code=200),
    ]
    monkeypatch.setattr("scripts.object_recovery_drill.httpx.Client", lambda **kwargs: client)
    pause = Mock()
    monkeypatch.setattr("scripts.object_recovery_drill.sleep", pause)
    wait_objects(55433)
    assert pause.call_count == 2
    assert client.__enter__.return_value.get.call_args.args == (
        "http://127.0.0.1:55433/minio/health/live",
    )


def test_stop_is_not_accepted_while_owned_source_still_runs(monkeypatch):
    data = json.loads(inspection())
    data[0]["State"]["Running"] = True
    monkeypatch.setattr("scripts.recovery_containers.command", lambda *a, **k: json.dumps(data))
    with pytest.raises(ValueError, match="SOURCE_STILL_RUNNING"):
        OwnedServices(INVOCATION, {"source-db": CID}).stop("source-db")


def test_generated_runtime_keys_and_flags_do_not_inherit_active_features(settings):
    from scripts.object_recovery_drill import fresh_settings

    source = settings.model_copy(
        update={
            "short_text_enabled": True,
            "channel_preservation_enabled": True,
            "export_retirement_enabled": True,
            "otp_observation_enabled": True,
        }
    )
    first = fresh_settings(
        source,
        "kasoma_drill_src_" + INVOCATION,
        "generated-password",
        "generated-access",
        "generated-secret",
    )
    second = fresh_settings(
        source,
        "kasoma_drill_src_" + INVOCATION,
        "generated-password",
        "generated-access",
        "generated-secret",
    )
    assert first.identity_encryption_key != source.identity_encryption_key
    assert first.identity_lookup_key != source.identity_lookup_key
    assert first.identity_encryption_key != second.identity_encryption_key
    assert first.jwt_signing_key != source.jwt_signing_key
    assert not any(
        (
            first.short_text_enabled,
            first.channel_preservation_enabled,
            first.export_retirement_enabled,
            first.otp_observation_enabled,
        )
    )
    assert first.model_provider == first.email_provider == first.sms_provider == "fake"
    assert first.whatsapp_app_secret != source.whatsapp_app_secret


@pytest.mark.parametrize(
    "diagnostic,expected",
    [
        ("No such image CANARY-private", "IMAGE_UNAVAILABLE"),
        ("The container name CANARY-private is in use", "NAME_CONFLICT"),
        ("no space left on device CANARY-private", "STORAGE_FULL"),
        ("Cannot connect to the Docker daemon CANARY-private", "DOCKER_UNAVAILABLE"),
        ("unknown CANARY-private", "COMMAND_FAILED"),
    ],
)
def test_command_diagnostics_are_closed_and_never_echoed(monkeypatch, capsys, diagnostic, expected):
    from scripts.recovery_containers import RecoveryCommandError, command

    tool = Mock(side_effect=subprocess.CalledProcessError(1, ["docker"], stderr=diagnostic))
    monkeypatch.setattr("scripts.recovery_containers.subprocess.run", tool)
    with pytest.raises(RecoveryCommandError) as error:
        command(["docker", "create"], environment={"MINIO_ROOT_PASSWORD": "CANARY-secret"})
    assert error.value.kind == str(error.value) == expected
    assert "CANARY" not in str(error.value)
    assert not any(capsys.readouterr())
    assert "CANARY" not in str(tool.call_args.args)
    assert tool.call_args.kwargs["env"]["MINIO_ROOT_PASSWORD"] == "CANARY-secret"


def test_command_timeout_is_closed_without_adopting_resources(monkeypatch):
    from scripts.recovery_containers import RecoveryCommandError, command

    monkeypatch.setattr(
        "scripts.recovery_containers.subprocess.run",
        Mock(side_effect=subprocess.TimeoutExpired(["docker"], 60, stderr=b"CANARY-private")),
    )
    with pytest.raises(RecoveryCommandError, match="^TIMEOUT$"):
        command(["docker", "create"])
