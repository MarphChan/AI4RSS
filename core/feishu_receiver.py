import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from core.reading_list_manager import reading_list_manager


def _find_first_url_in_payload(payload: Any) -> str:
    try:
        text = json.dumps(payload, ensure_ascii=False)
    except Exception:
        text = str(payload)
    return reading_list_manager.extract_first_url(text)


class _FeishuHandler(BaseHTTPRequestHandler):
    receiver_token: str = ""

    def _send_json(self, status: int, body: Dict[str, Any]) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _token_ok(self) -> bool:
        if not self.receiver_token:
            return True
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query or "")
        token = (qs.get("token") or [""])[0]
        return token == self.receiver_token

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(200, {"ok": True})
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in ("/feishu", "/feishu/webhook"):
            self._send_json(404, {"ok": False, "error": "not_found"})
            return

        if not self._token_ok():
            self._send_json(401, {"ok": False, "error": "unauthorized"})
            return

        try:
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8", errors="ignore") or "{}")
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return

        url = _find_first_url_in_payload(payload)
        if not url:
            self._send_json(200, {"ok": True, "added": False, "reason": "no_url_found"})
            return

        reading_list_manager.add_url(
            url,
            source="feishu",
            default_status="unread",
            preserve_order_if_exists=False,
        )
        self._send_json(200, {"ok": True, "added": True, "url": url})

    def log_message(self, format: str, *args) -> None:
        return


class FeishuReceiverService:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, token: str = ""):
        self.host = host
        self.port = port
        self.token = token
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return

        handler_cls = type("_FeishuHandlerBound", (_FeishuHandler,), {})
        handler_cls.receiver_token = self.token or ""
        self._server = HTTPServer((self.host, int(self.port)), handler_cls)

        def _run() -> None:
            try:
                self._server.serve_forever()
            finally:
                try:
                    self._server.server_close()
                except Exception:
                    pass

        self._thread = threading.Thread(target=_run, name="FeishuReceiver", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server:
            try:
                self._server.shutdown()
            except Exception:
                pass
        self._server = None
        self._thread = None

