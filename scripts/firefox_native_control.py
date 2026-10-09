"""Raw HTTP diagnostic, separate from real-application native Firefox acceptance."""

import json
import select
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from scripts.firefox_native_browser import native_browser

BODY = b'{"synthetic":"' + b"x" * 196608 + b'"}'


def main() -> None:
    closed = {mode: threading.Event() for mode in ("healthy", "corrupt", "stall")}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args) -> None:
            pass

        def do_GET(self) -> None:
            mode = self.path.removeprefix("/file/")
            if mode not in closed:
                mode = self.path.removeprefix("/")
                if mode not in closed:
                    self.send_error(404)
                    return
                body = b'<a id="download" href="/file/' + mode.encode() + b'">Save</a>'
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(BODY)))
            self.send_header("Content-Disposition", f'attachment; filename="control-{mode}.json"')
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(BODY if mode == "healthy" else BODY[:65536])
            self.wfile.flush()
            if mode == "stall":
                readable, _, _ = select.select([self.connection], [], [], 10)
                if readable and self.connection.recv(1, socket.MSG_PEEK) == b"":
                    closed[mode].set()
            else:
                if mode == "corrupt":
                    self.connection.shutdown(socket.SHUT_RDWR)
                closed[mode].set()
            self.close_connection = True

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with native_browser() as (wire, profile):
            for mode in closed:
                wire.command("Marionette:SetContext", {"value": "content"})
                wire.command(
                    "WebDriver:Navigate", {"url": f"http://127.0.0.1:{server.server_port}/{mode}"}
                )
                wire.command(
                    "WebDriver:ExecuteScript",
                    {"script": "document.querySelector('#download').click();", "args": []},
                )
                deadline = time.monotonic() + 5
                state = None
                while time.monotonic() < deadline:
                    state = wire.downloads("/file/" + mode, cancel=mode == "stall")
                    if state and state.get("stopped"):
                        break
                    time.sleep(0.1)
                if not state or not state.get("stopped"):
                    raise RuntimeError(f"Native {mode} download did not terminate")
                if state["succeeded"] != (mode == "healthy"):
                    raise RuntimeError(f"Native {mode} download completion mismatch")
                if mode == "healthy" and (profile / "control-healthy.json").read_bytes() != BODY:
                    raise RuntimeError("Native download bytes mismatch")
                if not closed[mode].wait(5):
                    raise RuntimeError(f"Native {mode} connection did not close")
                print(json.dumps({"mode": mode, **state, "closed": True}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
