import multiprocessing
import os

# Basic Gunicorn configuration for Tourist Safety System
# Adjust workers based on CPU cores (2-4 * cores is typical for sync workers)
workers = int(os.environ.get("GUNICORN_WORKERS", (multiprocessing.cpu_count() * 2) + 1))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:5000")
backlog = int(os.environ.get("GUNICORN_BACKLOG", "2048"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# App reference
wsgi_app = os.environ.get("GUNICORN_WSGI_APP", "wsgi:app")

# Security / proxy adjustments
forwarded_allow_ips = "*"
proxy_allow_ips = "*"

# Timeout (increase if heavy startup)
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))

# Graceful reload in containers (can be disabled in prod for perf)
reload = os.environ.get("GUNICORN_RELOAD", "false").lower() == "true"

# Limit request size (bytes). Adjust if you expect large uploads.
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Hooks (optional debug; currently no-op)
from typing import Any

def post_fork(server: Any, worker: Any) -> None:  # pragma: no cover
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server: Any, worker: Any) -> None:  # pragma: no cover
    pass

def when_ready(server: Any) -> None:  # pragma: no cover
    server.log.info("Gunicorn server is ready.")
