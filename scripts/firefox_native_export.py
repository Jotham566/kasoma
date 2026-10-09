"""Real-gateway corruption/retry acceptance through Firefox's ordinary download manager."""

import hashlib
import json
import re
import signal
import sys
import time
from pathlib import Path
from uuid import UUID

import httpx

from scripts.firefox_native_browser import native_browser

STAGE = "INPUT"
ELEMENT = "element-6066-11e4-a52e-4f735466cecf"


def validate(payload):
    if not isinstance(payload, dict) or set(payload) != {"target", "cookies"}:
        raise ValueError("Invalid synthetic browser input")
    target, cookies = payload["target"], payload["cookies"]
    if not isinstance(target, str) or str(UUID(target)) != target:
        raise ValueError("Invalid synthetic target")
    if not isinstance(cookies, list) or not 1 <= len(cookies) <= 2:
        raise ValueError("Invalid synthetic cookies")
    names = set()
    for cookie in cookies:
        if (
            not isinstance(cookie, dict)
            or set(cookie) != {"name", "value"}
            or cookie["name"] not in {"kasoma_access", "kasoma_refresh"}
            or cookie["name"] in names
            or not isinstance(cookie["value"], str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,1024}", cookie["value"])
        ):
            raise ValueError("Invalid synthetic cookie")
        names.add(cookie["name"])
    if "kasoma_access" not in names:
        raise ValueError("Missing synthetic session")
    return target, cookies


def click(wire, xpath):
    wire.command("Marionette:SetContext", {"value": "content"})
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            element = wire.command("WebDriver:FindElement", {"using": "xpath", "value": xpath})[
                "value"
            ]
            break
        except RuntimeError:
            time.sleep(0.1)
    else:
        raise RuntimeError("Native export control unavailable")
    wire.command("WebDriver:ElementClick", {"id": element[ELEMENT]})


def wait_download(wire, suffix, count):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = wire.downloads(suffix, count=count)
        if state and state.get("stopped"):
            return state
        time.sleep(0.1)
    raise RuntimeError("Native export did not terminate")


def run(payload):
    global STAGE
    target, cookies = validate(payload)
    suffix = f"/api/v1/me/data-requests/{target}/export-file"
    fixture = f"http://127.0.0.1:18000/__fixture/exports/{target}"
    STAGE = "FIXTURE"
    with httpx.Client(trust_env=False, timeout=3, follow_redirects=False) as http:
        # Production images have no such fixture. The Playwright harness owns this port/schema.
        probe = http.get(fixture + "/observations")
        if probe.status_code != 200 or set(probe.json()) != {"reads", "closed"}:
            raise RuntimeError("Isolated synthetic fixture required")
        STAGE = "BROWSER"
        with native_browser() as (wire, profile):
            wire.command("WebDriver:Navigate", {"url": "http://127.0.0.1:13000/privacy"})
            STAGE = "COOKIES"
            for cookie in cookies:
                wire.command(
                    "WebDriver:AddCookie",
                    {"cookie": {**cookie, "path": "/", "httpOnly": True, "sameSite": "Strict"}},
                )
            wire.command("WebDriver:Navigate", {"url": "http://127.0.0.1:13000/privacy"})
            STAGE = "STATUS"
            click(wire, "//button[normalize-space()='Check background status']")
            selector = f"//a[@href='{suffix}']"
            STAGE = "CORRUPT"
            click(wire, selector)
            failed = wait_download(wire, suffix, 1)
            if failed["succeeded"] or not failed["error"] or failed["path"] is not None:
                raise RuntimeError("Corrupt native export was not rejected")
            observations = http.get(fixture + "/observations").json()
            if observations["reads"] < 2 or observations["closed"] < 1:
                raise RuntimeError("Corrupt native export reader was not closed")
            wire.command("Marionette:SetContext", {"value": "content"})
            status = wire.command(
                "WebDriver:ExecuteAsyncScript",
                {
                    "script": """
                const done = arguments[arguments.length - 1];
                fetch(arguments[0], {cache:'no-store'})
                  .then(r => r.ok ? r.json() : null)
                  .then(v => done(v?.status ?? null), () => done(null));
                """,
                    "args": [suffix.removesuffix("export-file") + "export-job"],
                },
            )
            if status.get("value") != "READY":
                raise RuntimeError("Native failure changed export job state")
            reset = http.post(fixture + "/fault/normal")
            if reset.status_code != 200 or reset.json() != {"configured": True}:
                raise RuntimeError("Synthetic fault reset failed")
            STAGE = "RETRY"
            click(wire, selector)
            complete = wait_download(wire, suffix, 2)
            if not complete["succeeded"] or complete["error"]:
                raise RuntimeError("Native frozen retry failed")
            STAGE = "ARTIFACT"
            saved = Path(complete["path"]).resolve()
            if (
                saved.parent != profile.resolve()
                or not 0 < saved.stat().st_size <= 16 * 1024 * 1024
            ):
                raise RuntimeError("Native saved artifact boundary failed")
            body = saved.read_bytes()
            if json.loads(body).get("request_id") != target:
                raise RuntimeError("Native artifact owner binding failed")
            return {
                "corrupt_rejected": True,
                "reader_closed": True,
                "size": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
            }


if __name__ == "__main__":

    def interrupted(_signum, _frame):
        raise RuntimeError("Native verification interrupted")

    signal.signal(signal.SIGTERM, interrupted)
    try:
        raw = sys.stdin.buffer.read(8193)
        if len(raw) > 8192:
            raise ValueError("Oversized synthetic browser input")
        print(json.dumps(run(json.loads(raw))))
    except Exception as error:
        # Never serialize credentials, provider errors or downloaded account contents.
        print(f"NATIVE_EXPORT_{STAGE}_{type(error).__name__}", file=sys.stderr)
        raise SystemExit(1) from None
