"""MongoDB integration layer for optional backend storage.

This module provides a thin abstraction for user authentication/session
operations so the existing Flask routes can switch between SQLite and MongoDB
based on environment configuration.

Environment variables:
    MONGO_URI        - Full MongoDB Atlas connection string (do NOT hardcode; set in .env or host environment)
    MONGO_DB_NAME    - Database name (default: tourist_safety)
    MONGO_STATS_COLL - Collection for aggregated counters (default: stats_counters)

To enable MongoDB usage set (example in PowerShell):
    $env:DB_BACKEND = 'mongo'
    $env:MONGO_URI = 'mongodb+srv://<user>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority'
    $env:MONGO_DB_NAME = 'tourist_safety'

If DB_BACKEND != 'mongo' or MONGO_URI missing, callers should fall back to SQLite.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, cast, TypedDict, List
import os
import datetime as dt
import hashlib
import json

try:
    from pymongo import MongoClient, ReturnDocument  # type: ignore
    from pymongo.collection import Collection  # type: ignore
    _pymongo_available = True
except Exception:  # pragma: no cover - dependency may not be installed yet
    _pymongo_available = False
    MongoClient = None  # type: ignore

_client: Optional[MongoClient] = None  # type: ignore
_db = None
_users: Optional[Collection] = None  # type: ignore
_sessions: Optional[Collection] = None  # type: ignore
_audit: Optional[Collection] = None  # type: ignore
_stats: Optional[Collection] = None  # type: ignore
_admins: Optional[Collection] = None  # type: ignore
_safe_zones: Optional[Collection] = None  # type: ignore
_restricted_zones: Optional[Collection] = None  # type: ignore
_zone_breach_alerts: Optional[Collection] = None  # type: ignore
_panic_alerts: Optional[Collection] = None  # type: ignore
_enhanced_panic_alerts: Optional[Collection] = None  # type: ignore
_emergency_sos: Optional[Collection] = None  # type: ignore
_location_tracking: Optional[Collection] = None  # type: ignore
_admin_notifications: Optional[Collection] = None  # type: ignore
_tourists_basic: Optional[Collection] = None  # type: ignore
_enhanced_tourists: Optional[Collection] = None  # type: ignore
_file_uploads: Optional[Collection] = None  # type: ignore
_blockchain_records: Optional[Collection] = None  # type: ignore
_geofence_violations: Optional[Collection] = None  # type: ignore
_registration_drafts: Optional[Collection] = None  # type: ignore
_risk_alerts: Optional[Collection] = None  # type: ignore
_ai_monitoring_results: Optional[Collection] = None  # type: ignore
_incidents: Optional[Collection] = None  # type: ignore
_dispatch_tracking: Optional[Collection] = None  # type: ignore
_authority_verifications: Optional[Collection] = None  # type: ignore
_incident_alerts: Optional[Collection] = None  # type: ignore
_response_activity_logs: Optional[Collection] = None  # type: ignore
_emergency_contact_responses: Optional[Collection] = None  # type: ignore
_post_incident_reports: Optional[Collection] = None  # type: ignore
_report_sharing_logs: Optional[Collection] = None  # type: ignore
_report_analytics: Optional[Collection] = None  # type: ignore
_authority_report_prefs: Optional[Collection] = None  # type: ignore
_auto_sos_events: Optional[Collection] = None  # type: ignore
_auto_sos_config: Optional[Collection] = None  # type: ignore
_incident_packages: Optional[Collection] = None  # type: ignore

# TypedDict schemas for stronger static typing of zone documents
class SafeZoneDoc(TypedDict, total=False):
    zone_name: str
    description: str
    zone_type: str
    center_lat: float
    center_lng: float
    radius_meters: int
    created_at: str
    active: bool
    zone_category: str

class RestrictedZoneDoc(TypedDict, total=False):
    zone_name: str
    description: str
    zone_type: str
    center_lat: float
    center_lng: float
    radius_meters: int
    restriction_level: str
    alert_message: str
    active: bool
    created_at: str


def mongo_enabled() -> bool:
    return bool(os.environ.get('DB_BACKEND') == 'mongo' and os.environ.get('MONGO_URI') and _pymongo_available)


def init_mongo() -> bool:
    """Initialize global Mongo handles if environment instructs to use mongo.
    Returns True if initialized, False otherwise.
    """
    global _client, _db, _users, _sessions, _audit, _stats, _admins, _safe_zones, _restricted_zones, _zone_breach_alerts, _panic_alerts, _enhanced_panic_alerts, _emergency_sos, _location_tracking, _admin_notifications, _tourists_basic, _enhanced_tourists, _file_uploads, _blockchain_records, _geofence_violations, _registration_drafts, _risk_alerts, _ai_monitoring_results, _incidents, _dispatch_tracking, _authority_verifications, _incident_alerts, _response_activity_logs, _emergency_contact_responses, _post_incident_reports, _report_sharing_logs, _report_analytics, _authority_report_prefs, _auto_sos_events, _auto_sos_config, mongo_db
    if not mongo_enabled():
        return False
    if _client is not None:
        return True

    uri = os.environ.get('MONGO_URI')
    db_name = os.environ.get('MONGO_DB_NAME', 'tourist_safety')

    # Fallback to mongomock for local/dev test if URI missing
    if not uri:
        try:  # pragma: no cover - dev convenience
            import mongomock  # type: ignore
            _mock_client = mongomock.MongoClient()  # type: ignore
            _client = _mock_client  # type: ignore
        except Exception:  # if mongomock unavailable, raise meaningful error
            raise RuntimeError("MONGO_URI not set and mongomock not installed; cannot initialize Mongo backend")
    else:
        _client = MongoClient(uri, serverSelectionTimeoutMS=8000)  # type: ignore
    _db = _client[db_name]  # type: ignore[index]
    _users = _db['users']  # type: ignore[index]
    _sessions = _db['user_sessions']  # type: ignore[index]
    _audit = _db['security_audit_logs']  # type: ignore[index]
    _stats = _db[os.environ.get('MONGO_STATS_COLL', 'stats_counters')]  # type: ignore[index]
    _admins = _db['admin_users']  # type: ignore[index]
    _safe_zones = _db['safe_zones']  # type: ignore[index]
    _restricted_zones = _db['restricted_zones']  # type: ignore[index]
    _zone_breach_alerts = _db['zone_breach_alerts']  # type: ignore[index]
    _panic_alerts = _db['panic_alerts']  # type: ignore[index]
    _enhanced_panic_alerts = _db['enhanced_panic_alerts']  # type: ignore[index]
    _emergency_sos = _db['emergency_sos']  # type: ignore[index]
    _location_tracking = _db['location_tracking']  # type: ignore[index]
    _admin_notifications = _db['admin_notifications']  # type: ignore[index]
    _tourists_basic = _db['tourists']  # type: ignore[index]
    _enhanced_tourists = _db['enhanced_tourists']  # type: ignore[index]
    _file_uploads = _db['file_uploads']  # type: ignore[index]
    _blockchain_records = _db['blockchain_records']  # type: ignore[index]
    _geofence_violations = _db['geofence_violations']  # type: ignore[index]
    _registration_drafts = _db['registration_drafts']  # type: ignore[index]
    _risk_alerts = _db['risk_alerts']  # type: ignore[index]
    _ai_monitoring_results = _db['ai_monitoring_results']  # type: ignore[index]
    _incidents = _db['incidents']  # type: ignore[index]
    _dispatch_tracking = _db['dispatch_tracking']  # type: ignore[index]
    _authority_verifications = _db['authority_verifications']  # type: ignore[index]
    _incident_alerts = _db['incident_alerts']  # type: ignore[index]
    _response_activity_logs = _db['response_activity_logs']  # type: ignore[index]
    _emergency_contact_responses = _db['emergency_contact_responses']  # type: ignore[index]
    _post_incident_reports = _db['post_incident_reports']  # type: ignore[index]
    _report_sharing_logs = _db['report_sharing_logs']  # type: ignore[index]
    _report_analytics = _db['report_analytics']  # type: ignore[index]
    _authority_report_prefs = _db['authority_report_preferences']  # type: ignore[index]
    _auto_sos_events = _db['auto_sos_events']  # type: ignore[index]
    _auto_sos_config = _db['auto_sos_config']  # type: ignore[index]
    _incident_packages = _db['incident_packages']  # type: ignore[index]

    # Indexes (idempotent)
    if _users is not None:  # runtime guard
        coll_u = cast(Any, _users)
        coll_u.create_index('user_id', unique=True)
        coll_u.create_index('username', unique=True)
        coll_u.create_index('email', unique=True)
    if _sessions is not None:
        cast(Any, _sessions).create_index('session_id', unique=True)
    if _audit is not None:
        cast(Any, _audit).create_index('log_id', unique=True)

    # Indexes for new collections
    if _admins is not None:
        coll_a = cast(Any, _admins)
        coll_a.create_index('admin_id', unique=True)
        coll_a.create_index('username', unique=True)
        coll_a.create_index('email', unique=True)
    if _safe_zones is not None:
        cast(Any, _safe_zones).create_index('zone_name', unique=True)
    if _restricted_zones is not None:
        cast(Any, _restricted_zones).create_index('zone_name', unique=True)
    if _zone_breach_alerts is not None:
        cast(Any, _zone_breach_alerts).create_index('timestamp')
    if _panic_alerts is not None:
        cast(Any, _panic_alerts).create_index('timestamp')
    if _enhanced_panic_alerts is not None:
        coll_ep = cast(Any, _enhanced_panic_alerts)
        coll_ep.create_index('alert_id', unique=True)
        coll_ep.create_index('status')
        coll_ep.create_index('timestamp')
    if _emergency_sos is not None:
        coll_sos = cast(Any, _emergency_sos)
        coll_sos.create_index('timestamp')
        coll_sos.create_index('status')
    if _location_tracking is not None:
        coll_lt = cast(Any, _location_tracking)
        coll_lt.create_index([('tourist_id', 1), ('timestamp', -1)])  # type: ignore
        coll_lt.create_index('timestamp')
    if _admin_notifications is not None:
        coll_an = cast(Any, _admin_notifications)
        coll_an.create_index('notification_id', unique=True)
        coll_an.create_index('created_at')
    if _tourists_basic is not None:
        tb = cast(Any, _tourists_basic)
        tb.create_index('tourist_id', unique=True)
        tb.create_index('created_at')
    if _enhanced_tourists is not None:
        et = cast(Any, _enhanced_tourists)
        et.create_index('tourist_id', unique=True)
        et.create_index('email')
        et.create_index('created_at')
    if _file_uploads is not None:
        fu = cast(Any, _file_uploads)
        fu.create_index('tourist_id')
        fu.create_index('upload_time')
    if _blockchain_records is not None:
        br = cast(Any, _blockchain_records)
        br.create_index('tourist_id')
        br.create_index('transaction_type')
    if _geofence_violations is not None:
        gv = cast(Any, _geofence_violations)
        gv.create_index('tourist_id')
        gv.create_index('zone_name')
        gv.create_index('timestamp')
    if _registration_drafts is not None:
        rd = cast(Any, _registration_drafts)
        rd.create_index('draft_id', unique=True)
        rd.create_index('updated')
    # Incident response related indexes
    if _incidents is not None:
        inc = cast(Any, _incidents)
        inc.create_index('incident_id', unique=True)
        inc.create_index('created_at')
        inc.create_index('status')
    if _dispatch_tracking is not None:
        dtc = cast(Any, _dispatch_tracking)
        dtc.create_index('dispatch_id', unique=True)
        dtc.create_index('incident_id')
        dtc.create_index('dispatch_timestamp')
        dtc.create_index('response_status')
    if _authority_verifications is not None:
        av = cast(Any, _authority_verifications)
        av.create_index('incident_id')
        av.create_index('authority_id')
        av.create_index('verification_timestamp')
    if _incident_alerts is not None:
        ial = cast(Any, _incident_alerts)
        ial.create_index('incident_id')
        ial.create_index('sent_timestamp')
    if _response_activity_logs is not None:
        ral = cast(Any, _response_activity_logs)
        ral.create_index('incident_id')
        ral.create_index('activity_timestamp')
    if _emergency_contact_responses is not None:
        ecr = cast(Any, _emergency_contact_responses)
        ecr.create_index('notification_timestamp')
        ecr.create_index('response_status')
    # Post-incident reporting related indexes
    if _post_incident_reports is not None:
        pir = cast(Any, _post_incident_reports)
        pir.create_index('report_id', unique=True)
        pir.create_index('incident_id')
        pir.create_index('report_generated_at')
        pir.create_index('status')
    if _report_sharing_logs is not None:
        rsl = cast(Any, _report_sharing_logs)
        rsl.create_index('report_id')
        rsl.create_index('shared_with_type')
        rsl.create_index('shared_at')
    if _report_analytics is not None:
        ra = cast(Any, _report_analytics)
        ra.create_index('report_id')
        ra.create_index('analyzed_at')
    if _authority_report_prefs is not None:
        arp = cast(Any, _authority_report_prefs)
        arp.create_index('authority_id', unique=True)
        arp.create_index('created_at')
    # Auto SOS indexes
    if _auto_sos_events is not None:
        ase = cast(Any, _auto_sos_events)
        ase.create_index('event_id', unique=True)
        ase.create_index('trigger_timestamp')
        ase.create_index('status')
        ase.create_index('tourist_id')
    if _auto_sos_config is not None:
        asc = cast(Any, _auto_sos_config)
        asc.create_index('config_key', unique=True)
    if _incident_packages is not None:
        ip = cast(Any, _incident_packages)
        ip.create_index('incident_id', unique=True)
        ip.create_index('created_timestamp')
    if _risk_alerts is not None:
        ra = cast(Any, _risk_alerts)
        try:
            ra.create_index('alert_id', unique=True)
            ra.create_index('alert_timestamp')
            ra.create_index([('priority', 1), ('alert_timestamp', -1)])  # type: ignore[arg-type]
        except Exception:
            pass
    if _ai_monitoring_results is not None:
        amr = cast(Any, _ai_monitoring_results)
        try:
            amr.create_index('analysis_timestamp')
            amr.create_index('tourist_id')
            amr.create_index('risk_level')
        except Exception:
            pass
    
    # Update the exported mongo_db reference
    mongo_db = _db  # type: ignore
    return True


# ============= Auto SOS (Mongo) =============

def get_auto_sos_config() -> Dict[str, Any]:
    """Return Auto SOS configuration from Mongo with safe defaults."""
    cfg: Dict[str, Any] = {
        'critical_risk_score': 0.85,
        'high_risk_score': 0.75,
        'sustained_risk_duration': 300,
        'movement_anomaly_threshold': 3,
        'confidence_threshold': 0.7,
        'cooldown_period': 1800,
        'tourist_confirmation_timeout': 60,
        'auto_sos_enabled': True,
    }
    if not mongo_enabled() or _auto_sos_config is None:
        return cfg
    cur = cast(Any, _auto_sos_config).find({})
    for row in cur:
        key = row.get('config_key')
        val = row.get('config_value')
        if key is None:
            continue
        # Coerce numeric/bool strings when possible
        if isinstance(val, str):
            lv = val.lower()
            if lv in ('true', 'false'):
                cfg[key] = (lv == 'true')
                continue
            try:
                if '.' in val:
                    cfg[key] = float(val)
                else:
                    cfg[key] = int(val)
                continue
            except Exception:
                pass
        cfg[key] = val
    return cfg


def set_auto_sos_config(key: str, value: Any) -> bool:
    if not mongo_enabled() or _auto_sos_config is None:
        return False
    res = cast(Any, _auto_sos_config).update_one({'config_key': key}, {
        '$set': {
            'config_value': value,
            'last_updated': dt.datetime.now(dt.timezone.utc).isoformat(),
        }
    }, upsert=True)
    return bool(getattr(res, 'modified_count', 1))


def create_auto_sos_event(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Create an Auto SOS event in Mongo and return stored doc."""
    if not mongo_enabled() or _auto_sos_events is None:
        raise RuntimeError('MongoDB not enabled for Auto SOS')
    base: Dict[str, Any] = {
        'event_id': doc.get('event_id') or f"AUTO-SOS-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S')}-{doc.get('tourist_id')}-{hashlib.sha1(str(dt.datetime.now().timestamp()).encode()).hexdigest()[:8]}",
        'tourist_id': doc.get('tourist_id'),
        'user_id': doc.get('user_id'),
        'trigger_type': doc.get('trigger_type', 'unknown'),
        'risk_score': float(doc.get('risk_score') or 0.0),
        'confidence': float(doc.get('confidence') or 0.0),
        'ai_monitoring_id': doc.get('ai_monitoring_id'),
        'trigger_timestamp': doc.get('trigger_timestamp') or dt.datetime.now(dt.timezone.utc).isoformat(),
        'location_lat': doc.get('location_lat'),
        'location_lng': doc.get('location_lng'),
        'location_accuracy': doc.get('location_accuracy'),
        'trigger_reason': doc.get('trigger_reason'),
        'status': doc.get('status', 'pending'),
        'tourist_response': None,
        'tourist_response_timestamp': None,
        'auto_escalated': False,
        'escalation_timestamp': None,
        'manual_sos_id': None,
        'resolved': False,
        'resolution_timestamp': None,
        'resolution_notes': None,
    }
    cast(Any, _auto_sos_events).insert_one(base)
    return base


