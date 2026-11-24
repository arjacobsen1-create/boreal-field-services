"""Boreal Field Services - serve the Python dashboard.

    python3 -m app.serve            (from the repository root)
    python3 serve.py                 (from inside app/)

Then open http://localhost:8000. Standard library only.

Routes:
  GET  /           the dashboard, rendered from the current state
  POST /step       advance the morning one step
  POST /approve-b  put the verified Station B transfer to the gate
  POST /approve-c  put the unverified Station C transfer to the gate
  POST /reset      restart the morning
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from .dashboard import render
    from .simulation import Morning
except ImportError:  # running as loose scripts inside the folder
    from dashboard import render
    from simulation import Morning

MORNING = Morning()


class Handler(BaseHTTPRequestHandler):
    def _page(self) -> None:
        body = render(MORNING).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self) -> None:
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        if self.path == "/":
            self._page()
        else:
            self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802 (stdlib naming)
        if self.path == "/step":
            MORNING.advance()
        elif self.path == "/approve-b":
            MORNING.approve("Station B")
        elif self.path == "/approve-c":
            MORNING.approve("Station C")
        elif self.path == "/reset":
            MORNING.reset()
        else:
            self.send_error(404)
            return
        self._redirect()

    def log_message(self, *args) -> None:  # keep the console quiet
        pass


def main(port: int = 8000) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Boreal Field Services dashboard at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
