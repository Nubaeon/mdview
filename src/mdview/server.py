"""Live reload server for mdview.

Serves rendered HTML over HTTP with Server-Sent Events (SSE) for
automatic browser reload when the source markdown changes.

Usage:
    from mdview.server import serve
    serve("SPEC.md", port=8080)

Architecture:
    - HTTP server: stdlib http.server on a single thread
    - File watcher: mtime polling in a background thread (0.5s interval)
    - Reload push: SSE endpoint at /__events (no WebSocket needed)
    - Zero dependencies beyond stdlib + mdview's own renderer
"""

from __future__ import annotations

import logging
import queue
import signal
import sys
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from .renderer import render_html

logger = logging.getLogger(__name__)

# SSE clients waiting for reload events
_sse_clients: list[queue.Queue[str]] = []
_sse_lock = threading.Lock()

# Current rendered HTML (updated by watcher thread)
_current_html: str = ""
_html_lock = threading.Lock()


def _broadcast_reload() -> None:
    """Notify all connected SSE clients to reload."""
    with _sse_lock:
        dead: list[queue.Queue[str]] = []
        for q in _sse_clients:
            try:
                q.put_nowait("reload")
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)


def _render_and_store(filepath: Path, diagram_service: str | None) -> str:
    """Render markdown to HTML and store for serving."""
    global _current_html
    html = render_html(filepath, diagram_service=diagram_service)
    # Inject SSE live-reload client script before </body>
    html = _inject_sse_client(html)
    with _html_lock:
        _current_html = html
    return html


def _inject_sse_client(html: str) -> str:
    """Inject SSE client JavaScript for live reload."""
    sse_script = """
<script>
// mdview live reload via SSE
(function() {
  var es = new EventSource('/__events');
  es.onmessage = function(e) {
    if (e.data === 'reload') {
      window.location.reload();
    }
  };
  es.onerror = function() {
    // Reconnect on error (server restart, etc.)
    setTimeout(function() {
      es.close();
      var retry = new EventSource('/__events');
      retry.onmessage = es.onmessage;
      retry.onerror = es.onerror;
    }, 2000);
  };
  // Visual indicator
  var dot = document.createElement('div');
  dot.style.cssText = 'position:fixed;bottom:8px;right:8px;width:8px;height:8px;' +
    'border-radius:50%;background:#9ece6a;opacity:0.6;z-index:9999;' +
    'transition:opacity 0.3s;';
  dot.title = 'mdview live reload active';
  document.body.appendChild(dot);
  es.onopen = function() { dot.style.background = '#9ece6a'; dot.style.opacity = '0.6'; };
  es.onerror = function() { dot.style.background = '#f7768e'; dot.style.opacity = '0.8'; };
})();
</script>"""
    return html.replace("</body>", sse_script + "\n</body>")


class _RequestHandler(BaseHTTPRequestHandler):
    """HTTP handler: serves rendered HTML and SSE events."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default access logs, use our logger."""
        logger.debug(format, *args)

    def do_GET(self) -> None:
        if self.path == "/__events":
            self._handle_sse()
        elif self.path == "/" or self.path.endswith(".html"):
            self._serve_html()
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_html(self) -> None:
        """Serve the current rendered HTML."""
        with _html_lock:
            body = _current_html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _handle_sse(self) -> None:
        """Server-Sent Events endpoint for live reload."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        client_queue: queue.Queue[str] = queue.Queue(maxsize=10)
        with _sse_lock:
            _sse_clients.append(client_queue)

        try:
            # Send initial connected event
            self.wfile.write(b"data: connected\n\n")
            self.wfile.flush()

            while True:
                try:
                    msg = client_queue.get(timeout=30)
                    self.wfile.write(f"data: {msg}\n\n".encode())
                    self.wfile.flush()
                except queue.Empty:
                    # Keep-alive ping
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with _sse_lock:
                if client_queue in _sse_clients:
                    _sse_clients.remove(client_queue)


class _ThreadedHTTPServer(HTTPServer):
    """HTTPServer that handles each request in a new thread."""
    daemon_threads = True
    allow_reuse_address = True

    def process_request(self, request, client_address):  # type: ignore[override]
        """Start a new thread for each request (needed for SSE)."""
        t = threading.Thread(
            target=self.process_request_thread,
            args=(request, client_address),
            daemon=True,
        )
        t.start()

    def process_request_thread(self, request, client_address):  # type: ignore[override]
        """Process request in thread, handle errors."""
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)


def _watch_file(
    filepath: Path,
    diagram_service: str | None,
    poll_interval: float = 0.5,
) -> None:
    """Watch a file for changes and trigger re-render + reload."""
    last_mtime = filepath.stat().st_mtime

    while True:
        time.sleep(poll_interval)
        try:
            mtime = filepath.stat().st_mtime
            if mtime != last_mtime:
                last_mtime = mtime
                logger.info(f"File changed: {filepath.name} — re-rendering")
                try:
                    _render_and_store(filepath, diagram_service)
                    _broadcast_reload()
                    logger.info("Reload sent to browser")
                except Exception as e:
                    logger.warning(f"Re-render failed: {e}")
        except FileNotFoundError:
            logger.warning(f"File disappeared: {filepath}")
            time.sleep(2)


def serve(
    filepath: str | Path,
    *,
    port: int = 8090,
    open_browser: bool = True,
    diagram_service: str | None = None,
    poll_interval: float = 0.5,
) -> None:
    """Start live reload server for a markdown file.

    Args:
        filepath: Path to markdown file.
        port: HTTP port (default 8090).
        open_browser: Auto-open browser on start.
        diagram_service: Override diagram rendering service URL.
        poll_interval: File poll interval in seconds.
    """
    filepath = Path(filepath).resolve()
    if not filepath.exists():
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(1)

    # Initial render
    print(f"Rendering {filepath.name}...")
    _render_and_store(filepath, diagram_service)

    # Start file watcher
    watcher = threading.Thread(
        target=_watch_file,
        args=(filepath, diagram_service, poll_interval),
        daemon=True,
    )
    watcher.start()

    # Start HTTP server
    server = _ThreadedHTTPServer(("127.0.0.1", port), _RequestHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"Serving {filepath.name} at {url}")
    print(f"Watching for changes (poll: {poll_interval}s)")
    print("Press Ctrl+C to stop")

    if open_browser:
        webbrowser.open(url)

    # Handle Ctrl+C gracefully
    def _shutdown(sig, frame):
        print("\nShutting down...")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