def get_auto_sos_event(event_id: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _auto_sos_events is None:
        return None
    return cast(Any, _auto_sos_events).find_one({'event_id': event_id})


def update_auto_sos_event(event_id: str, updates: Dict[str, Any]) -> bool:
    if not mongo_enabled() or _auto_sos_events is None:
        return False
    res = cast(Any, _auto_sos_events).update_one({'event_id': event_id}, {'$set': updates})
    return bool(getattr(res, 'modified_count', 0))


def list_auto_sos_events(user_id: str, limit: int = 10) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _auto_sos_events is None:
        return []
    cur = cast(Any, _auto_sos_events).find({ '$or': [ {'user_id': user_id}, {'tourist_id': user_id} ] }).sort('trigger_timestamp', -1).limit(limit)
    return list(cur)


def is_auto_sos_enabled() -> bool:
    cfg = get_auto_sos_config()
    return bool(cfg.get('auto_sos_enabled', True))


def is_in_auto_sos_cooldown(tourist_id: str, cooldown_seconds: int) -> bool:
    if not mongo_enabled() or _auto_sos_events is None:
        return False
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=cooldown_seconds)).isoformat()
    cnt: int = cast(int, _auto_sos_events.count_documents({  # type: ignore[union-attr]
        'tourist_id': tourist_id,
        'trigger_timestamp': { '$gte': since },
        'status': { '$in': ['escalated', 'auto_escalated'] }
    }))
    return cnt > 0


