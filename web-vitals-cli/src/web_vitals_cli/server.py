import os
import time
import threading
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer


def find_free_port(start_port: int = 8000) -> int:
    """Find a free localhost port."""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
    raise RuntimeError("No free port found")


def serve_directory(directory: str, port: int) -> str:
    """Serve directory on port, return URL base."""
    os.chdir(directory)
    server = HTTPServer(("", port), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)  # Allow startup
    return f"http://localhost:{port}/"