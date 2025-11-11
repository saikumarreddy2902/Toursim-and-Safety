"""
Quick dev utility to create a Mongo-backed user account for login testing.

Usage (defaults create saikumar user):
    python backend/dev_create_user.py

Or specify values:
    python backend/dev_create_user.py --username saikumar --email sai@example.com \
        --password "Password@123" --full-name "Sai Kumar"

Requires MongoDB connection to be configured (MONGO_URI). The script will use
existing backend configuration via mongo_db.init_mongo().
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Dict

try:
    from repository import repo  # type: ignore
    from mongo_db import init_mongo, mongo_enabled  # type: ignore
except Exception as e:
    print(f"Failed to import backend modules: {e}")
    sys.exit(1)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create a dev user in MongoDB")
    parser.add_argument("--username", default="saikumar", help="Username for login")
    parser.add_argument("--email", default="saikumar@example.com", help="Email address")
    parser.add_argument(
        "--password", default="Password@123", help="Plaintext password to set"
    )
    parser.add_argument("--full-name", default="Saikumar", help="Full name")
    args = parser.parse_args(argv)

    if not mongo_enabled():
        print("MongoDB backend is not enabled. Set MONGO_URI and try again.")
        return 2

    try:
        init_mongo()
    except Exception as e:
        print(f"Mongo initialization failed: {e}")
        return 2

    try:
        doc: Dict[str, Any] = repo.create_user(
            username=args.username,
            email=args.email,
            password=args.password,
            full_name=args.full_name,
            email_verified=True,
        )
        print("User created:")
        print(f"  user_id:  {doc.get('user_id')}")
        print(f"  username: {doc.get('username')}")
        print(f"  email:    {doc.get('email')}")
        print("You can now log in at /user_login")
        return 0
    except ValueError as ve:
        print(f"Create user failed: {ve}")
        print("If the username or email already exists, choose different values.")
        return 1
    except Exception as e:
        print(f"Unexpected error creating user: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