def cooldown_remaining_seconds(tourist_id: str, cooldown_seconds: int) -> int:
    if not mongo_enabled() or _auto_sos_events is None:
        return 0
    doc = cast(Any, _auto_sos_events).find({
        'tourist_id': tourist_id,
        'status': { '$in': ['escalated', 'auto_escalated'] }
    }).sort('trigger_timestamp', -1).limit(1)
    docs = list(doc)
    if not docs:
        return 0
    last_ts = docs[0].get('trigger_timestamp')
    try:
        last_dt = dt.datetime.fromisoformat(last_ts)
    except Exception:
        return 0
    remaining = (last_dt + dt.timedelta(seconds=cooldown_seconds) - dt.datetime.now(dt.timezone.utc)).total_seconds()
    return max(0, int(remaining))


def sustained_high_risk(tourist_id: str, duration_seconds: int, risk_threshold: float) -> bool:
    if not mongo_enabled() or _ai_monitoring_results is None:
        return False
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=duration_seconds)).isoformat()
    cnt: int = cast(int, _ai_monitoring_results.count_documents({  # type: ignore[union-attr]
        'tourist_id': tourist_id,
        'analysis_timestamp': { '$gte': since },
        'risk_score': { '$gte': risk_threshold }
    }))
    return cnt >= 3


def find_pending_auto_sos_older_than(seconds: int) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _auto_sos_events is None:
        return []
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=seconds)).isoformat()
    cur = cast(Any, _auto_sos_events).find({
        'status': 'pending',
        'trigger_timestamp': { '$lt': cutoff }
    }).sort('trigger_timestamp', 1)
    return list(cur)


def auto_sos_statistics(hours: int = 24) -> Dict[str, Any]:
    if not mongo_enabled() or _auto_sos_events is None:
        return {
            'total_events': 0,
            'escalated_count': 0,
            'cancelled_count': 0,
            'pending_count': 0,
            'avg_risk_score': 0,
            'avg_confidence': 0,
            'trigger_types': {},
            'false_positive_rate': 0,
            'escalation_rate': 0,
        }
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)).isoformat()
    pipeline: List[Dict[str, Any]] = [
        { '$match': { 'trigger_timestamp': { '$gte': since } } },
        { '$group': {
            '_id': None,
            'total_events': { '$sum': 1 },
            'escalated_count': { '$sum': { '$cond': [ { '$in': ['$status', ['escalated','auto_escalated']] }, 1, 0 ] } },
            'cancelled_count': { '$sum': { '$cond': [ { '$eq': ['$status', 'cancelled'] }, 1, 0 ] } },
            'pending_count': { '$sum': { '$cond': [ { '$eq': ['$status', 'pending'] }, 1, 0 ] } },
            'avg_risk_score': { '$avg': '$risk_score' },
            'avg_confidence': { '$avg': '$confidence' },
        } }
    ]
    agg = list(cast(Any, _auto_sos_events).aggregate(pipeline))
    base: Dict[str, Any] = cast(Dict[str, Any], agg[0]) if agg else {}
    # trigger type distribution
    type_cur = cast(Any, _auto_sos_events).aggregate([
        { '$match': { 'trigger_timestamp': { '$gte': since } } },
        { '$group': { '_id': '$trigger_type', 'count': { '$sum': 1 } } }
    ])
    types: Dict[str, int] = {}
    for row in type_cur:
        types[str(row.get('_id'))] = int(row.get('count') or 0)
    total: int = int(cast(Any, base.get('total_events')) or 0)
    cancelled: int = int(cast(Any, base.get('cancelled_count')) or 0)
    escalated: int = int(cast(Any, base.get('escalated_count')) or 0)
    return {
        'total_events': total,
        'escalated_count': escalated,
        'cancelled_count': cancelled,
        'pending_count': int(cast(Any, base.get('pending_count')) or 0),
        'avg_risk_score': round(float(cast(Any, base.get('avg_risk_score')) or 0), 3),
        'avg_confidence': round(float(cast(Any, base.get('avg_confidence')) or 0), 3),
        'trigger_types': types,
        'false_positive_rate': round((cancelled / max(total, 1)) * 100, 1),
        'escalation_rate': round((escalated / max(total, 1)) * 100, 1)
    }


def store_incident_package(package: Dict[str, Any]) -> bool:
    """Store incident package in Mongo incident_packages collection."""
    if not mongo_enabled() or _incident_packages is None:
        return False
    doc: Dict[str, Any] = {
        'incident_id': package.get('incident_metadata', {}).get('incident_id'),
        'incident_type': package.get('incident_metadata', {}).get('incident_type'),
        'tourist_id': package.get('digital_identity', {}).get('contact_data', {}).get('user_id'),
        'package_data': package,
        'created_timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'accessed_count': 0,
        'last_accessed': None,
    }
    cast(Any, _incident_packages).insert_one(doc)
    return True


# ============= User Operations =============

