"""Run the PKL submission API with Python's standard library.

Usage:
    PKL_REVIEWER_TOKEN=... python -m pkl.server
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .api import SubmissionAPI
from .submissions import SubmissionStore


class PKLHandler(BaseHTTPRequestHandler):
    api: SubmissionAPI

    def _json(self, status: int, body: dict) -> None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", os.getenv("PKL_CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Contributor-ID")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if status != 204:
            self.wfile.write(encoded)

    def _token(self) -> str | None:
        value = self.headers.get("Authorization", "")
        if value.lower().startswith("bearer "):
            return value[7:].strip()
        return None

    def _payload(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("request body too large")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._json(204, {})

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        if path == "/api/public/submissions":
            self._json(*self.api.public_submissions())
            return
        if path == "/api/reviewer/submissions":
            self._json(*self.api.reviewer_queue(self._token()))
            return
        if path == "/api/reviewer/audit":
            self._json(*self.api.reviewer_audit(self._token()))
            return
        self._json(404, {"error": "not found", "code": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        try:
            payload = self._payload()
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc), "code": "invalid_json"})
            return

        if path == "/api/submissions":
            contributor = self.headers.get("X-Contributor-ID") or f"ip:{self.client_address[0]}"
            rate_limit_id = f"ip:{self.client_address[0]}"
            self._json(*self.api.submit(payload, contributor_id=contributor, rate_limit_id=rate_limit_id))
            return

        prefix = "/api/reviewer/submissions/"
        if path.startswith(prefix) and path.endswith("/decision"):
            submission_id = path[len(prefix):-len("/decision")].strip("/")
            if not submission_id:
                self._json(404, {"error": "submission not found", "code": "not_found"})
                return
            self._json(*self.api.moderate(submission_id, payload, self._token()))
            return

        self._json(404, {"error": "not found", "code": "not_found"})

    def log_message(self, format: str, *args: object) -> None:
        print("PKL API:", format % args)


def create_server(*, data_path: str | Path = "data/submissions.json", host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    store = SubmissionStore(data_path)
    api = SubmissionAPI(store, reviewer_token=os.getenv("PKL_REVIEWER_TOKEN"))
    handler = type("ConfiguredPKLHandler", (PKLHandler,), {"api": api})
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    server = create_server(host=os.getenv("PKL_API_HOST", "127.0.0.1"), port=int(os.getenv("PKL_API_PORT", "8787")))
    print(f"PKL API listening on http://{server.server_address[0]}:{server.server_address[1]}")
    server.serve_forever()


if __name__ == "__main__":
    main()
