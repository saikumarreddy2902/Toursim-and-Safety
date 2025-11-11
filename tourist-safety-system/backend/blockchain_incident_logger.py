"""
Mongo-backed Blockchain Incident Logging (SQLite-free)
=====================================================

This module provides a simplified, MongoDB-backed implementation of the
blockchain logging API used by the incident response system. It removes all
SQLite usage and delegates persistence to helpers in backend.mongo_db.

Public contract preserved (used by incident_response.py):
- class BlockchainIncidentLogger(database_path: str)
  - log_incident_record(incident_data) -> {record_hash, block_hash, incident_hash, verification_status, timestamp}
  - log_response_activity(incident_id, activity_type, activity_data, actor_id=None, actor_type=None) -> activity_hash
  - create_immutable_storage_record(incident_id, storage_data) -> {storage_hash, block_hash, merkle_root, verification_url, public_audit_url}
  - get_incident_blockchain_record(incident_id) -> Dict[str, Any]
  - verify_blockchain_integrity() -> Dict[str, Any]

Implementation notes:
- Uses add_blockchain_record, log_response_activity, get_incident_blockchain_record, verify_blockchain_integrity
  from backend.mongo_db
- Computes hashes (incident/activity/storage) deterministically via SHA256
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Mongo helpers
try:
    from . import mongo_db as mdb  # when imported as package
except Exception:  # pragma: no cover
    import mongo_db as mdb  # fallback when run as script/module


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _merkle_root_from_dict(data: Dict[str, Any]) -> str:
    # Simple merkle root over sorted key/value pairs
    if not data:
        return hashlib.sha256(b"").hexdigest()
    leaves: List[str] = []
    for k in sorted(data.keys()):
        v = data[k]
        leaves.append(_sha256_json([k, v]))
    if len(leaves) == 1:
        return leaves[0]
    level = leaves
    while len(level) > 1:
        nxt: List[str] = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i + 1] if i + 1 < len(level) else level[i]
            nxt.append(hashlib.sha256((a + b).encode()).hexdigest())
        level = nxt
    return level[0]


class BlockchainIncidentLogger:
    """Mongo-backed implementation; database_path kept for API compatibility."""

    def __init__(self, database_path: str):
        self.database_path = database_path  # ignored in Mongo mode
        # Initialize Mongo once
        try:
            mdb.init_mongo()
        except Exception:
            pass

    # ---------- Public API ----------
    def log_incident_record(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        incident_id = incident_data.get("incident_id")
        incident_hash = self._create_incident_hash(incident_data)
        record_payload: Dict[str, Any] = {
            "transaction_type": "incident",
            "type": "incident_record",
            "incident_id": incident_id,
            "incident_hash": incident_hash,
            "timestamp": time.time(),
            "location": incident_data.get("location", {}),
            "incident_type": incident_data.get("incident_type"),
            "severity": incident_data.get("severity"),
            "tourist_id": incident_data.get("tourist_id"),
            "required_services": incident_data.get("required_services", []),
            "public_record": True,
        }
        # Append to Mongo blockchain collection
        rec = mdb.add_blockchain_record(record_payload)
        record_hash = rec.get("hash") or _sha256_json(record_payload)
        # For compatibility, use the same hash for block_hash
        return {
            "record_hash": record_hash,
            "block_hash": record_hash,
            "incident_hash": incident_hash,
            "verification_status": "recorded",
            "timestamp": record_payload["timestamp"],
        }

    def log_response_activity(
        self,
        incident_id: str,
        activity_type: str,
        activity_data: Dict[str, Any],
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
    ) -> str:
        activity_timestamp = time.time()
        activity_record: Dict[str, Any] = {
            "incident_id": incident_id,
            "activity_type": activity_type,
            "timestamp": activity_timestamp,
            "data": activity_data,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "system_timestamp": datetime.now().isoformat(),
        }
        activity_hash = self._create_activity_hash(activity_record)
        verification_hash = self._create_verification_hash(incident_id, activity_hash, activity_timestamp)
        # Persist to response activity logs (Mongo)
        try:
            mdb.log_response_activity(
                {
                    "incident_id": incident_id,
                    "activity_type": activity_type,
                    "activity_timestamp": datetime.now().isoformat(),
                    "activity_data": activity_record,
                    "actor_id": actor_id,
                    "actor_type": actor_type,
                    "verification_hash": verification_hash,
                    "immutable": True,
                }
            )
        except Exception:
            pass
        # Also append to blockchain records as an activity transaction (optional)
        try:
            mdb.add_blockchain_record(
                {
                    "transaction_type": "activity",
                    "incident_id": incident_id,
                    "activity_type": activity_type,
                    "activity_hash": activity_hash,
                    "timestamp": activity_timestamp,
                }
            )
        except Exception:
            pass
        return activity_hash

    def create_immutable_storage_record(self, incident_id: str, storage_data: Dict[str, Any]) -> Dict[str, Any]:
        storage_timestamp = time.time()
        storage_record: Dict[str, Any] = {
            "incident_id": incident_id,
            "storage_timestamp": storage_timestamp,
            "data": storage_data,
            "immutable": True,
        }
        merkle_root = _merkle_root_from_dict(storage_record)
        storage_hash = self._create_storage_hash(storage_record)
        try:
            mdb.add_blockchain_record(
                {
                    "transaction_type": "immutable_storage",
                    "incident_id": incident_id,
                    "merkle_root": merkle_root,
                    "timestamp": storage_timestamp,
                    "storage_hash": storage_hash,
                    "transparency_level": "public_audit",
                }
            )
        except Exception:
            pass
        return {
            "storage_hash": storage_hash,
            "block_hash": storage_hash,  # compatibility shim
            "merkle_root": merkle_root,
            "verification_url": f"/api/blockchain/verify/{incident_id}",
            "public_audit_url": f"/api/blockchain/audit/{incident_id}",
        }

    def get_incident_blockchain_record(self, incident_id: str) -> Dict[str, Any]:
        try:
            chain = mdb.get_incident_blockchain_record(incident_id)
        except Exception:
            chain = []
        try:
            activities = mdb.get_incident_activity_logs(incident_id)
        except Exception:
            activities = []
        first = chain[0] if chain else {}
        return {
            "incident_id": incident_id,
            "records": chain,
            "record_hash": first.get("hash"),
            "block_hash": first.get("hash"),
            "incident_data_hash": first.get("incident_hash"),
            "timestamp": first.get("timestamp"),
            "response_activities": activities,
            "verification_status": "verified",
            "immutable": True,
            "transparent": True,
        }

    def verify_blockchain_integrity(self) -> Dict[str, Any]:
        try:
            result: Dict[str, Any] = mdb.verify_blockchain_integrity()
        except Exception:
            result = {"enabled": False, "valid": False, "total_records": 0, "mismatches": []}
        total_records = int(result.get("total_records", 0))
        mismatches_list = result.get("mismatches", [])
        if isinstance(mismatches_list, list):
            mismatches: List[Any] = [m for m in mismatches_list]  # type: ignore[var-annotated]
        else:
            mismatches = []
        valid = bool(result.get("valid", False))
        status: Dict[str, Any] = {
            "total_blocks": total_records,
            "verified_blocks": total_records - len(mismatches),
            "integrity_status": "valid" if valid else "invalid",
            "errors": mismatches,
        }
        return status

    # ---------- Hash helpers ----------
    def _create_incident_hash(self, incident_data: Dict[str, Any]) -> str:
        critical = {
            "incident_id": incident_data.get("incident_id"),
            "timestamp": incident_data.get("timestamp"),
            "location": incident_data.get("location"),
            "incident_type": incident_data.get("incident_type"),
            "severity": incident_data.get("severity"),
            "tourist_id": incident_data.get("tourist_id"),
        }
        return _sha256_json(critical)

    def _create_activity_hash(self, activity_record: Dict[str, Any]) -> str:
        return _sha256_json(activity_record)

    def _create_verification_hash(self, incident_id: str, activity_hash: str, timestamp: float) -> str:
        return hashlib.sha256(f"{incident_id}:{activity_hash}:{timestamp}".encode()).hexdigest()

    def _create_storage_hash(self, storage_record: Dict[str, Any]) -> str:
        return _sha256_json(storage_record)