def get_user_for_login(username_or_email: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _users is None:
        return None
    return _users.find_one({ '$or': [ {'username': username_or_email}, {'email': username_or_email} ] })  # type: ignore


def update_failed_login(user_doc: Dict[str, Any], lock_until: Optional[dt.datetime], increment: bool = True) -> None:
    if not mongo_enabled() or _users is None:
        return
    failed = int(user_doc.get('failed_login_attempts') or 0)
    if increment:
        failed += 1
    _users.update_one({'_id': user_doc['_id']}, {  # type: ignore[union-attr]
        '$set': {
            'failed_login_attempts': failed,
            'account_locked_until': lock_until.isoformat() if lock_until else None
        }
    })


def reset_failed_login(user_doc: Dict[str, Any]) -> None:
    if not mongo_enabled() or _users is None:
        return
    _users.update_one({'_id': user_doc['_id']}, {  # type: ignore[union-attr]
        '$set': {
            'failed_login_attempts': 0,
            'account_locked_until': None,
            'last_login': dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        '$inc': { 'login_count': 1 }
    })


def create_user_session(user_id: Any, ip: str | None, user_agent: str | None, device_info: str | None, session_id: str) -> None:
    if not mongo_enabled() or _sessions is None:
        return
    _sessions.insert_one({  # type: ignore[union-attr]
        'session_id': session_id,
        'user_id': user_id,
        'user_type': 'user',
        'ip_address': ip,
        'user_agent': user_agent,
        'device_info': device_info,
        'login_timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'session_status': 'active'
    })

# ----- Admin session helpers (Mongo) -----

def create_admin_session(admin_id: Any, session_id: str, ip: str | None, user_agent: str | None, device_info: str | None, expires_at: dt.datetime | None = None) -> None:
    """Record an admin session in user_sessions collection (shared with users)."""
    if not mongo_enabled() or _sessions is None:
        return
    doc: Dict[str, Any] = {
        'session_id': session_id,
        'user_id': admin_id,
        'user_type': 'admin',
        'ip_address': ip,
        'user_agent': user_agent,
        'device_info': device_info,
        'login_timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'logout_timestamp': None,
        'session_status': 'active',
        'expires_at': expires_at.isoformat() if expires_at else None
    }
    try:
        cast(Any, _sessions).insert_one(doc)
    except Exception:
        pass

def end_admin_session(session_id: str) -> bool:
    if not mongo_enabled() or _sessions is None:
        return False
    res = cast(Any, _sessions).update_one({'session_id': session_id, 'user_type': 'admin', 'session_status': 'active'}, {
        '$set': {
            'session_status': 'terminated',
            'logout_timestamp': dt.datetime.now(dt.timezone.utc).isoformat()
        }
    })
    return bool(getattr(res, 'modified_count', 0))

def clear_admin_auth_state(admin_id: Any) -> None:
    """Clear session token / expiry on admin user record."""
    if not mongo_enabled() or _admins is None:
        return
    try:
        _admins.update_one({'admin_id': admin_id}, {'$set': {'session_token': None, 'session_expires': None}})  # type: ignore[union-attr]
    except Exception:
        pass

def list_admin_sessions_mongo(limit: int = 50, active_only: bool = False) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _sessions is None:
        return []
    query: Dict[str, Any] = {'user_type': 'admin'}
    if active_only:
        query['session_status'] = 'active'
    cur = cast(Any, _sessions).find(query).sort('login_timestamp', -1).limit(limit)
    return list(cur)


def add_audit_log(user_id: Any, username: str, log_id: str, ip: str | None, user_agent: str | None) -> None:
    if not mongo_enabled() or _audit is None:
        return
    _audit.insert_one({  # type: ignore[union-attr]
        'log_id': log_id,
        'user_id': user_id,
        'user_type': 'user',
        'action_type': 'USER_LOGIN',
        'action_description': f'Successful login: {username}',
        'ip_address': ip,
        'user_agent': user_agent,
        'success': True,
        'timestamp': dt.datetime.now(dt.timezone.utc).isoformat()
    })


def incr_stat(counter: str) -> None:
    if not mongo_enabled() or _stats is None:
        return
    _stats.find_one_and_update({'_id': counter}, {'$inc': {'value': 1}}, upsert=True, return_document=ReturnDocument.AFTER)  # type: ignore[union-attr]


# Optional helper to fetch aggregated numbers

def get_all_stats() -> Dict[str, int]:
    if not mongo_enabled() or _stats is None:
        return {}
    results: Dict[str, int] = {}
    for doc in cast(Any, _stats).find():  # type: ignore[union-attr]
        key = str(doc.get('_id'))
        results[key] = int(doc.get('value', 0))
    return results

# ============= Admin Operations =============

def get_admin_for_login(identifier: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _admins is None:
        return None
    ident = identifier.lower().strip()
    return _admins.find_one({'$or': [{'username': ident}, {'email': ident}]})  # type: ignore[union-attr]

def get_admin_by_admin_id(admin_id: str) -> Optional[Dict[str, Any]]:
    """Fetch an admin document by its admin_id (Mongo only)."""
    if not mongo_enabled() or _admins is None:
        return None
    return _admins.find_one({'admin_id': admin_id})  # type: ignore[union-attr]

def update_admin_failed_login(admin_doc: Dict[str, Any], lock_until: Optional[dt.datetime]) -> None:
    if not mongo_enabled() or _admins is None:
        return
    failed = int(admin_doc.get('failed_login_attempts') or 0) + 1
    _admins.update_one({'_id': admin_doc['_id']}, {  # type: ignore[union-attr]
        '$set': {
            'failed_login_attempts': failed,
            'account_locked_until': lock_until.isoformat() if lock_until else None
        }
    })

def reset_admin_failed_login(admin_doc: Dict[str, Any]) -> None:
    if not mongo_enabled() or _admins is None:
        return
    _admins.update_one({'_id': admin_doc['_id']}, {  # type: ignore[union-attr]
        '$set': {
            'failed_login_attempts': 0,
            'account_locked_until': None,
            'last_login': dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        '$inc': {'login_count': 1}
    })

def ensure_default_admin() -> None:
    """Create a default admin if none exist (Mongo only)."""
    if not mongo_enabled() or _admins is None:
        return
    if _admins.count_documents({}) == 0:  # type: ignore[union-attr]
        admin_doc: Dict[str, Any] = {
            'admin_id': f"ADMIN-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}",
            'username': 'admin',
            'email': 'admin@touristsafety.com',
            'password_hash': '',
            'full_name': 'System Administrator',
            'department': 'IT Security',
            'role': 'super_admin',
            'permission_level': 5,
            'account_status': 'active',
            'failed_login_attempts': 0,
            'login_count': 0,
            'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'updated_at': dt.datetime.now(dt.timezone.utc).isoformat()
        }
        try:
            from werkzeug.security import generate_password_hash  # type: ignore
            admin_doc['password_hash'] = generate_password_hash('AdminPass123!')  # type: ignore[index]
        except Exception:
            admin_doc['password_hash'] = ''
        _admins.insert_one(admin_doc)  # type: ignore[union-attr]

 # ============= Zones Operations =============

def ensure_default_zones() -> None:
    if not mongo_enabled() or _safe_zones is None or _restricted_zones is None:
        return
    if _safe_zones.count_documents({}) == 0:  # type: ignore[union-attr]
        safe_defaults: List[SafeZoneDoc] = [
            {
                'zone_name': 'Airport Security Zone',
                'description': 'International airport security perimeter',
                'zone_type': 'circular',
                'center_lat': 17.2403,
                'center_lng': 78.4294,
                'radius_meters': 2000,
                'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'active': True,
                'zone_category': 'transport_hub',
            },
            {
                'zone_name': 'Tourist Information Center',
                'description': 'Government tourist information center',
                'zone_type': 'circular',
                'center_lat': 17.3850,
                'center_lng': 78.4867,
                'radius_meters': 500,
                'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'active': True,
                'zone_category': 'information_center',
            },
            {
                'zone_name': 'Police Station Area',
                'description': 'Police station safe radius',
                'zone_type': 'circular',
                'center_lat': 17.4065,
                'center_lng': 78.4772,
                'radius_meters': 300,
                'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'active': True,
                'zone_category': 'safety_services',
            },
        ]
        _safe_zones.insert_many(safe_defaults)  # type: ignore[union-attr]
    if _restricted_zones.count_documents({}) == 0:  # type: ignore[union-attr]
        restricted_defaults: List[RestrictedZoneDoc] = [
            {
                'zone_name': 'Industrial Area',
                'description': 'Heavy industrial zone - restricted access',
                'zone_type': 'circular',
                'center_lat': 17.4500,
                'center_lng': 78.3800,
                'radius_meters': 1500,
                'restriction_level': 'warning',
                'alert_message': 'You are entering an industrial area. Exercise caution.',
                'active': True,
                'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            },
            {
                'zone_name': 'High Crime Area',
                'description': 'Area with elevated security risks',
                'zone_type': 'circular',
                'center_lat': 17.3200,
                'center_lng': 78.5200,
                'radius_meters': 800,
                'restriction_level': 'danger',
                'alert_message': 'WARNING: High-risk area.',
                'active': True,
                'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            },
            {
                'zone_name': 'Military Zone',
                'description': 'Restricted military installation',
                'zone_type': 'circular',
                'center_lat': 17.5000,
                'center_lng': 78.4000,
                'radius_meters': 1000,
                'restriction_level': 'prohibited',
                'alert_message': 'PROHIBITED AREA: Entry restricted.',
                'active': True,
                'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            },
        ]
        _restricted_zones.insert_many(restricted_defaults)  # type: ignore[union-attr]

def get_active_safe_zones() -> list[Dict[str, Any]]:
    if not mongo_enabled() or _safe_zones is None:
        return []
    return list(cast(Any, _safe_zones).find({'active': True}))  # type: ignore[union-attr]

def get_active_restricted_zones() -> list[Dict[str, Any]]:
    if not mongo_enabled() or _restricted_zones is None:
        return []
    return list(cast(Any, _restricted_zones).find({'active': True}))  # type: ignore[union-attr]

# ---- Analytics helper functions (public) ----
def count_zone_breaches_since(since: dt.datetime) -> int:
    if not mongo_enabled() or _zone_breach_alerts is None:
        return 0
    return int(cast(Any, _zone_breach_alerts).count_documents({'timestamp': {'$gte': since}}))

def aggregate_zone_breaches(pipeline: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _zone_breach_alerts is None:
        return []
    return list(cast(Any, _zone_breach_alerts).aggregate(pipeline))

def distinct_restricted_tourists_since(since: dt.datetime) -> int:
    if not mongo_enabled() or _location_tracking is None:
        return 0
    filt: Dict[str, Any] = {'is_inside_restricted_zone': True, 'timestamp': {'$gte': since}}
    ids = list(cast(Any, _location_tracking).distinct('tourist_id', filt))
    return len(ids)

def list_safe_zones(include_inactive: bool = True) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _safe_zones is None:
        return []
    query: Dict[str, Any] = {} if include_inactive else {'active': True}
    return list(cast(Any, _safe_zones).find(query).sort('created_at', -1))

def list_restricted_zones(include_inactive: bool = True) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _restricted_zones is None:
        return []
    query: Dict[str, Any] = {} if include_inactive else {'active': True}
    return list(cast(Any, _restricted_zones).find(query).sort('created_at', -1))

def create_safe_zone(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _safe_zones is None:
        return {}
    base = dict(doc)
    base.setdefault('active', True)
    base.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _safe_zones).insert_one(base)
    return base

def create_restricted_zone(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _restricted_zones is None:
        return {}
    base = dict(doc)
    base.setdefault('active', True)
    base.setdefault('auto_alert', bool(base.get('auto_alert', True)))
    base.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _restricted_zones).insert_one(base)
    return base

def insert_zone_breach_alert(doc: Dict[str, Any]) -> None:
    if not mongo_enabled() or _zone_breach_alerts is None:
        return
    doc.setdefault('timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    _zone_breach_alerts.insert_one(doc)  # type: ignore[union-attr]

def ensure_domain_initialized() -> None:
    if not mongo_enabled():
        return
    init_mongo()
    ensure_default_admin()
    ensure_default_zones()

# ============= User Management (Registration) =============

def create_user(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new tourist/user document.
    Expects fields: username, email, password_hash (already hashed), full_name (optional)
    Generates user_id if not provided.
    """
    if not mongo_enabled() or _users is None:
        return {}
    base = dict(user_doc)
    base.setdefault('user_id', f"USER-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}")
    base.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('updated_at', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('account_status', 'active')
    cast(Any, _users).insert_one(base)
    return base

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _users is None:
        return None
    return _users.find_one({'user_id': user_id})  # type: ignore

# ============= Enhanced Tourist Registration =============

def create_enhanced_tourist(enhanced_doc: Dict[str, Any], file_records: list[Dict[str, Any]] | None = None, blockchain_record: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Create enhanced tourist registration in Mongo.
    enhanced_doc should already contain 'tourist_id'.
    file_records: list of file metadata dicts (each must include at least stored_name/path/type)
    blockchain_record: optional blockchain metadata.
    """
    if not mongo_enabled() or _enhanced_tourists is None:
        return {}
    base = dict(enhanced_doc)
    base.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('updated_at', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _enhanced_tourists).insert_one(base)
    if file_records and _file_uploads is not None:
        enriched: List[Dict[str, Any]] = []
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
        for fr in file_records:
            r = dict(fr)
            r.setdefault('tourist_id', base.get('tourist_id'))
            r.setdefault('upload_time', now_iso)
            enriched.append(r)
        if enriched:
            cast(Any, _file_uploads).insert_many(enriched)
    if blockchain_record and _blockchain_records is not None:
        brec = dict(blockchain_record)
        brec.setdefault('tourist_id', base.get('tourist_id'))
        brec.setdefault('timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
        cast(Any, _blockchain_records).insert_one(brec)
    return base

def get_enhanced_tourist(tourist_id: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _enhanced_tourists is None:
        return None
    return _enhanced_tourists.find_one({'tourist_id': tourist_id})  # type: ignore

def list_enhanced_tourists(limit: int = 100) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _enhanced_tourists is None:
        return []
    return list(cast(Any, _enhanced_tourists).find().sort('created_at', -1).limit(limit))

# ============= Admin Notifications =============

def create_admin_notification(data: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _admin_notifications is None:
        return {}
    doc = dict(data)
    doc.setdefault('notification_id', f"NOTIF-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}")
    doc.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    doc.setdefault('status', 'unread')
    doc.setdefault('read', False)  # Add 'read' field for consistency
    cast(Any, _admin_notifications).insert_one(doc)
    return doc

def get_recent_admin_notifications(limit: int = 50) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _admin_notifications is None:
        return []
    cur = cast(Any, _admin_notifications).find().sort('created_at', -1).limit(limit)
    return list(cur)

def list_admin_notifications(notification_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get admin notifications with optional type filtering"""
    if not mongo_enabled() or _admin_notifications is None:
        return []
    try:
        query: Dict[str, Any] = {}
        if notification_type:
            query['type'] = notification_type
        cur = cast(Any, _admin_notifications).find(query).sort('created_at', -1).limit(limit)
        notifications = list(cur)
        
        # Convert ObjectId to string for JSON serialization
        for notification in notifications:
            if '_id' in notification:
                notification['_id'] = str(notification['_id'])
        
        return notifications
    except Exception as e:
        print(f"Error listing admin notifications: {e}")
        return []

def mark_admin_notification_read(notification_id: str) -> bool:
    """Mark an admin notification as read (sets status/read_status fields)."""
    if not mongo_enabled() or _admin_notifications is None:
        return False
    try:
        from bson import ObjectId  # type: ignore
        # Try to convert to ObjectId if it's a valid MongoDB ID
        try:
            query: Dict[str, Any] = {'_id': ObjectId(notification_id)}  # type: ignore
        except Exception:
            # Fallback to string comparison if not a valid ObjectId
            query = {'notification_id': notification_id}  # type: ignore
        
        res = cast(Any, _admin_notifications).update_one(query, {
            '$set': {
                'status': 'read',
                'read': True,  # Add 'read' field for consistency
                'read_status': True,
                'read_at': dt.datetime.now(dt.timezone.utc).isoformat()
            }
        })
        return bool(getattr(res, 'modified_count', 0))
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return False

# ============= SOS / Auto-SOS helpers =============

def create_sos_event(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Create a generic SOS event document in emergency_sos collection.

    Required fields (validated lightly): sos_id, emergency_type, message, status.
    """
    if not mongo_enabled() or _emergency_sos is None:
        return {}
    base = dict(doc)
    base.setdefault('timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('created_at', base['timestamp'])
    base.setdefault('status', 'ACTIVE')
    try:
        cast(Any, _emergency_sos).insert_one(base)
    except Exception:
        pass
    return base


# ============= Panic Alerts & SOS =============

def create_basic_panic_alert(tourist_id: str | None, latitude: float, longitude: float) -> Dict[str, Any]:
    if not mongo_enabled() or _panic_alerts is None:
        return {}
    doc: Dict[str, Any] = {
        'tourist_id': tourist_id,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'status': 'active',
        'alert_type': 'standard'
    }
    _panic_alerts.insert_one(doc)  # type: ignore[union-attr]
    return doc

def create_enhanced_panic_alert(data: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _enhanced_panic_alerts is None:
        return {}
    base = dict(data)
    base.setdefault('alert_id', f"ALERT-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}")
    base.setdefault('timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('status', 'active')
    _enhanced_panic_alerts.insert_one(base)  # type: ignore[union-attr]
    return base

def get_recent_enhanced_panic_alerts(limit: int = 50) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _enhanced_panic_alerts is None:
        return []
    cur = cast(Any, _enhanced_panic_alerts).find().sort('timestamp', -1).limit(limit)
    return list(cur)

def get_panic_alert_metrics() -> Dict[str, Any]:
    if not mongo_enabled() or _enhanced_panic_alerts is None:
        return {}
    total_active_i: int = cast(int, _enhanced_panic_alerts.count_documents({'status': 'active'}))  # type: ignore[union-attr]
    from_dt = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_i: int = cast(int, _enhanced_panic_alerts.count_documents({'timestamp': {'$gte': from_dt.isoformat()}}))  # type: ignore[union-attr]
    severities = list(cast(Any, _enhanced_panic_alerts).aggregate([
        {'$match': {'status': 'active'}},
        {'$group': {'_id': None, 'avg': {'$avg': '$severity_level'}}}
    ]))
    avg_sev = severities[0]['avg'] if severities else 0
    return {
        'active_alerts': int(total_active_i),
        'alerts_today': int(today_i),
        'avg_severity': float(avg_sev)
    }

def create_emergency_sos(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _emergency_sos is None:
        return {}
    base = dict(doc)
    base.setdefault('timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('status', 'ACTIVE')
    _emergency_sos.insert_one(base)  # type: ignore[union-attr]
    return base

def get_recent_sos(limit: int = 50) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _emergency_sos is None:
        return []
    cur = cast(Any, _emergency_sos).find().sort('timestamp', -1).limit(limit)
    return list(cur)

def get_sos_metrics() -> Dict[str, Any]:
    if not mongo_enabled() or _emergency_sos is None:
        return {}
    total_active_i: int = cast(int, _emergency_sos.count_documents({'status': 'ACTIVE'}))  # type: ignore[union-attr]
    from_dt = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_i: int = cast(int, _emergency_sos.count_documents({'timestamp': {'$gte': from_dt.isoformat()}}))  # type: ignore[union-attr]
    return {'active_sos': int(total_active_i), 'sos_today': int(today_i)}

def update_sos_status(sos_id: str, status: str, admin_response: str = '', admin_id: str = '') -> bool:
    """Update SOS alert status and add admin response."""
    if not mongo_enabled() or _emergency_sos is None:
        return False
    update_data: Dict[str, Any] = {
        'status': status,
        'updated_at': dt.datetime.now(dt.timezone.utc).isoformat()
    }
    if admin_response:
        update_data['admin_response'] = admin_response
    if admin_id:
        update_data['responded_by'] = admin_id
    result = cast(Any, _emergency_sos).update_one(
        {'sos_id': sos_id},
        {'$set': update_data}
    )
    return result.modified_count > 0  # type: ignore

def get_sos_by_id(sos_id: str) -> Dict[str, Any] | None:
    """Get a specific SOS alert by ID."""
    if not mongo_enabled() or _emergency_sos is None:
        return None
    result = cast(Any, _emergency_sos).find_one({'sos_id': sos_id})
    if result:
        # Convert ObjectId to string for JSON serialization
        if '_id' in result:
            result['_id'] = str(result['_id'])
        return dict(result)
    return None

# ============= Location Tracking =============

def insert_location_tracking(doc: Dict[str, Any]) -> None:
    if not mongo_enabled() or _location_tracking is None:
        return
    base = dict(doc)
    base.setdefault('timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    _location_tracking.insert_one(base)  # type: ignore[union-attr]

def get_recent_locations(tourist_id: str, limit: int = 100) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _location_tracking is None:
        return []
    cur = cast(Any, _location_tracking).find({'tourist_id': tourist_id}).sort('timestamp', -1).limit(limit)
    return list(cur)

# ============= Post-Incident Reporting (Mongo) =============

def create_post_incident_report(report_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a post-incident report document (Mongo only)."""
    if not mongo_enabled() or _post_incident_reports is None:
        return {}
    base = dict(report_doc)
    base.setdefault('report_generated_at', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('status', 'draft')
    cast(Any, _post_incident_reports).insert_one(base)
    return base

def get_post_incident_report(report_id: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _post_incident_reports is None:
        return None
    return cast(Any, _post_incident_reports).find_one({'report_id': report_id})

def share_post_incident_report(report_id: str, shared_with_type: str, shared_with_id: str, method: str, delivery_status: str = 'pending') -> Dict[str, Any]:
    if not mongo_enabled() or _report_sharing_logs is None:
        return {}
    log: Dict[str, Any] = {
        'sharing_id': f"SHARE-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S')}-{os.getpid()}",
        'report_id': report_id,
        'shared_with_type': shared_with_type,
        'shared_with_id': shared_with_id,
        'shared_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'sharing_method': method,
        'delivery_status': delivery_status,
        'access_log': []
    }
    cast(Any, _report_sharing_logs).insert_one(log)
    return log

def list_reports_for_tourist(tourist_id: str, limit: int = 50) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _post_incident_reports is None:
        return []
    cur = cast(Any, _post_incident_reports).find({'tourist_id': tourist_id}).sort('report_generated_at', -1).limit(limit)
    return list(cur)

def get_reporting_statistics(limit_recent: int = 10) -> Dict[str, Any]:
    if not mongo_enabled() or _post_incident_reports is None:
        return {}
    total_reports = cast(Any, _post_incident_reports).count_documents({})
    completed = cast(Any, _post_incident_reports).count_documents({'status': 'completed'})
    # shares
    total_shares = 0
    tourist_shares = 0
    authority_shares = 0
    if _report_sharing_logs is not None:
        total_shares = cast(Any, _report_sharing_logs).count_documents({})
        tourist_shares = cast(Any, _report_sharing_logs).count_documents({'shared_with_type': 'tourist'})
        authority_shares = cast(Any, _report_sharing_logs).count_documents({'shared_with_type': 'authority'})
    recent: List[Dict[str, Any]] = []
    for r in cast(Any, _post_incident_reports).find().sort('report_generated_at', -1).limit(limit_recent):
        recent.append({
            'report_id': r.get('report_id'),
            'incident_id': r.get('incident_id'),
            'report_generated_at': r.get('report_generated_at'),
            'report_type': r.get('report_type', 'full')
        })
    return {
        'total_reports': int(total_reports),
        'completed_reports': int(completed),
        'total_shares': int(total_shares),
        'tourist_shares': int(tourist_shares),
        'authority_shares': int(authority_shares),
        'recent_reports': recent
    }

# ============= Geofence Violations =============

def log_geofence_violation(tourist_id: str, zone_name: str, latitude: float, longitude: float) -> Dict[str, Any]:
    if not mongo_enabled() or _geofence_violations is None:
        return {}
    doc: Dict[str, Any] = {
        'tourist_id': tourist_id,
        'zone_name': zone_name,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': dt.datetime.now(dt.timezone.utc).isoformat()
    }
    cast(Any, _geofence_violations).insert_one(doc)
    return doc

def get_recent_geofence_violations(tourist_id: str | None = None, limit: int = 100) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _geofence_violations is None:
        return []
    query: Dict[str, Any] = {}
    if tourist_id:
        query['tourist_id'] = tourist_id
    cur = cast(Any, _geofence_violations).find(query).sort('timestamp', -1).limit(limit)  # type: ignore
    return list(cur)

# ============= Registration Drafts =============

def save_registration_draft(draft_id: str, step: int, step_data: Dict[str, Any]) -> Dict[str, Any]:
    """Upsert a registration draft merging step data."""
    if not mongo_enabled() or _registration_drafts is None:
        return {}
    existing_any = cast(Any, _registration_drafts).find_one({'draft_id': draft_id})
    existing: Dict[str, Any]
    if isinstance(existing_any, dict):
        existing = existing_any  # type: ignore[assignment]
    else:
        existing = {}
    if not existing:
        existing = {
            'draft_id': draft_id,
            'created': dt.datetime.now(dt.timezone.utc).isoformat(),
            'steps': {},
            'last_step': None
        }
    steps_obj = existing.get('steps')
    steps: Dict[str, Any]
    if isinstance(steps_obj, dict):
        steps = cast(Dict[str, Any], steps_obj)
    else:
        steps = {}
    steps[str(step)] = step_data
    existing['steps'] = steps
    existing['last_step'] = step
    existing['updated'] = dt.datetime.now(dt.timezone.utc).isoformat()
    cast(Any, _registration_drafts).update_one({'draft_id': draft_id}, {'$set': existing}, upsert=True)
    return existing

def get_registration_draft(draft_id: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _registration_drafts is None:
        return None
    return cast(Any, _registration_drafts).find_one({'draft_id': draft_id})

# ============= Risk Alerts & AI Monitoring (Mongo replacement) =============

def insert_risk_alert(alert_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a risk alert document.

    Ensures alert_id and alert_timestamp fields. Returns stored document (shallow copy).
    """
    if not mongo_enabled() or _risk_alerts is None:
        return {}
    doc = dict(alert_doc)
    doc.setdefault('alert_id', f"ALERT-{dt.datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    doc.setdefault('alert_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    doc.setdefault('acknowledged', False)
    doc.setdefault('resolved', False)
    cast(Any, _risk_alerts).insert_one(doc)
    return doc

def list_risk_alerts(hours: int = 24, priority: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
    if not mongo_enabled() or _risk_alerts is None:
        return []
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    query: Dict[str, Any] = {'alert_timestamp': {'$gte': since.isoformat()}}
    if priority:
        query['priority'] = priority
    cur = cast(Any, _risk_alerts).find(query).sort('alert_timestamp', -1).limit(limit)
    return list(cur)

def acknowledge_risk_alert(alert_id: str, admin_id: Any) -> bool:
    if not mongo_enabled() or _risk_alerts is None:
        return False
    res = cast(Any, _risk_alerts).update_one({'alert_id': alert_id}, {'$set': {
        'acknowledged': True,
        'acknowledged_by': admin_id,
        'acknowledgment_timestamp': dt.datetime.now(dt.timezone.utc).isoformat()
    }})
    return res.modified_count > 0  # type: ignore[no-any-return]

def resolve_risk_alert(alert_id: str) -> bool:
    if not mongo_enabled() or _risk_alerts is None:
        return False
    res = cast(Any, _risk_alerts).update_one({'alert_id': alert_id}, {'$set': {
        'resolved': True,
        'resolution_timestamp': dt.datetime.now(dt.timezone.utc).isoformat()
    }})
    return res.modified_count > 0  # type: ignore[no-any-return]

def insert_ai_monitoring_result(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _ai_monitoring_results is None:
        return {}
    base = dict(doc)
    base.setdefault('analysis_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _ai_monitoring_results).insert_one(base)
    return base

def get_ai_statistics(hours: int = 24) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}
    if not mongo_enabled() or _ai_monitoring_results is None or _risk_alerts is None:
        return stats
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    since_iso = since.isoformat()
    amr = cast(Any, _ai_monitoring_results)
    ra = cast(Any, _risk_alerts)
    stats['analyses_count'] = amr.count_documents({'analysis_timestamp': {'$gte': since_iso}})
    # Risk distribution of analyses
    pipeline: List[Dict[str, Any]] = [
        {'$match': {'analysis_timestamp': {'$gte': since_iso}}},
        {'$group': {'_id': '$risk_level', 'count': {'$sum': 1}}}
    ]
    risk_dist: Dict[str, int] = {}
    for row in amr.aggregate(pipeline):
        risk_dist[str(row.get('_id'))] = int(row.get('count', 0))
    stats['risk_distribution'] = risk_dist
    # Alert distribution
    alert_pipe: List[Dict[str, Any]] = [
        {'$match': {'alert_timestamp': {'$gte': since_iso}}},
        {'$group': {'_id': '$priority', 'count': {'$sum': 1}}}
    ]
    alert_dist: Dict[str, int] = {}
    for row in ra.aggregate(alert_pipe):
        alert_dist[str(row.get('_id'))] = int(row.get('count', 0))
    stats['alert_distribution'] = alert_dist
    # Average risk score & confidence
    avg_risk_cur = list(amr.aggregate([
        {'$match': {'analysis_timestamp': {'$gte': since_iso}, 'risk_score': {'$exists': True}}},
        {'$group': {'_id': None, 'avg': {'$avg': '$risk_score'}}}
    ]))
    stats['avg_risk_score'] = round(float(avg_risk_cur[0]['avg']), 3) if avg_risk_cur else 0.0
    avg_conf_cur = list(amr.aggregate([
        {'$match': {'analysis_timestamp': {'$gte': since_iso}, 'confidence': {'$exists': True}}},
        {'$group': {'_id': None, 'avg': {'$avg': '$confidence'}}}
    ]))
    stats['avg_confidence'] = round(float(avg_conf_cur[0]['avg']), 3) if avg_conf_cur else 0.0
    return stats

# ============= Incident Response (Mongo) =============

def upsert_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update an incident record."""
    if not mongo_enabled() or _incidents is None:
        return {}
    base = dict(incident)
    base.setdefault('incident_id', f"INC-{dt.datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    base.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('updated_at', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _incidents).update_one({'incident_id': base['incident_id']}, {'$set': base}, upsert=True)
    return base

def get_incident(incident_id: str) -> Optional[Dict[str, Any]]:
    if not mongo_enabled() or _incidents is None:
        return None
    return cast(Any, _incidents).find_one({'incident_id': incident_id})

def log_dispatch(update: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _dispatch_tracking is None:
        return {}
    base = dict(update)
    base.setdefault('dispatch_id', f"DSP-{dt.datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    base.setdefault('dispatch_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    base.setdefault('response_status', 'dispatched')
    cast(Any, _dispatch_tracking).insert_one(base)
    return base

def update_dispatch(dispatch_id: str, fields: Dict[str, Any]) -> bool:
    if not mongo_enabled() or _dispatch_tracking is None:
        return False
    fields = dict(fields)
    fields['updated_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    res = cast(Any, _dispatch_tracking).update_one({'dispatch_id': dispatch_id}, {'$set': fields})
    return bool(getattr(res, 'modified_count', 0))

def mark_dispatch_arrived(dispatch_id: str, arrival_location: Dict[str, Any] | None = None) -> bool:
    if not mongo_enabled() or _dispatch_tracking is None:
        return False
    update_fields: Dict[str, Any] = {
        'response_status': 'arrived',
        'actual_arrival': dt.datetime.now(dt.timezone.utc).isoformat()
    }
    if arrival_location:
        update_fields['arrival_location'] = arrival_location
    res = cast(Any, _dispatch_tracking).update_one({'dispatch_id': dispatch_id}, {'$set': update_fields})
    return bool(getattr(res, 'modified_count', 0))

def record_authority_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _authority_verifications is None:
        return {}
    base = dict(data)
    base.setdefault('verification_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _authority_verifications).insert_one(base)
    return base

def insert_incident_alert(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _incident_alerts is None:
        return {}
    base = dict(doc)
    base.setdefault('sent_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _incident_alerts).insert_one(base)
    return base

def log_response_activity(activity: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _response_activity_logs is None:
        return {}
    base = dict(activity)
    base.setdefault('activity_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _response_activity_logs).insert_one(base)
    return base

def record_emergency_contact_response(record: Dict[str, Any]) -> Dict[str, Any]:
    if not mongo_enabled() or _emergency_contact_responses is None:
        return {}
    base = dict(record)
    base.setdefault('notification_timestamp', dt.datetime.now(dt.timezone.utc).isoformat())
    cast(Any, _emergency_contact_responses).insert_one(base)
    return base

def list_incident_alerts(incident_id: str) -> List[Dict[str, Any]]:
    """Return all incident alerts for a given incident_id, ordered by sent_timestamp."""
    if not mongo_enabled() or _incident_alerts is None:
        return []
    cur = cast(Any, _incident_alerts).find({'incident_id': incident_id}).sort('sent_timestamp', 1)
    return list(cur)

def list_contact_responses(incident_id: str) -> List[Dict[str, Any]]:
    """Return all emergency contact responses for an incident_id, ordered by notification_timestamp."""
    if not mongo_enabled() or _emergency_contact_responses is None:
        return []
    cur = cast(Any, _emergency_contact_responses).find({'incident_id': incident_id}).sort('notification_timestamp', 1)
    return list(cur)

def list_dispatches(incident_id: str) -> List[Dict[str, Any]]:
    """Return all dispatch tracking records for an incident_id, ordered by dispatch_timestamp."""
    if not mongo_enabled() or _dispatch_tracking is None:
        return []
    cur = cast(Any, _dispatch_tracking).find({'incident_id': incident_id}).sort('dispatch_timestamp', 1)
    return list(cur)

def list_authority_verifications(incident_id: str) -> List[Dict[str, Any]]:
    """Return all authority verification records for an incident_id, ordered by verification_timestamp."""
    if not mongo_enabled() or _authority_verifications is None:
        return []
    cur = cast(Any, _authority_verifications).find({'incident_id': incident_id}).sort('verification_timestamp', 1)
    return list(cur)

def get_incident_response_stats(hours: int = 24) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}
    if not mongo_enabled():
        return stats
    now = dt.datetime.now(dt.timezone.utc)
    since_24 = now - dt.timedelta(hours=hours)
    since_24_iso = since_24.isoformat()
    # Alerts
    if _incident_alerts is not None:
        stats['alerts_24h'] = int(cast(Any, _incident_alerts).count_documents({'sent_timestamp': {'$gte': since_24_iso}}))
    if _authority_verifications is not None:
        stats['verifications_24h'] = int(cast(Any, _authority_verifications).count_documents({'verification_status': 'verified', 'verification_timestamp': {'$gte': since_24_iso}}))
    # Active dispatches
    if _dispatch_tracking is not None:
        stats['active_dispatches'] = int(cast(Any, _dispatch_tracking).count_documents({'response_status': {'$in': ['dispatched', 'en_route']}}))
        # Average response time (last 7 days) - compute manually
        seven_days_iso = (now - dt.timedelta(days=7)).isoformat()
        cur = cast(Any, _dispatch_tracking).find({'actual_arrival': {'$exists': True}, 'dispatch_timestamp': {'$gte': seven_days_iso}}, {'dispatch_timestamp': 1, 'actual_arrival': 1})
        durations: list[float] = []
        for d in cur:
            try:
                dt1 = dt.datetime.fromisoformat(d.get('dispatch_timestamp'))
                dt2 = dt.datetime.fromisoformat(d.get('actual_arrival'))
                durations.append((dt2 - dt1).total_seconds() / 60.0)
            except Exception:
                pass
        stats['avg_response_time_minutes'] = round(sum(durations)/len(durations), 2) if durations else 0
    if _emergency_contact_responses is not None:
        # success rate = sent / total in period
        total_resp = cast(Any, _emergency_contact_responses).count_documents({'notification_timestamp': {'$gte': since_24_iso}})
        sent_resp = cast(Any, _emergency_contact_responses).count_documents({'notification_timestamp': {'$gte': since_24_iso}, 'response_status': 'sent'})
        stats['contact_success_rate'] = round((sent_resp * 100.0 / total_resp), 2) if total_resp else 0.0
    return stats

# ============= Blockchain (Mongo replacement) =============

def _ensure_blockchain_indexes() -> None:
    if not mongo_enabled() or _blockchain_records is None:
        return
    try:
        br = cast(Any, _blockchain_records)
        br.create_index('created_at')
        br.create_index('incident_id')
        br.create_index('transaction_type')
        br.create_index('hash', unique=True)
    except Exception:
        pass

def _canonical_record_payload(record: Dict[str, Any]) -> str:
    filtered = {k: v for k, v in record.items() if k not in {'_id', 'hash', 'previous_hash'}}
    # Stable JSON encoding
    return json.dumps(filtered, sort_keys=True, separators=(',', ':'))

def _compute_hash(previous_hash: str, payload: str) -> str:
    h = hashlib.sha256()
    h.update(previous_hash.encode('utf-8'))
    h.update(payload.encode('utf-8'))
    return h.hexdigest()

def add_blockchain_record(data: Dict[str, Any]) -> Dict[str, Any]:
    """Append a blockchain-style record (hash chained) to Mongo.

    Fields automatically added:
      created_at (UTC ISO), previous_hash, hash, sequence (monotonic int)
    Caller may include: incident_id, tourist_id, transaction_type, details
    """
    if not mongo_enabled() or _blockchain_records is None:
        return {}
    _ensure_blockchain_indexes()
    br = cast(Any, _blockchain_records)
    last = br.find_one(sort=[('sequence', -1)])
    previous_hash = last.get('hash') if last else 'GENESIS'
    sequence = (int(last.get('sequence')) + 1) if last and 'sequence' in last else 0
    base = dict(data)
    base.setdefault('created_at', dt.datetime.now(dt.timezone.utc).isoformat())
    base['previous_hash'] = previous_hash
    base['sequence'] = sequence
    payload = _canonical_record_payload(base)
    base['hash'] = _compute_hash(previous_hash, payload)
    try:
        br.insert_one(base)
    except Exception:
        # Very unlikely (hash collision), just append with modified hash suffix
        base['hash'] = base['hash'] + ':1'
        try:
            br.insert_one(base)
        except Exception:
            return {}
    return base

def get_incident_blockchain_record(incident_id: str) -> List[Dict[str, Any]]:
    if not mongo_enabled() or _blockchain_records is None:
        return []
    br = cast(Any, _blockchain_records)
    cur = br.find({'incident_id': incident_id}).sort('sequence', 1)
    return list(cur)

def verify_blockchain_integrity() -> Dict[str, Any]:
    if not mongo_enabled() or _blockchain_records is None:
        return {'enabled': False, 'valid': False, 'reason': 'backend_disabled'}
    br = cast(Any, _blockchain_records)
    cur = list(br.find().sort('sequence', 1))
    mismatches: List[Dict[str, Any]] = []
    previous_hash = 'GENESIS'
    for rec in cur:
        payload = _canonical_record_payload(rec)
        expected = _compute_hash(previous_hash, payload)
        if rec.get('hash') != expected:
            mismatches.append({'sequence': rec.get('sequence'), 'stored': rec.get('hash'), 'expected': expected})
        previous_hash = rec.get('hash', '')
    return {
        'enabled': True,
        'valid': len(mismatches) == 0,
        'total_records': len(cur),
        'mismatches': mismatches
    }

def get_incident_activity_logs(incident_id: str) -> List[Dict[str, Any]]:
    if not mongo_enabled() or _response_activity_logs is None:
        return []
    ral = cast(Any, _response_activity_logs)
    cur = ral.find({'incident_id': incident_id}).sort('activity_timestamp', 1)
    return list(cur)

def get_blockchain_stats() -> Dict[str, Any]:
    if not mongo_enabled() or _blockchain_records is None:
        return {}
    br = cast(Any, _blockchain_records)
    stats: Dict[str, Any] = {}
    stats['total_blocks'] = int(br.count_documents({}))
    stats['total_incident_records'] = int(br.count_documents({'transaction_type': 'incident'}))
    # For activity logs we already have a separate collection
    if _response_activity_logs is not None:
        stats['total_activity_logs'] = int(cast(Any, _response_activity_logs).count_documents({}))
    # Basic chain validity snapshot
    integrity = verify_blockchain_integrity()
    stats['chain_valid'] = integrity.get('valid')
    stats['chain_records'] = integrity.get('total_records')
    return stats

def list_recent_blockchain_records(limit: int = 50) -> list[Dict[str, Any]]:
    """Return recent blockchain records (most recent first)."""
    if not mongo_enabled() or _blockchain_records is None:
        return []
    br = cast(Any, _blockchain_records)
    cur = br.find().sort('created_at', -1).limit(limit)
    return list(cur)

# =============== AI MONITORING FUNCTIONS ===============

def store_ai_analysis(analysis_data: Dict[str, Any]) -> bool:
    """Store AI analysis results in MongoDB"""
    global _db
    if not mongo_enabled():
        return False
    try:
        init_mongo()
        if _db is None:
            return False
        
        collection = cast(Any, _db['_ai_analysis'])
        analysis_data['created_at'] = dt.datetime.now()
        collection.insert_one(analysis_data)  # type: ignore
        return True
    except Exception as e:
        print(f"Error storing AI analysis: {e}")
        return False

# =============== AUTO SOS FUNCTIONS ===============

def store_auto_sos_evaluation(eval_data: Dict[str, Any]) -> bool:
    """Store Auto SOS evaluation results in MongoDB"""
    global _db
    if not mongo_enabled():
        return False
    try:
        init_mongo()
        if _db is None:
            return False
        
        collection = cast(Any, _db['_auto_sos_evaluations'])
        eval_data['created_at'] = dt.datetime.now()
        collection.insert_one(eval_data)  # type: ignore
        return True
    except Exception as e:
        print(f"Error storing Auto SOS evaluation: {e}")
        return False

# =============== DOCUMENT MANAGEMENT FUNCTIONS ===============

def list_user_documents(user_id: str) -> List[Dict[str, Any]]:
    """Get all documents for a user"""
    global _db
    if not mongo_enabled() or _db is None:
        return []
    try:
        collection = cast(Any, _db['_user_documents'])
        docs: List[Dict[str, Any]] = list(collection.find({'user_id': user_id}).sort('upload_date', -1))  # type: ignore
        return docs
    except Exception as e:
        print(f"Error listing user documents: {e}")
        return []

def create_document_record(doc_data: Dict[str, Any]) -> bool:
    """Create a document record in MongoDB"""
    global _db
    if not mongo_enabled() or _db is None:
        return False
    try:
        collection = cast(Any, _db['_user_documents'])
        doc_data['created_at'] = dt.datetime.now()
        collection.insert_one(doc_data)  # type: ignore
        return True
    except Exception as e:
        print(f"Error creating document record: {e}")
        return False


# =============== TOURIST DASHBOARD HELPER FUNCTIONS ===============

def update_tourist_settings(tourist_id: str, settings: Dict[str, Any]) -> bool:
    """Update tourist settings (e.g., location sharing preference)
    
    Args:
        tourist_id: Tourist ID
        settings: Dictionary of settings to update (e.g., {'location_sharing_enabled': True})
    
    Returns:
        bool: True if update successful, False otherwise
    """
    global _db
    if not mongo_enabled() or _db is None:
        return False
    
    try:
        # Try enhanced_tourists collection first
        collection = cast(Any, _db.get('enhanced_tourists'))  # type: ignore
        if collection is not None:
            result = collection.update_one(  # type: ignore
                {'tourist_id': tourist_id},
                {'$set': settings}
            )
            if result.modified_count > 0:
                return True
        
        # Fall back to tourists_basic collection
        collection = cast(Any, _db.get('tourists_basic'))  # type: ignore
        if collection is not None:
            result = collection.update_one(  # type: ignore
                {'tourist_id': tourist_id},
                {'$set': settings}
            )
            return result.modified_count > 0
        
        return False
    except Exception as e:
        print(f"Error updating tourist settings: {e}")
        return False


def get_latest_location(tourist_id: str) -> Optional[Dict[str, Any]]:
    """Get the most recent location record for a tourist
    
    Args:
        tourist_id: Tourist ID
    
    Returns:
        dict: Latest location record or None if not found
    """
    global _location_tracking
    if not mongo_enabled() or _location_tracking is None:
        return None
    
    try:
        # Find most recent location, sorted by timestamp descending
        location = _location_tracking.find_one(  # type: ignore
            {'tourist_id': tourist_id},
            sort=[('timestamp', -1)]
        )
        return location  # type: ignore
    except Exception as e:
        print(f"Error getting latest location: {e}")
        return None


def get_recent_sos_alerts(tourist_id: str, hours: int = 24) -> List[Dict[str, Any]]:
    """Get recent SOS alerts for a tourist within specified time window
    
    Args:
        tourist_id: Tourist ID
        hours: Time window in hours (default: 24)
    
    Returns:
        list: List of recent SOS alert records
    """
    global _emergency_sos
    if not mongo_enabled() or _emergency_sos is None:
        return []
    
    try:
        # Calculate time threshold
        time_threshold = dt.datetime.now() - dt.timedelta(hours=hours)
        
        # Find SOS alerts within time window
        alerts: List[Dict[str, Any]] = list(_emergency_sos.find({  # type: ignore
            'tourist_id': tourist_id,
            'timestamp': {'$gte': time_threshold}
        }).sort('timestamp', -1))
        
        return alerts
    except Exception as e:
        print(f"Error getting recent SOS alerts: {e}")
        return []


def search_tourists(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Full-text search for tourists by name, email, or tourist_id
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 5)
    
    Returns:
        list: List of matching tourist records
    """
    global _db
    if not mongo_enabled() or _db is None:
        return []
    
    try:
        # Try enhanced_tourists collection first
        collection = cast(Any, _db.get('enhanced_tourists'))  # type: ignore
        if collection is not None:
            # Case-insensitive regex search on multiple fields
            search_pattern = {'$regex': query, '$options': 'i'}
            results: List[Dict[str, Any]] = list(collection.find({  # type: ignore
                '$or': [
                    {'name': search_pattern},
                    {'email': search_pattern},
                    {'tourist_id': search_pattern}
                ]
            }).limit(limit))
            
            if results:
                return results
        
        # Fall back to tourists_basic collection
        collection = cast(Any, _db.get('tourists_basic'))  # type: ignore
        if collection is not None:
            search_pattern = {'$regex': query, '$options': 'i'}
            results = list(collection.find({  # type: ignore
                '$or': [
                    {'name': search_pattern},
                    {'email': search_pattern},
                    {'tourist_id': search_pattern}
                ]
            }).limit(limit))
            return results
        
        return []
    except Exception as e:
        print(f"Error searching tourists: {e}")
        return []


def search_sos_alerts(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Full-text search for SOS alerts by message or tourist_id
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 5)
    
    Returns:
        list: List of matching SOS alert records
    """
    global _emergency_sos
    if not mongo_enabled() or _emergency_sos is None:
        return []
    
    try:
        # Case-insensitive regex search
        search_pattern = {'$regex': query, '$options': 'i'}
        results: List[Dict[str, Any]] = list(_emergency_sos.find({  # type: ignore
            '$or': [
                {'tourist_id': search_pattern},
                {'message': search_pattern},
                {'location_description': search_pattern}
            ]
        }).sort('timestamp', -1).limit(limit))
        
        return results
    except Exception as e:
        print(f"Error searching SOS alerts: {e}")
        return []


# Export the database object for direct access by app.py
# This allows code like: from mongo_db import mongo_db; mongo_db['collection_name']
mongo_db = _db
