r"""Quick MongoDB connectivity diagnostic.

Usage (PowerShell):
    # Set your variables first (Atlas example)
    $env:DB_BACKEND = 'mongo'
    $env:MONGO_URI = 'mongodb+srv://<user>:<password>@cluster.example.mongodb.net/?retryWrites=true&w=majority'
    $env:MONGO_DB_NAME = 'tourist_safety'
    .\venv\Scripts\python.exe test_mongo_connection.py

For local MongoDB:
    $env:MONGO_URI = 'mongodb://127.0.0.1:27017'

This script only reads environment variables; it does not modify the database
other than performing a lightweight ping and listing collection names.
"""
from __future__ import annotations

import os
import sys
import time
from typing import Any

try:
    from pymongo import MongoClient  # type: ignore
except Exception as e:  # pragma: no cover
    print("pymongo not installed or import failed:", e)
    sys.exit(2)


def main() -> int:
    db_backend = os.environ.get('DB_BACKEND')
    uri = os.environ.get('MONGO_URI')
    db_name = os.environ.get('MONGO_DB_NAME', 'tourist_safety')

    print("=== Mongo Connectivity Check ===")
    print(f"DB_BACKEND      : {db_backend}")
    print(f"MONGO_URI set   : {'yes' if uri else 'NO'}")
    print(f"Target DB Name  : {db_name}")

    if db_backend != 'mongo':
        print("ERROR: DB_BACKEND is not 'mongo'. Set $env:DB_BACKEND='mongo' and retry.")
        return 1
    if not uri:
        print("ERROR: MONGO_URI is not set. Set it to your Atlas or local connection string and retry.")
        return 1

    start = time.time()
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=6000)  # type: ignore
        # Ping admin to verify connectivity
        client.admin.command('ping')  # type: ignore
        elapsed = (time.time() - start) * 1000
        print(f"Ping OK ({elapsed:.1f} ms)")
    except Exception as e:
        print("PING FAILED:", e)
        print("Common causes:\n - Wrong password / user\n - IP not added to Atlas Network Access\n - SRV record blocked by firewall/DNS\n - Local network offline")
        return 2

    try:
        db = client[db_name]  # type: ignore[index]
        # Attempt a benign list of collection names
        cols: list[str] = sorted(db.list_collection_names())  # type: ignore
        if cols:
            print(f"Collections ({len(cols)}): {', '.join(cols[:10])}{' ...' if len(cols) > 10 else ''}")
        else:
            print("No collections yet (this is fine if app hasn't inserted anything).")
        # Simple stats: user count
        if 'users' in cols:
            try:
                count = db['users'].count_documents({})  # type: ignore[index]
                print(f"users collection count: {count}")
            except Exception:
                pass
        print("Status: SUCCESS")
        return 0
    except Exception as e:
        print("Listing collections failed:", e)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
