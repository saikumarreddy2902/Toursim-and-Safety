#!/usr/bin/env python3
from __future__ import annotations
"""Stable host launcher for the Tourist Safety System.

Why this file?
The Flask debug reloader caused restarts that appeared like crashes on Windows.
This script runs the existing `app` object under Waitress (a production‑ready,
pure‑Python WSGI server) to keep a single stable process. If Waitress isn't
installed it falls back to Flask's built‑in server (not for production).

Usage (run from project root: tourist-safety-system/):
    python host_app.py                # listen 127.0.0.1:5000
    python host_app.py --port 5050    # choose alternate port
    python host_app.py --prod         # force production env (disables debug)

Health check:
    http://127.0.0.1:5000/healthz  (change port if you used --port)

If unreachable:
    1. Allow Python through Windows Firewall (private network)
    2. Ensure the port is free (use: netstat -ano | findstr :5000)
    3. Try a different port with --port
    4. Install waitress if fallback used: pip install waitress
"""

import argparse
import os
import sys
import logging
import traceback
from pathlib import Path


def configure_paths() -> Path:
    """Add backend directory to sys.path so that `app` can be imported."""
    root = Path(__file__).parent.resolve()
    backend = root / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    return backend

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Host Tourist Safety System")
    p.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    p.add_argument("--port", type=int, default=5000, help="Port to listen on (default 5000)")
    p.add_argument("--prod", action="store_true", help="Force production mode (disables debug)")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    backend_dir = configure_paths()

    # Environment (avoid Flask reloader; we always run a single process)
    if args.prod:
        os.environ["FLASK_ENV"] = "production"
    else:
        os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("SECRET_KEY", "dev-secret-change-me-in-production")

    try:
        from app import app  # type: ignore
    except Exception as e:  # pragma: no cover - startup diagnostics
        print("[FATAL] Failed to import Flask app:", e)
        print("        Expecting backend/app.py defining 'app = Flask(...)'.")
        print(f"        Working directory: {Path.cwd()}")
        print(f"        Backend path tried: {backend_dir}")
        sys.exit(1)

    # Prefer Waitress (cross-platform). Fallback to Flask dev server if unavailable.
    # Basic logging so waitress internal messages show up
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    try:
        from waitress import serve  # type: ignore
        print("Starting Tourist Safety System (Waitress)")
        print(f" Project Root : {Path(__file__).parent}")
        print(f" Python       : {sys.executable}")
        print(f" URL          : http://{args.host}:{args.port}")
        print(" Mode         :", os.environ.get("FLASK_ENV"))
        print(" Press Ctrl+C to stop")
        print("[DIAG] Entering waitress.serve()")
        try:
            serve(app, listen=f"{args.host}:{args.port}")  # type: ignore
        except BaseException as e:  # pragma: no cover
            print("[FATAL] waitress.serve raised exception:", repr(e))
            traceback.print_exc()
            sys.exit(10)
        else:  # pragma: no cover
            print("[WARN] waitress.serve() returned unexpectedly (it should block). Exiting.")
            sys.exit(11)
    except ModuleNotFoundError:
        debug = not args.prod
        print("WARNING: Waitress not installed; falling back to Flask built-in server (dev only)")
        print("         Install production server: pip install waitress")
        app.run(host=args.host, port=args.port, debug=debug)  # type: ignore
    except KeyboardInterrupt:
        print("\nShutdown requested (Ctrl+C)")
    except Exception as e:  # pragma: no cover
        print("[FATAL] Server crashed:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()