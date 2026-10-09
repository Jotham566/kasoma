"""Owned, loopback-only native Firefox test sessions; never a personal profile."""

import json
import shutil
import socket
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Wire:
    def __init__(self, connection: socket.socket) -> None:
        self.connection = connection
        self.sequence = 0

    def read(self):
        prefix = bytearray()
        while True:
            byte = self.connection.recv(1)
            if byte == b":":
                break
            if not byte or not byte.isdigit() or len(prefix) >= 8:
                raise RuntimeError("Invalid local browser protocol frame")
            prefix.extend(byte)
        if not prefix:
            raise RuntimeError("Invalid local browser protocol frame")
        size = int(prefix)
        if not 0 < size <= 1048576:
            raise RuntimeError("Oversized local browser protocol frame")
        body = bytearray()
        while len(body) < size:
            part = self.connection.recv(size - len(body))
            if not part:
                raise RuntimeError("Local browser protocol closed")
            body.extend(part)
        return json.loads(body)

    def command(self, command: str, parameters: dict, *, dismiss_alert: bool = True):
        self.sequence += 1
        payload = json.dumps([0, self.sequence, command, parameters]).encode()
        self.connection.sendall(str(len(payload)).encode() + b":" + payload)
        response = self.read()
        if (
            not isinstance(response, list)
            or len(response) != 4
            or response[:2] != [1, self.sequence]
        ):
            raise RuntimeError("Invalid local browser response")
        if response[2] is not None:
            category = response[2].get("error") if isinstance(response[2], dict) else None
            if (
                category == "unexpected alert open"
                and command == "WebDriver:ExecuteAsyncScript"
                and dismiss_alert
            ):
                # The session dismisses native failure dialogs; Gecko may still notify
                # the interrupted command. Retry that observation once, never indefinitely.
                return self.command(command, parameters, dismiss_alert=False)
            if category not in {
                "javascript error",
                "script timeout",
                "invalid session id",
                "unexpected alert open",
                "no such window",
                "no such frame",
                "invalid argument",
                "unknown error",
                "unsupported operation",
            }:
                category = "protocol error"
            raise RuntimeError(f"Local browser command failed: {command} ({category})")
        return response[3]

    def downloads(self, suffix: str, cancel: bool = False, count: int = 1):
        self.command("Marionette:SetContext", {"value": "chrome"})
        result = self.command(
            "WebDriver:ExecuteAsyncScript",
            {
                "script": """
                const done = arguments[arguments.length - 1];
                (async () => {
                  const {Downloads} = ChromeUtils.importESModule(
                    'resource://gre/modules/Downloads.sys.mjs');
                  const list = await Downloads.getList(Downloads.ALL);
                  const items = (await list.getAll()).filter(
                    d => d.source.url.endsWith(arguments[0]));
                  if (items.length !== arguments[2]) return null;
                  const d = items[items.length - 1];
                  if (arguments[1]) await d.cancel();
                  return {stopped:d.stopped, succeeded:d.succeeded,
                    canceled:d.canceled, error:!!d.error, path:d.succeeded ? d.target.path : null};
                })().then(done, () => done({probeError:true}));
                """,
                "args": [suffix, cancel, count],
                "newSandbox": True,
                "sandbox": "default",
            },
        )
        return result.get("value")


@contextmanager
def native_browser():
    root = ROOT / ".local/browsers/firefox-1509/firefox"
    candidates = [
        p for p in [root / "firefox", root / "Nightly.app/Contents/MacOS/firefox"] if p.is_file()
    ]
    if len(candidates) != 1:
        raise RuntimeError("Install the pinned Firefox with make e2e-install")
    process = None
    profile = Path(tempfile.mkdtemp(prefix="kasoma-native-firefox-"))
    connection = None
    try:
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        preferences = {
            "marionette.port": port,
            "browser.shell.checkDefaultBrowser": False,
            "browser.startup.page": 0,
            "browser.download.folderList": 2,
            "browser.download.dir": str(profile),
            "browser.download.useDownloadDir": True,
            "browser.helperApps.neverAsk.saveToDisk": "application/json",
            "browser.download.always_ask_before_handling_new_types": False,
            "network.proxy.type": 1,
            "network.proxy.http": "127.0.0.1",
            "network.proxy.http_port": 9,
            "network.proxy.ssl": "127.0.0.1",
            "network.proxy.ssl_port": 9,
            "network.proxy.no_proxies_on": "127.0.0.1,localhost",
            "network.trr.mode": 5,
            "network.captive-portal-service.enabled": False,
            "network.connectivity-service.enabled": False,
            "datareporting.healthreport.uploadEnabled": False,
            "datareporting.policy.dataSubmissionEnabled": False,
            "toolkit.telemetry.enabled": False,
        }
        (profile / "user.js").write_text(
            "\n".join(
                f"user_pref({json.dumps(k)}, {json.dumps(v)});" for k, v in preferences.items()
            )
        )
        process = subprocess.Popen(
            [
                str(candidates[0]),
                "-headless",
                "-no-remote",
                "-profile",
                str(profile),
                "-marionette",
                "--remote-allow-system-access",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and process.poll() is None:
            try:
                connection = socket.create_connection(("127.0.0.1", port), timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        if connection is None:
            raise RuntimeError("Owned local Firefox did not start")
        connection.settimeout(15)
        wire = Wire(connection)
        if wire.read().get("applicationType") != "gecko":
            raise RuntimeError("Unexpected local browser protocol")
        session = wire.command(
            "WebDriver:NewSession",
            {"capabilities": {"alwaysMatch": {"unhandledPromptBehavior": "dismiss"}}},
        )
        if Path(session["capabilities"]["moz:profile"]).resolve() != profile.resolve():
            raise RuntimeError("Browser profile ownership mismatch")
        yield wire, profile
    finally:
        if connection is not None:
            connection.close()
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        shutil.rmtree(profile)
