"""Unified repository abstraction for data access (users, sessions, stats).

Provides a single interface layer for data access backed by MongoDB only.
Legacy SQLite paths have been removed to satisfy the requirement that the
entire website runs only on MongoDB.

Usage:
    from repository import repo
    user = repo.get_user_by_username_or_email(identifier)
    repo.create_user(...)

Environment:
    Requires DB_BACKEND='mongo' and a valid MONGO_URI (pymongo installed)
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import os
import hashlib
from datetime import datetime, timedelta, timezone
import random, string

from werkzeug.security import generate_password_hash, check_password_hash

from mongo_db import (
    init_mongo, mongo_enabled, get_user_for_login as _mongo_get_user_for_login,
    update_failed_login as _mongo_update_failed_login, reset_failed_login as _mongo_reset_failed_login,
    create_user_session as _mongo_create_user_session, add_audit_log as _mongo_add_audit_log,
    incr_stat as _mongo_incr_stat, get_all_stats as _mongo_get_all_stats,
    get_admin_for_login as _mongo_get_admin_for_login,
    update_admin_failed_login as _mongo_update_admin_failed_login,
    reset_admin_failed_login as _mongo_reset_admin_failed_login
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Repository:
    PASSWORD_SCHEME_FIELD = 'pw_scheme'  # indicates hashing scheme version
    SCHEME_SHA256 = 'sha256_legacy'
    SCHEME_WERKZEUG = 'werkzeug_pbkdf2'

    def __init__(self) -> None:
        self._mongo_initialized = False

    # ---------- Utility ----------
    def _ensure_mongo(self) -> None:
        if mongo_enabled() and not self._mongo_initialized:
            self._mongo_initialized = init_mongo()

    def using_mongo(self) -> bool:
        self._ensure_mongo()
        return mongo_enabled() and self._mongo_initialized

    # ---------- User Retrieval ----------
    def get_user_by_username_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        identifier = identifier.strip().lower()
        doc = _mongo_get_user_for_login(identifier)
        if doc:
            return dict(doc)
        return None

    # ---------- Admin Retrieval ----------
    def get_admin_by_username_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        identifier = identifier.strip().lower()
        doc = _mongo_get_admin_for_login(identifier)
        if doc:
            return dict(doc)
        return None

    # ---------- Password Hashing ----------
    def hash_password(self, plain: str) -> str:
        # new scheme (werkzeug) automatically salted
        return generate_password_hash(plain)

    def verify_and_optionally_upgrade_password(self, user: Dict[str, Any], plain: str) -> bool:
        stored = user.get('password_hash', '')
        if not stored:
            return False

        # Detect scheme: legacy SHA256 is 64 hex chars without pbkdf markers
        is_legacy = len(stored) == 64 and all(c in '0123456789abcdef' for c in stored.lower())
        if is_legacy:
            if hashlib.sha256(plain.encode()).hexdigest() == stored:
                # Upgrade path
                new_hash = self.hash_password(plain)
                self._persist_password_upgrade(user, new_hash)
                return True
            return False
        # Assume werkzeug pbkdf2 scheme
        try:
            return check_password_hash(stored, plain)
        except Exception:
            return False

    def _persist_password_upgrade(self, user: Dict[str, Any], new_hash: str) -> None:
        from pymongo.collection import Collection  # type: ignore
        from mongo_db import _users as _mongo_users  # type: ignore
        _mongo_users: Collection  # type: ignore
        if _mongo_users is not None:
            _mongo_users.find_one_and_update({'_id': user.get('_id')}, {'$set': {'password_hash': new_hash}})  # type: ignore[attr-defined]
        return

    # ---------- Failed login tracking ----------
    def register_failed_login(self, user: Dict[str, Any]) -> None:
        failed = int(user.get('failed_login_attempts') or 0)
        if user.get('admin_id'):
            lock_until = None
            if failed + 1 >= 3:
                lock_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            _mongo_update_admin_failed_login(user, lock_until)
        else:
            lock_until = None
            if failed + 1 >= 5:
                lock_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            _mongo_update_failed_login(user, lock_until, increment=True)
        return

    def reset_login_success(self, user: Dict[str, Any]) -> None:
        if user.get('admin_id'):
            _mongo_reset_admin_failed_login(user)
        else:
            _mongo_reset_failed_login(user)
        return

    # ---------- Account lock check ----------
    def is_account_locked(self, user: Dict[str, Any]) -> bool:
        """Return True if the account is temporarily locked due to failures.

        Works for both Mongo-backed and legacy SQLite-backed user dicts.
        """
        locked_until = user.get('account_locked_until')
        if not locked_until:
            return False
        try:
            if isinstance(locked_until, (int, float)):
                # epoch seconds
                dt = datetime.fromtimestamp(float(locked_until), tz=timezone.utc)
            elif isinstance(locked_until, datetime):
                dt = locked_until if locked_until.tzinfo else locked_until.replace(tzinfo=timezone.utc)
            else:
                # assume ISO string
                dt = datetime.fromisoformat(str(locked_until))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            return dt > datetime.now(timezone.utc)
        except Exception:
            return False

    # ---------- Sessions & Audit ----------
    def create_session_and_audit(self, user: Dict[str, Any], ip: str | None, user_agent: str | None, device_info: str | None) -> str:
        session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        _mongo_create_user_session(user.get('_id'), ip, user_agent, device_info, session_id)
        audit_id = f"AUDIT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}"
        _mongo_add_audit_log(user.get('_id'), user.get('username',''), audit_id, ip, user_agent)
        return session_id

    # ---------- Stats ----------
    def incr_stat(self, name: str) -> None:
        _mongo_incr_stat(name)

    def get_stats(self) -> Dict[str, int]:
        return _mongo_get_all_stats()

    # ---------- User Creation (Registration + Inline account creation) ----------
    def create_user(self, *, username: str, email: str, password: str, full_name: str, email_verified: bool = False, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._ensure_mongo()
        username = username.strip().lower()
        email = email.strip().lower()
        password_hash = self.hash_password(password)
        extra = extra or {}
        user_identifier = f"USER-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
        from mongo_db import _users as _mongo_users  # type: ignore
        if _mongo_users is None:
            raise RuntimeError('Mongo users collection unavailable')
        # uniqueness checks
        existing = _mongo_users.find_one({'$or':[{'username': username},{'email': email}]})  # type: ignore[attr-defined]
        if existing:
            raise ValueError('Username or email already exists')
        doc: Dict[str, Any] = {
            'user_id': user_identifier,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'account_status': 'active',
            'email_verified': email_verified,
            'failed_login_attempts': 0,
            'login_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        doc.update(extra)
        _mongo_users.insert_one(doc)  # type: ignore[attr-defined]
        return doc  # type: ignore[return-value]

repo: Repository = Repository()
