"""Production launcher for the Flask app using Waitress.

This avoids the previous issue where Waitress was started inside a daemon
thread (causing the process to exit as soon as the main script finished).
Run with:
    python serve.py
Or set PORT env var (default 5000):
    $env:PORT=5099; python serve.py  (PowerShell)
"""
from __future__ import annotations

import os
import logging
from waitress import serve

# Import the Flask application instance
from app import app  # noqa: E402

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


def main() -> None:
    port = int(os.environ.get('PORT', '5000'))
    listen = f"0.0.0.0:{port}"
    logging.info("Starting Waitress on %s", listen)
    try:
        serve(app, listen=listen)
    except Exception:  # pragma: no cover
        logging.exception("Fatal error while running Waitress server")
        raise


if __name__ == '__main__':
    main()
