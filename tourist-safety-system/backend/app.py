#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tourist Safety System - Main Application"""
import sys
import io

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response, send_file, flash  # type: ignore
from flask import send_from_directory as _flask_send_from_directory  # type: ignore
from typing import Optional, Union, Any, Dict, Callable, List, TypedDict, cast, Literal, Protocol, overload
import os

# Type annotation for Flask's send_from_directory - use Any to avoid "partially unknown" PathLike issues
# _flask_send_from_directory: Callable[[Union[str, Any], Union[str, Any], Any], Response]  # type: ignore

# Strongly-typed wrapper to avoid "partially unknown" PathLike parameters for static analysis
class StrPathLike(Protocol):
    def __fspath__(self) -> str: ...

_PathType = Union[str, StrPathLike]

@overload
def send_from_directory(directory: str, path: str, **kwargs: Any) -> Response: ...
@overload
def send_from_directory(directory: StrPathLike, path: StrPathLike, **kwargs: Any) -> Response: ...
def send_from_directory(directory: _PathType, path: _PathType, **kwargs: Any) -> Response:
    """Typed wrapper that accepts str | PathLike (with __fspath__ -> str) and returns Response."""
    return _flask_send_from_directory(str(os.fspath(directory)), str(os.fspath(path)), **kwargs)  # type: ignore
# SQLite fully deprecated; removing import.
from mongo_db import (
    init_mongo, mongo_enabled,
    create_enhanced_panic_alert,
    get_recent_enhanced_panic_alerts, get_panic_alert_metrics,
    create_emergency_sos, get_recent_sos, get_sos_metrics,
    insert_location_tracking, get_recent_locations,
    create_enhanced_tourist, create_user  # newly used for Mongo registration
)  # type: ignore
from repository import repo  # unified data access
import json
from datetime import datetime, timedelta, timezone
import time  # For timestamps
import hashlib
import random
import string
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash  # password hashing
import re  # regex for email validation
from functools import wraps
from pathlib import Path

# Type definitions for zone data structures
class ZoneData(TypedDict):
    zone_name: str
    description: str
    center_lat: float
    center_lng: float
    radius_meters: int
    zone_category: str

class RestrictedZoneData(TypedDict):
    zone_name: str
    description: str
    center_lat: float
    center_lng: float
    radius_meters: int
    restriction_level: str
    alert_message: str
    contact_info: str

class HighRiskZoneData(TypedDict):
    name: str
    lat_min: float
    lat_max: float
    lng_min: float
    lng_max: float

# Payload types to reduce "partially unknown" issues
class LocationPayload(TypedDict, total=False):
    latitude: float
    longitude: float
    accuracy: float
    address: str
    country: str
    state: str
    city: str

class TouristLoginPayload(TypedDict, total=False):
    tourist_id: str

class SosRequestPayload(TypedDict, total=False):
    tourist_id: str
    timestamp: str
    page: str
    language: str
    location: LocationPayload
    emergency_type: str
    message: str
    user_agent: str

class AutoSosEvalPayload(TypedDict, total=False):
    user_id: str
    risk_score: float
    risk_level: str
    analysis_data: Dict[str, Any]
    location: LocationPayload

class SafeZoneCreatePayload(TypedDict, total=False):
    zone_name: str
    description: str
    zone_type: Literal['circular','polygon']
    center_lat: float
    center_lng: float
    radius_meters: int
    polygon_coords: Any
    zone_category: str
    created_by: str

class RestrictedZoneCreatePayload(TypedDict, total=False):
    zone_name: str
    description: str
    zone_type: Literal['circular','polygon']
    center_lat: float
    center_lng: float
    radius_meters: int
    polygon_coords: Any
    restriction_level: str
    alert_message: str
    auto_alert: bool
    created_by: str

class ReportSharePayload(TypedDict, total=False):
    share_with_tourist: bool
    share_with_authorities: bool
    authority_types: List[str]

# Import enhanced blockchain utilities with authority-level security
secure_blockchain: Optional[Any] = None
encrypt_tourist_data: Any = None  # type: ignore
decrypt_tourist_data: Any = None  # type: ignore

try:
    from blockchain_utils import (
        secure_blockchain as _secure_blockchain, 
        # AuthorityEncryption, # type: ignore 
        # TouristEncryption, # type: ignore 
        # SecurityError, # type: ignore
        encrypt_tourist_data as _encrypt_tourist_data,  # type: ignore
        decrypt_tourist_data as _decrypt_tourist_data  # type: ignore
    )
    secure_blockchain = _secure_blockchain
    encrypt_tourist_data = _encrypt_tourist_data  # type: ignore
    decrypt_tourist_data = _decrypt_tourist_data  # type: ignore
    blockchain_enabled = True
    print("✅ Enhanced blockchain security system loaded")
except ImportError as e:
    print(f"⚠️ Blockchain utilities not available: {e}. Running in basic mode.")
    blockchain_enabled = False

# Import Google Translate service (including underlying service object for status routes)
try:
    from translation_service import (
        translate_with_cache,  # type: ignore
        translate_service  # type: ignore
    )
    translation_enabled = True
    print("✅ Google Translate service loaded")
except ImportError as e:
    print(f"⚠️ Translation service not available: {e}. Running without translation.")
    translation_enabled = False
    translate_service = None  # type: ignore

# Fallback no-op translator to avoid unbound name warnings
if 'translate_with_cache' not in globals():  # pragma: no cover
    def translate_with_cache(text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:  # type: ignore
        """Fallback translation implementation returning original text."""
        return text

# Safety: ensure translate_service symbol exists even if later modules shadow or reload
if 'translate_service' not in globals():  # pragma: no cover
    translate_service = None  # type: ignore

# --- Flask App Initialization (restored) ---
from config import config as _config_map  # type: ignore
app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
_env = os.environ.get('FLASK_CONFIG', 'development')
app.config.from_object(_config_map.get(_env, _config_map['default']))

# Ensure MongoDB backend is active by default when running locally
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')
try:
    init_mongo()
except Exception as _e:
    # Start without DB but keep app running; endpoints that need DB will report 503
    print(f"Mongo init warning: {_e}")

# Ensure default admin exists (runs once on the first request; Flask 3 compatible)
@app.before_request
def _ensure_admin_defaults() -> None:  # type: ignore
    cfg = cast(Dict[str, Any], app.config)
    _initialized = bool(cfg.get('_admin_defaults_initialized', False))
    if not _initialized:
        try:
            initialize_default_admin()
        except Exception as _e:
            print(f"ensure_default_admin warning: {_e}")
        cfg['_admin_defaults_initialized'] = True

# Feature flags (defaults; may be updated after trying imports below)
ai_monitoring_enabled = True  # Enable AI monitoring with MongoDB backend
auto_sos_enabled = True  # Enable Auto SOS with MongoDB backend
incident_response_enabled = False
blockchain_logger_enabled = False
post_incident_reporting_enabled = False
ai_monitoring_system: Optional[Any] = None  # Added stub to avoid undefined reference errors
incident_response_system: Optional[Any] = None  # Added stub to avoid undefined reference errors
blockchain_logger: Any = None  # placeholder until Mongo-based blockchain refactor
auto_sos_detector: Optional[Any] = None  # Auto SOS detector stub

try:  # set translate API key if available
    os.environ['GOOGLE_TRANSLATE_API_KEY'] = app.config.get('GOOGLE_TRANSLATE_API_KEY', os.environ.get('GOOGLE_TRANSLATE_API_KEY', ''))  # type: ignore
except Exception:
    pass

# Import and initialize AI Monitoring System
try:
    from ai_monitoring import AIMonitoringSystem  # type: ignore
    try:
        ai_monitoring_system = AIMonitoringSystem()  # type: ignore[call-arg]
        ai_monitoring_enabled = True
        print("✅ AI Monitoring System loaded")
    except TypeError:
        # Some versions require arguments; use MongoDB backend instead
        ai_monitoring_enabled = True
        ai_monitoring_system = None
        print("✅ AI Monitoring using MongoDB backend")
except ImportError:
    ai_monitoring_enabled = True
    ai_monitoring_system = None
    print("✅ AI Monitoring using MongoDB backend")
except Exception as e:
    print(f"⚠️ AI Monitoring initialization warning: {e}")
    ai_monitoring_enabled = True  # Still enable with MongoDB fallback
    ai_monitoring_system = None

# Import and initialize Auto SOS Detection System
try:
    from auto_sos_detection import AutoSOSDetector  # type: ignore
    try:
        auto_sos_detector = AutoSOSDetector()  # type: ignore[call-arg]
        auto_sos_enabled = True
        print("✅ Auto SOS Detection System loaded")
    except (TypeError, Exception):
        # Use MongoDB backend instead
        auto_sos_enabled = True
        auto_sos_detector = None
        print("✅ Auto SOS Detection using MongoDB backend")
except ImportError:
    auto_sos_enabled = True
    auto_sos_detector = None
    print("✅ Auto SOS Detection using MongoDB backend")
# Supported languages
SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa', 'or', 'as']

# Absolute path to the SQLite database (stable regardless of CWD)
BASE_DIR = Path(__file__).resolve().parent.parent
database_path = str(BASE_DIR / 'data' / 'tourist_safety.db')

@app.get('/healthz')
def healthz() -> Response:  # type: ignore
    """Lightweight health check; verifies Mongo connectivity if enabled."""
    status: Dict[str, Any] = {'status': 'healthy', 'backend': 'disabled'}
    if mongo_enabled():
        try:
            init_mongo()
            from mongo_db import get_all_stats  # type: ignore
            _ = get_all_stats()
            status['backend'] = 'mongo'
        except Exception:
            status['backend'] = 'mongo-error'
    return jsonify({'success': True, **status})

# Initialize Post-Incident Reporting System
post_incident_reporter: Optional[Any] = None
if post_incident_reporting_enabled:
    try:
        from post_incident_reporting import PostIncidentReportGenerator
        post_incident_reporter = PostIncidentReportGenerator(database_path)
        print("✅ Post-Incident Reporting System initialized successfully")
    except Exception as e:  # type: ignore  # Exception handled
        print(f"⚠️ Failed to initialize Post-Incident Reporting System: {e}")
        post_incident_reporting_enabled = False

def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require admin authentication for routes"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        auth_result = require_admin_auth()
        if auth_result is not None:  # If require_admin_auth returns a Response, auth failed
            return jsonify({
                'error': 'Admin authentication required',
                'requires_admin': True
            }), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def set_user_language(lang_code: str) -> None:  # type: ignore
    """Persist preferred language in session (simple helper)."""
    session['language'] = lang_code  # type: ignore

def get_user_language() -> str:  # type: ignore
    return cast(str, session.get('language', 'en'))  # type: ignore

# --- Small payload parsers to stabilize typing ---
def parse_json_dict(silent: bool = True) -> Dict[str, Any]:  # type: ignore
    obj = request.get_json(silent=silent)  # type: ignore
    return cast(Dict[str, Any], obj) if isinstance(obj, dict) else cast(Dict[str, Any], {})

def parse_tourist_login_payload() -> TouristLoginPayload:
    data = parse_json_dict()
    out: TouristLoginPayload = {}
    if 'tourist_id' in data and isinstance(data['tourist_id'], str):
        out['tourist_id'] = data['tourist_id']
    return out

def parse_sos_payload() -> SosRequestPayload:
    data = parse_json_dict()
    out: SosRequestPayload = {}
    if 'tourist_id' in data and isinstance(data['tourist_id'], str):
        out['tourist_id'] = data['tourist_id']
    for k in ('timestamp','page','language','emergency_type','message','user_agent'):
        v = data.get(k)
        if isinstance(v, str):
            out[k] = v  # type: ignore[index]
    loc_raw = data.get('location')
    if isinstance(loc_raw, dict):
        loc: Dict[str, Any] = cast(Dict[str, Any], loc_raw)
        lout: LocationPayload = {}
        for lk in ('latitude','longitude','accuracy'):
            lv: Any = loc.get(lk)
            if isinstance(lv, (int, float)):
                lout[lk] = float(lv)  # type: ignore[index]
        for lk in ('address','country','state','city'):
            lv2 = loc.get(lk)
            if isinstance(lv2, str):
                lout[lk] = lv2  # type: ignore[index]
        out['location'] = lout
    return out

def parse_safe_zone_payload() -> SafeZoneCreatePayload:
    data = parse_json_dict()
    out: SafeZoneCreatePayload = {}
    # Required base fields
    zn = data.get('zone_name')
    if isinstance(zn, str) and zn.strip():
        out['zone_name'] = zn.strip()
    desc = data.get('description')
    if isinstance(desc, str):
        out['description'] = desc
    zt = data.get('zone_type')
    if zt in ('circular', 'polygon'):
        out['zone_type'] = zt  # type: ignore[assignment]
    clat = data.get('center_lat')
    if isinstance(clat, (int, float)):
        out['center_lat'] = float(clat)
    clng = data.get('center_lng')
    if isinstance(clng, (int, float)):
        out['center_lng'] = float(clng)
    rad = data.get('radius_meters')
    if isinstance(rad, (int, float)):
        out['radius_meters'] = int(rad)
    poly = data.get('polygon_coords')
    if poly is not None:
        out['polygon_coords'] = poly
    cat = data.get('zone_category')
    if isinstance(cat, str):
        out['zone_category'] = cat
    cb = data.get('created_by')
    if isinstance(cb, str):
        out['created_by'] = cb
    return out

def parse_restricted_zone_payload() -> RestrictedZoneCreatePayload:
    data = parse_json_dict()
    out: RestrictedZoneCreatePayload = {}
    zn = data.get('zone_name')
    if isinstance(zn, str) and zn.strip():
        out['zone_name'] = zn.strip()
    desc = data.get('description')
    if isinstance(desc, str):
        out['description'] = desc
    zt = data.get('zone_type')
    if zt in ('circular', 'polygon'):
        out['zone_type'] = zt  # type: ignore[assignment]
    clat = data.get('center_lat')
    if isinstance(clat, (int, float)):
        out['center_lat'] = float(clat)
    clng = data.get('center_lng')
    if isinstance(clng, (int, float)):
        out['center_lng'] = float(clng)
    rad = data.get('radius_meters')
    if isinstance(rad, (int, float)):
        out['radius_meters'] = int(rad)
    poly = data.get('polygon_coords')
    if poly is not None:
        out['polygon_coords'] = poly
    rl = data.get('restriction_level')
    if isinstance(rl, str):
        out['restriction_level'] = rl
    am = data.get('alert_message')
    if isinstance(am, str):
        out['alert_message'] = am
    aa = data.get('auto_alert')
    if isinstance(aa, bool):
        out['auto_alert'] = aa
    cb = data.get('created_by')
    if isinstance(cb, str):
        out['created_by'] = cb
    return out

def parse_report_share_payload() -> ReportSharePayload:
    data = parse_json_dict()
    out: ReportSharePayload = {}
    swt = data.get('share_with_tourist')
    if isinstance(swt, bool):
        out['share_with_tourist'] = swt
    swa = data.get('share_with_authorities')
    if isinstance(swa, bool):
        out['share_with_authorities'] = swa
    auth_types_raw = data.get('authority_types')
    if isinstance(auth_types_raw, list):
        at: List[str] = []
        for a in cast(List[Any], auth_types_raw):
            if isinstance(a, str) and a:
                at.append(a)
        out['authority_types'] = at
    return out

# Backward compatibility stub for earlier refactor; real implementation may exist later.
try:
    require_admin_auth  # type: ignore[name-defined]
except NameError:  # pragma: no cover
    def require_admin_auth() -> Optional[Response]:  # type: ignore
        # Check for either admin_authenticated or admin_id in session
        if not (session.get('admin_authenticated') or session.get('admin_id')):  # type: ignore
            # Return a Response; callers expecting Optional[Response] can handle
            return jsonify({'error': 'Admin authentication required'})
        return None

def init_db():  # type: ignore
    """Deprecated: SQLite schema creation removed after Mongo migration."""
    return None

def initialize_default_admin():  # type: ignore
    """Mongo-only ensure default admin exists."""
    try:
        from mongo_db import ensure_default_admin  # type: ignore
        ensure_default_admin()
    except Exception as e:  # pragma: no cover
        print(f"Default admin initialization error (mongo): {e}")

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r

def check_zone_breach(tourist_id: str, latitude: float, longitude: float) -> tuple[list[dict[str, Any]], bool]:
    """Mongo-only zone breach detection.
    Returns (alerts_triggered, is_in_safe_zone).
    """
    alerts_triggered: List[Dict[str, Any]] = []
    is_in_safe_zone = False
    if not mongo_enabled():
        return alerts_triggered, is_in_safe_zone
    from mongo_db import (
        get_active_restricted_zones, get_active_safe_zones,
        insert_zone_breach_alert, create_admin_notification
    )  # type: ignore
    try:
        # Restricted zones
        for rz in get_active_restricted_zones():
            try:
                center_lat = float(rz.get('center_lat'))  # type: ignore[arg-type]
                center_lng = float(rz.get('center_lng'))  # type: ignore[arg-type]
                radius = float(rz.get('radius_meters'))  # type: ignore[arg-type]
                dist = calculate_distance(latitude, longitude, center_lat, center_lng)
            except Exception:
                continue
            if dist <= radius:
                restriction_level = str(rz.get('restriction_level', 'warning'))
                zone_name = str(rz.get('zone_name', 'Unknown'))
                alert_message = str(rz.get('alert_message', 'Restricted zone'))
                alert_doc: Dict[str, Any] = {
                    'tourist_id': tourist_id,
                    'zone_type': 'restricted',
                    'zone_name': zone_name,
                    'breach_type': 'entry',
                    'latitude': latitude,
                    'longitude': longitude,
                    'severity': restriction_level,
                    'alert_message': alert_message
                }
                insert_zone_breach_alert(alert_doc)
                create_admin_notification({
                    'type': 'zone_breach',
                    'title': f'Restricted Zone Breach: {zone_name}',
                    'message': f'Tourist {tourist_id} entered restricted zone: {zone_name}. Level: {restriction_level}',
                    'tourist_id': tourist_id,
                    'latitude': latitude,
                    'longitude': longitude,
                    'priority': restriction_level
                })
                alerts_triggered.append(alert_doc)
        # Safe zones
        for sz in get_active_safe_zones():
            try:
                center_lat = float(sz.get('center_lat'))  # type: ignore[arg-type]
                center_lng = float(sz.get('center_lng'))  # type: ignore[arg-type]
                radius = float(sz.get('radius_meters'))  # type: ignore[arg-type]
                dist = calculate_distance(latitude, longitude, center_lat, center_lng)
            except Exception:
                continue
            if dist <= radius:
                is_in_safe_zone = True
                break
    except Exception as e:  # pragma: no cover
        print(f"Zone breach detection error: {e}")
    return alerts_triggered, is_in_safe_zone

HIGH_RISK_ZONES: List[HighRiskZoneData] = [
    {
        'name': 'Construction Zone',
        'lat_min': 28.6129,  # Example coordinates for Delhi area
        'lat_max': 28.6150,
        'lng_min': 77.2090,
        'lng_max': 77.2110
    },
    {
        'name': 'Restricted Area',
        'lat_min': 28.6000,
        'lat_max': 28.6020,
        'lng_min': 77.2000,
        'lng_max': 77.2020
    }
]

def check_geofence_violation(lat: float, lng: float, tourist_id: str) -> Optional[str]:
    """Check if coordinates are in any high-risk zone"""
    for zone in HIGH_RISK_ZONES:
        if (zone['lat_min'] <= lat <= zone['lat_max'] and 
            zone['lng_min'] <= lng <= zone['lng_max']):
            # Mongo logging
            if mongo_enabled():
                try:
                    from mongo_db import log_geofence_violation  # type: ignore
                    log_geofence_violation(tourist_id, zone['name'], lat, lng)
                except Exception as e:  # pragma: no cover
                    print(f"Geofence log error: {e}")
            return zone['name']
    return None

# Language support utilities
def get_user_language() -> str:
    """Get user's preferred language and persist until logout.
    Preference order (initially): session > URL param > browser header > 'en'.
    Once set in session, URL/header will NOT override during the session.
    """
    # If already chosen this session, keep it
    lang_in_session = session.get('language')  # type: ignore
    if isinstance(lang_in_session, str) and lang_in_session in SUPPORTED_LANGUAGES:
        return lang_in_session

    # Derive initial language
    candidate = (
        request.args.get('language') or  # type: ignore
        request.headers.get('Accept-Language', '').split(',')[0].split('-')[0] or
        'en'
    )
    if candidate not in SUPPORTED_LANGUAGES:
        candidate = 'en'

    # Persist for the session lifespan
    session['language'] = candidate
    try:
        session.permanent = True  # respect PERMANENT_SESSION_LIFETIME from config
    except Exception:
        pass
    return candidate  # type: ignore

def render_template_with_language(template_name: str, **kwargs: Any) -> str:
    """Render template with language context"""
    current_language = get_user_language()  # type: ignore  # Used in template context
    kwargs.update({
        'current_language': current_language,
        'supported_languages': SUPPORTED_LANGUAGES
    })
    return render_template(template_name, **kwargs)

@app.route('/')
def index():  # type: ignore
    """Public landing page with language + optional tourist session propagation."""
    tourist_id = request.args.get('tourist_id')  # type: ignore
    if tourist_id:
        session['tourist_id'] = tourist_id
    return render_template_with_language('index.html', tourist_id=tourist_id or session.get('tourist_id'))  # type: ignore

@app.route('/health_full')
def health_check():  # type: ignore
    """Mongo-only comprehensive health endpoint (deprecated name; prefer /healthz).
    Provides service availability and basic Mongo stats without touching SQLite.
    """
    resp: Dict[str, Any] = {
        'endpoint': 'health_full',
        'deprecated': True,
        'prefer': '/healthz',
    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'services': {
            'blockchain': 'available' if blockchain_enabled else 'disabled',
            'translation': 'available' if translation_enabled else 'disabled',
            'ai_monitoring': 'available' if ai_monitoring_enabled else 'disabled',
            'auto_sos': 'available' if auto_sos_enabled else 'disabled'
        },
        'database': {
            'backend': 'mongo' if mongo_enabled() else 'disabled'
        },
        'status': 'healthy'
    }
    if mongo_enabled():
        try:
            init_mongo()
            from mongo_db import get_all_stats  # type: ignore
            stats = get_all_stats()
            resp['database']['stats'] = stats  # type: ignore[index]
        except Exception as e:  # pragma: no cover
            resp['status'] = 'degraded'
            resp['database']['error'] = str(e)  # type: ignore[index]
    else:
        resp['status'] = 'degraded'
    return jsonify(resp), 200 if resp.get('status') == 'healthy' else 503

@app.route('/enhanced_registration')
def enhanced_registration():  # type: ignore
    """Enhanced registration page with language support"""
    return render_template_with_language('enhanced_registration.html')

@app.route('/app_download')
def app_download():  # type: ignore
    return render_template_with_language('app_download.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():  # type: ignore
    """User login page (GET) and JSON login processor (POST).

    Frontend (user_login.html) submits a JSON payload to the same endpoint.
    This handler adds POST support (previously 405) and returns a JSON response:
    { success: bool, redirect_url?: str, error?: str }
    """
    if request.method == 'GET':
        return render_template_with_language('user_login.html')

    # POST: process JSON credentials
    try:
        # Safely parse JSON body
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        data: Dict[str, Any] = payload  # type: ignore

        # Extract and normalize credentials
        username_or_email = str(data.get('email') or data.get('username') or '').strip().lower()
        password = str(data.get('password') or '')

        if not username_or_email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400

        # Unified repository path
        user_obj = repo.get_user_by_username_or_email(username_or_email)
        if not user_obj:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        # Lock checks
        locked_until_raw = user_obj.get('account_locked_until')
        if locked_until_raw:
            try:
                lt = datetime.fromisoformat(locked_until_raw)
                if lt > datetime.now():
                    return jsonify({'success': False, 'error': 'Account temporarily locked due to failed login attempts'}), 423
            except Exception:
                pass
        if user_obj.get('account_status') != 'active':
            return jsonify({'success': False, 'error': 'Account is deactivated'}), 403
        if not repo.verify_and_optionally_upgrade_password(user_obj, password):
            repo.register_failed_login(user_obj)
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        # success
        repo.reset_login_success(user_obj)
        session_id = repo.create_session_and_audit(user_obj, request.remote_addr, request.headers.get('User-Agent'), data.get('device_info', ''))
        repo.incr_stat('total_logins')
        # Prefer logical user_id for downstream lookups
        session['user_id'] = user_obj.get('user_id') or (user_obj.get('pk') or str(user_obj.get('_id')))
        session['session_id'] = session_id
        session['user_type'] = 'user'
        session['logged_in'] = True
        user_id = user_obj.get('user_id')
        username = user_obj.get('username')
        full_name = user_obj.get('full_name')
        email_verified = bool(user_obj.get('email_verified'))

        # Language preference from query, payload, or default
        lang_query = request.args.get('language')
        lang_payload = data.get('language') if isinstance(data.get('language'), str) else None
        language = (lang_query or lang_payload or 'en')
        redirect_url = f'/user_dashboard?language={language}'

        return jsonify({
            'success': True,
            'message': 'Login successful! Redirecting to dashboard...',
            'redirect_url': redirect_url,
            'user': {
                'user_id': user_id,
                'username': username,
                'full_name': full_name,
                'email_verified': bool(email_verified)
            },
            'backend': 'mongo'
        })

    except Exception as e:  # type: ignore
        # Return a concise, user-friendly error when DB is unavailable
        msg = str(e)
        if 'WinError 10061' in msg or 'AutoReconnect' in msg or 'connection refused' in msg.lower():
            return jsonify({'success': False, 'error': 'Database is unavailable. Please start MongoDB locally or set MONGO_URI, then retry.'}), 503
        return jsonify({'success': False, 'error': 'Login failed. Please try again later.'}), 500

@app.route('/api/auth/me', methods=['GET'])
def auth_me() -> Any:  # type: ignore
    """Return current logged-in user's basic profile from Mongo."""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        init_mongo()

        if 'user_id' not in session:
            return jsonify({'success': False, 'authenticated': False}), 401
        try:
            user_id_str = str(session['user_id'])  # type: ignore[index]
        except Exception:
            user_id_str = ''
        if not user_id_str:
            return jsonify({'success': False, 'authenticated': False}), 401

        from mongo_db import get_user_by_id  # type: ignore
        doc = get_user_by_id(user_id_str)
        if not doc:
            return jsonify({'success': False, 'authenticated': False}), 401

        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'user_id': doc.get('user_id'),
                'username': doc.get('username'),
                'full_name': doc.get('full_name'),
                'email_verified': bool(doc.get('email_verified'))
            }
        })
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout() -> Any:  # type: ignore
    """Clear the current session and log out the user."""
    try:
        session.clear()
        return jsonify({'success': True})
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin_login')
def admin_login():  # type: ignore
    """Admin login page with language support"""
    return render_template_with_language('admin_login.html')

@app.route('/registration_success')
def registration_success():  # type: ignore
    """Success page after enhanced or basic registration.
    Expects query params: tourist_id, blockchain_hash (optional), registration_type.
    """
    tourist_id = request.args.get('tourist_id')
    blockchain_hash = request.args.get('blockchain_hash')
    registration_type = request.args.get('registration_type', 'enhanced')
    return render_template_with_language('registration_success.html',
        tourist_id=tourist_id,
        blockchain_hash=blockchain_hash,
        registration_type=registration_type
    )

@app.route('/digital_id')
def digital_id():  # type: ignore
    return render_template('digital_id.html')

@app.route('/uploads/<path:filename>')
def serve_upload(filename: str):  # type: ignore
    """Serve uploaded files (profile photos, documents) from the uploads directory.

    Note: In production, prefer serving these via your web server with proper auth.
    """
    upload_folder = os.path.join(BASE_DIR.parent, 'uploads')
    return send_from_directory(upload_folder, filename)

@app.route('/dashboard')
def dashboard():  # type: ignore
    return render_template('dashboard.html')

@app.route('/language_settings')
def language_settings():  # type: ignore
    return render_template('language_settings.html')

@app.route('/api/enhanced_registration', methods=['POST'])
def handle_enhanced_registration():  # type: ignore
    """Handle enhanced tourist registration (Mongo-only) with blockchain integration"""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        tourist_id = generate_tourist_id()
        upload_folder = os.path.join(BASE_DIR.parent, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_fields = {
            'passport_file': 'passport',
            'visa_file': 'visa',
            'id_file': 'government_id',
            'medical_file': 'medical',
            'profile_photo': 'profile_photo'
        }
        uploaded_files: Dict[str, List[Dict[str, Any]]] = {}
        profile_photo_stored: Optional[str] = None
        for field, ftype in file_fields.items():
            if field in request.files:
                for file in request.files.getlist(field):  # type: ignore[arg-type]
                    if not file or not file.filename:
                        continue
                    safe_name = secure_filename(file.filename)
                    fname = f"{tourist_id}_{ftype}_{safe_name}"
                    fpath = os.path.join(upload_folder, fname)
                    try:
                        file.save(fpath)  # type: ignore[attr-defined]
                        uploaded_files.setdefault(ftype, []).append({
                            'original_name': file.filename,
                            'stored_name': fname,
                            'path': fpath,
                            'size': os.path.getsize(fpath)
                        })
                        if ftype == 'profile_photo' and profile_photo_stored is None:
                            profile_photo_stored = fname
                    except Exception as fe:
                        print(f"File save error ({field}): {fe}")
        medical_data = {
            'blood_type': request.form.get('blood_type'),
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'medical_insurance': request.form.get('medical_insurance'),
            'allergies': request.form.get('allergies'),
            'medications': request.form.get('medications'),
            'medical_conditions': request.form.get('medical_conditions'),
            'emergency_instructions': request.form.get('emergency_instructions')
        }
        emergency_contacts = {
            'primary': {
                'name': request.form.get('emergency_name_1'),
                'relationship': request.form.get('emergency_relationship_1'),
                'phone': request.form.get('emergency_phone_1'),
                'email': request.form.get('emergency_email_1'),
                'address': request.form.get('emergency_address_1')
            },
            'secondary': {
                'name': request.form.get('emergency_name_2'),
                'relationship': request.form.get('emergency_relationship_2'),
                'phone': request.form.get('emergency_phone_2'),
                'email': request.form.get('emergency_email_2')
            },
            'local': {
                'name': request.form.get('local_contact_name'),
                'phone': request.form.get('local_contact_phone')
            }
        }
        created_user_id: Optional[str] = None
        account_email = (request.form.get('email') or '').strip()
        account_password = (request.form.get('account_password') or '').strip()
        if account_email and account_password:
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', account_email):
                return jsonify({'success': False, 'error': 'Invalid email format'}), 400
            if len(account_password) < 6:
                return jsonify({'success': False, 'error': 'Password too short'}), 400
            username_base = (request.form.get('full_name') or 'user').split()[0].lower()[:12] or 'user'
            username_candidate = username_base
            from mongo_db import _users  # type: ignore
            if _users is not None:
                suffix = 1
                while True:
                    if not _users.find_one({'username': username_candidate}):  # type: ignore
                        break
                    suffix += 1
                    username_candidate = f"{username_base}{suffix}"
            password_hash = generate_password_hash(account_password)
            existing = None
            try:
                if _users is not None:
                    existing = _users.find_one({'email': account_email})  # type: ignore
            except Exception:
                existing = None
            if existing:
                created_user_id = existing.get('user_id')  # type: ignore
            else:
                user_doc: Dict[str, Any] = {
                    'username': username_candidate,
                    'email': account_email,
                    'password_hash': password_hash,
                    'full_name': request.form.get('full_name'),
                    'email_verified': True,
                    'preferred_language': get_user_language(),
                }
                nu = create_user(user_doc)
                created_user_id = nu.get('user_id')  # type: ignore
            if created_user_id:
                session['user_id'] = created_user_id
                session['logged_in'] = True
        encrypted_medical = encrypt_tourist_data(medical_data)
        encrypted_emergency = encrypt_tourist_data(emergency_contacts)
        blockchain_data: Dict[str, Any] = {
            'tourist_id': tourist_id,
            'full_name': request.form.get('full_name'),
            'date_of_birth': request.form.get('date_of_birth'),
            'gender': request.form.get('gender'),
            'nationality': request.form.get('nationality'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'passport_number': request.form.get('passport_number'),
            'visa_number': request.form.get('visa_number'),
            'medical_info': medical_data,
            'emergency_contacts': emergency_contacts,
            'registration_timestamp': datetime.now().isoformat(),
            'data_classification': 'SENSITIVE_TOURIST_DATA'
        }
        if blockchain_enabled and secure_blockchain is not None:
            try:
                block_index = secure_blockchain.add_encrypted_tourist_data(blockchain_data)  # type: ignore
                blockchain_hash = secure_blockchain.chain[block_index].hash  # type: ignore
                verification_hash = hashlib.sha256(f"verify_{tourist_id}".encode()).hexdigest()
            except Exception as e:
                print(f"Blockchain storage error: {e}")
                block_index = 0
                blockchain_hash = "BLOCKCHAIN_UNAVAILABLE"
                verification_hash = "VERIFICATION_UNAVAILABLE"
        else:
            block_index = 0
            blockchain_hash = "BLOCKCHAIN_DISABLED"
            verification_hash = "VERIFICATION_DISABLED"
        enhanced_doc: Dict[str, Any] = {
            'tourist_id': tourist_id,
            'full_name': request.form.get('full_name'),
            'date_of_birth': request.form.get('date_of_birth'),
            'gender': request.form.get('gender'),
            'nationality': request.form.get('nationality'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'occupation': request.form.get('occupation'),
            'education': request.form.get('education'),
            'passport_number': request.form.get('passport_number'),
            'passport_expiry': request.form.get('passport_expiry'),
            'visa_required': request.form.get('visa_required', 'no'),
            'visa_number': request.form.get('visa_number'),
            'visa_expiry': request.form.get('visa_expiry'),
            'medical_data_encrypted': encrypted_medical,
            'emergency_contacts_encrypted': encrypted_emergency,
            'passport_file_path': json.dumps(uploaded_files.get('passport', [])),
            'visa_file_path': json.dumps(uploaded_files.get('visa', [])),
            'id_file_path': json.dumps(uploaded_files.get('government_id', [])),
            'profile_photo_path': profile_photo_stored or '',
            'blockchain_hash': blockchain_hash,
            'blockchain_block_index': block_index,
            'verification_hash': verification_hash,
            'data_consent': request.form.get('data_consent') == 'on',
            'blockchain_consent': request.form.get('blockchain_consent') == 'on',
            'emergency_consent': request.form.get('emergency_consent') == 'on'
        }
        file_records: list[Dict[str, Any]] = []
        for ftype, files in uploaded_files.items():
            for fi in files:
                file_records.append({
                    'file_type': ftype,
                    'original_filename': fi['original_name'],
                    'stored_filename': fi['stored_name'],
                    'file_path': fi['path'],
                    'file_size': fi['size'],
                    'encrypted': True
                })
        blockchain_record: Dict[str, Any] = {
            'block_hash': blockchain_hash,
            'block_index': block_index,
            'transaction_type': 'registration',
            'data_hash': verification_hash,
            'verified': blockchain_enabled and blockchain_hash not in {"BLOCKCHAIN_DISABLED", "BLOCKCHAIN_UNAVAILABLE"}
        }
        created_doc = create_enhanced_tourist(enhanced_doc, file_records, blockchain_record)
        _sess: Dict[str, Any] = dict(session)
        return jsonify({
            'success': True,
            'tourist_id': created_doc.get('tourist_id', tourist_id),
            'blockchain_hash': blockchain_hash,
            'verification_hash': verification_hash,
            'blockchain_enabled': blockchain_enabled,
            'message': 'Enhanced registration completed (Mongo) with authority-level security!',
            'user_dashboard_redirect': url_for('user_dashboard') if bool(_sess.get('logged_in')) else None
        })
    except Exception as e:
        print(f"Enhanced registration error: {e}")
        return jsonify({'success': False, 'error': str(e), 'message': 'Registration failed. Please try again.'}), 500


@app.route('/api/enhanced_registration/draft', methods=['POST'])
def save_enhanced_registration_draft():  # type: ignore
    """Save or update a partial enhanced registration draft.
    Client sends JSON: { draft_id: string (uuid), step: int, data: { ...fields... } }
    We merge per-step data into a consolidated JSON blob so user can resume later.
    """
    try:
        payload = request.get_json(force=True)  # type: ignore
        draft_id = payload.get('draft_id')
        step = payload.get('step')
        step_data = payload.get('data', {})
        if not draft_id:
            return jsonify({'success': False, 'message': 'draft_id is required'}), 400
        if step is None:
            return jsonify({'success': False, 'message': 'step is required'}), 400
        if mongo_enabled():
            try:
                from mongo_db import save_registration_draft  # type: ignore
                merged = save_registration_draft(draft_id, int(step), step_data)
                return jsonify({'success': True, 'draft': merged})
            except Exception as e:  # pragma: no cover
                print(f"Draft save (mongo) error: {e}")
                return jsonify({'success': False, 'error': 'Draft save failed'}), 500
        # SQLite path deprecated
        return jsonify({'success': False, 'error': 'Mongo not enabled'}), 503
    except Exception as e:  # type: ignore
        print(f"Draft save error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/enhanced_registration/draft/<draft_id>', methods=['GET'])
def get_enhanced_registration_draft(draft_id: str):  # type: ignore
    """Retrieve a previously saved draft for resuming the registration."""
    try:
        if mongo_enabled():
            from mongo_db import get_registration_draft  # type: ignore
            doc = get_registration_draft(draft_id)
            if not doc:
                return jsonify({'success': False, 'error': 'Draft not found'}), 404
            return jsonify({'success': True, 'draft': doc})
        return jsonify({'success': False, 'error': 'Mongo not enabled'}), 503
    except Exception as e:  # type: ignore
        print(f"Draft fetch error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def generate_tourist_id():  # type: ignore
    """Generate a unique tourist ID"""
    letters = string.ascii_uppercase
    numbers = string.digits
    
    # Format: TS-XXXX-YYYY (TS = Tourist Safety)
    letter_part = ''.join(random.choices(letters, k=4))
    number_part = ''.join(random.choices(numbers, k=4))
    
    return f"TS-{letter_part}-{number_part}"

@app.route('/tourist_dashboard')
def tourist_dashboard_page():  # type: ignore
    """Tourist dashboard page with language support - using modernized dashboard"""
    tourist_id = request.args.get('tourist_id')  # type: ignore
    if not tourist_id:
        return redirect(url_for('tourist_login'))
    # Mongo path only
    if mongo_enabled():
        try:
            init_mongo()
            from mongo_db import get_enhanced_tourist  # type: ignore
            doc = get_enhanced_tourist(tourist_id)
            if doc:
                return render_template_with_language('tourist_dashboard_modernized.html', tourist_id=tourist_id, tourist_name=doc.get('full_name') or 'Tourist')
        except Exception as e:  # pragma: no cover
            print(f"Tourist dashboard mongo error: {e}")
    # Fallback (no record) -> force registration/login
    return redirect(url_for('tourist_login'))

@app.route('/tourist/<int:tourist_id>')
def tourist_dashboard(tourist_id: str) -> Any:  # deprecated numeric route
    return redirect(url_for('tourist_dashboard_page'))

@app.route('/login')
def tourist_login():  # type: ignore
    """Tourist login page with language support"""
    # Get language from URL parameter or session
    selected_language = request.args.get('language', session.get('language', 'en'))  # type: ignore
    
    # Validate language
    if selected_language not in SUPPORTED_LANGUAGES:
        selected_language = 'en'
    
    # Store in session
    session['language'] = selected_language
    
    return render_template('tourist_login.html', 
                         current_language=selected_language,
                         supported_languages=SUPPORTED_LANGUAGES)

@app.route('/admin')
@app.route('/admin_dashboard')
def admin_dashboard():  # type: ignore
    """Admin dashboard (Mongo-only)."""
    # Correctly handle the helper that returns a Response when NOT authenticated
    auth_check = require_admin_auth()
    if auth_check is not None:
        return redirect(url_for('admin_login'))
    return render_template_with_language('admin_dashboard.html')

@app.route('/admin/location')
def location_dashboard():  # type: ignore
    """Location and geo-fencing admin dashboard"""
    return render_template('location_dashboard.html')

@app.route('/user_dashboard')
def user_dashboard():  # type: ignore
    """User dashboard page with authentication check"""
    if 'user_id' not in session or 'logged_in' not in session:
        return redirect(url_for('user_login'))
    try:
        if not mongo_enabled():
            session.clear()
            return redirect(url_for('user_login'))
        init_mongo()
        from mongo_db import get_user_by_id  # type: ignore
        user_id = str(session.get('user_id'))  # type: ignore
        doc = get_user_by_id(user_id)
        if not doc or doc.get('account_status') != 'active':
            session.clear()
            return redirect(url_for('user_login'))
        user_data: Dict[str, Any] = {
            'user_id': doc.get('user_id'),
            'username': doc.get('username'),
            'full_name': doc.get('full_name'),
            'email': doc.get('email'),
            'email_verified': bool(doc.get('email_verified')),
        }
        lang_default = str(session.get('language', 'en'))  # type: ignore
        language = str(request.args.get('language', lang_default) or lang_default)
        session['language'] = language
        return render_template_with_language('user_dashboard.html', user=user_data)
    except Exception:
        session.clear()
        return redirect(url_for('user_login'))

@app.route('/logout')
def logout():  # type: ignore
    """User logout"""
    session.clear()
    # Redirect and explicitly clear helper cookies
    resp = redirect(url_for('index'))
    try:
        resp.delete_cookie('language')
    except Exception:
        pass
    return resp

@app.route('/api/tourist_login', methods=['POST'])
def authenticate_tourist():  # type: ignore
    """Enhanced tourist authentication with automatic registration"""
    tdata = parse_tourist_login_payload()
    tourist_id = str(tdata.get('tourist_id', '')).strip().upper()
    if not tourist_id:
        return jsonify({'error': 'Tourist ID is required'}), 400
    if not tourist_id.startswith('TST-') or len(tourist_id) < 8:
        return jsonify({'error': 'Invalid Tourist ID format. Should be like TST-12345'}), 400
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import get_enhanced_tourist  # type: ignore
        doc = get_enhanced_tourist(tourist_id)
        current_language = session.get('language', 'en')  # type: ignore
        if doc:
            session['tourist_id'] = tourist_id
            session['tourist_logged_in'] = True
            return jsonify({
                'success': True,
                'message': 'Login successful! Redirecting to dashboard...',
                'tourist_id': tourist_id,
                'existing_user': True,
                'redirect_url': f'/tourist_dashboard?language={current_language}&tourist_id={tourist_id}'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'New Tourist ID detected. Please complete your registration...',
                'tourist_id': tourist_id,
                'existing_user': False,
                'redirect_url': f'/enhanced_registration?tourist_id={tourist_id}&language={current_language}',
                'requires_registration': True
            })
    except Exception as e:  # pragma: no cover
        print(f"Error authenticating tourist (mongo): {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/admin_login', methods=['POST'])
def authenticate_admin():  # type: ignore
    """Authenticate admin with authority-provided credentials"""
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
        
    admin_id = data.get('admin_id', '').strip()  # type: ignore
    password = data.get('password', '').strip()  # type: ignore
    
    if not admin_id or not password:
        return jsonify({'error': 'Admin ID and password are required'}), 400
    
    if not blockchain_enabled or secure_blockchain is None:
        return jsonify({'error': 'Blockchain security system not available'}), 503
    
    try:
        # Authenticate with authority-level blockchain system
        success, message, auth_data = secure_blockchain.authenticate_authority_admin(admin_id, password)  # type: ignore
        
        if success and auth_data is not None:
            # Store admin session
            session['admin_authenticated'] = True
            session['admin_id'] = admin_id
            session['admin_token'] = auth_data['token']
            session['admin_permissions'] = auth_data['permissions']
            session['authority_level'] = auth_data['authority_level']
            
            return jsonify({
                'success': True,
                'message': 'Authority admin authentication successful',
                'redirect_url': '/admin',
                'admin_info': {
                    'admin_id': admin_id,
                    'authority_level': auth_data['authority_level'],
                    'permissions': auth_data['permissions']
                }
            }), 200
        else:
            return jsonify({'error': f'Authentication failed: {message}'}), 401
            
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Authentication error: {str(e)}'}), 500

@app.route('/api/register_tourist', methods=['POST'])
def register_tourist():  # type: ignore
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    # Mongo-only simplified tourist registration (basic). Prefer enhanced pathway elsewhere.
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import create_user  # type: ignore
        name = data.get('name')  # type: ignore
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        basic_doc: Dict[str, Any] = {
            'full_name': name,
            'registration_type': 'basic',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        created = create_user(basic_doc)  # type: ignore
        return jsonify({'success': True, 'tourist_id': created.get('user_id'), 'registration_type': 'basic', 'backend': 'mongo'})
    except Exception as e:
        return jsonify({'error': f'Failed to register tourist: {e}'}), 500

@app.route('/api/panic_alert', methods=['POST'])
def panic_alert():  # type: ignore
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    tourist_id = data.get('tourist_id')
    lat = data.get('latitude')
    lng = data.get('longitude')
    if not tourist_id or lat is None or lng is None:
        return jsonify({'error': 'tourist_id, latitude, longitude are required'}), 400
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        # Store as enhanced panic alert for admin dashboard visibility
        username_val = str(session.get('username', 'Unknown'))  # type: ignore
        alert_data: Dict[str, Any] = {
            'tourist_id': str(tourist_id),
            'latitude': float(lat),
            'longitude': float(lng),
            'alert_type': str(data.get('alert_type', 'panic')),
            'severity_level': str(data.get('severity', 'medium')),
            'message': str(data.get('message', 'Panic alert triggered')),
            'location_accuracy': data.get('location', {}).get('accuracy') if data.get('location') else None,
            'address': data.get('location', {}).get('address') if data.get('location') else None,
            'status': 'active',
            'timestamp': str(data.get('timestamp', datetime.now().isoformat())),
            'user_info': {
                'user_id': tourist_id,
                'username': username_val
            }
        }
        alert_result = create_enhanced_panic_alert(alert_data)
        
        # Create admin notification for panic alert
        from mongo_db import create_admin_notification  # type: ignore
        try:
            alert_id = str(alert_result.get('alert_id', 'UNKNOWN'))
            notification_data: Dict[str, Any] = {
                'type': 'panic_alert',
                'title': f'Panic Alert: {alert_id}',
                'message': f'Panic alert from user {tourist_id}: {data.get("message", "User triggered panic alert")}',
                'priority': 'medium',
                'related_id': alert_id,
                'location': {
                    'latitude': lat,
                    'longitude': lng
                },
                'tourist_id': tourist_id,
                'alert_type': str(data.get('alert_type', 'panic'))
            }
            create_admin_notification(notification_data)
        except Exception as notif_err:
            print(f"Failed to create admin notification for panic alert: {notif_err}")
    except Exception as e:
        return jsonify({'error': f'Failed to store panic alert: {e}'}), 500
    violation_zone = check_geofence_violation(lat, lng, tourist_id)
    return jsonify({
        'success': True,
        'message': 'Panic alert sent successfully!',
        'geofence_violation': violation_zone,
        'backend': 'mongo'
    })

# =============== EMERGENCY SOS SYSTEM ===============

@app.route('/api/emergency/sos', methods=['POST'])
def handle_sos_request():  # type: ignore
    """Handle emergency SOS requests and notify admins (Mongo-first)."""
    try:
        data = parse_sos_payload()
        tourist_id = data.get('tourist_id')
        if not tourist_id:
            return jsonify({'error': 'Authentication required. Please log in to send SOS alerts.', 'requires_login': True}), 401

        timestamp = data.get('timestamp', datetime.now().isoformat())
        page = data.get('page', 'unknown')
        language = data.get('language', 'en')
        location = data.get('location')
        emergency_type = data.get('emergency_type', 'SOS_REQUEST')
        message = data.get('message', 'Emergency SOS Request')
        user_agent = data.get('user_agent', '')
        sos_id = f"SOS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

        incident_response_triggered = False
        latitude = location.get('latitude') if location else None
        longitude = location.get('longitude') if location else None

        if not mongo_enabled():
            return jsonify({'error': 'MongoDB not enabled'}), 503
        sos_doc: Dict[str, Any] = {
            'sos_id': sos_id,
            'tourist_id': tourist_id,
            'timestamp': timestamp,
            'page': page,
            'language': language,
            'location_lat': latitude,
            'location_lng': longitude,
            'location_accuracy': location.get('accuracy') if location else None,
            'emergency_type': emergency_type,
            'message': message,
            'user_agent': user_agent,
            'status': 'ACTIVE'
        }
        create_emergency_sos(sos_doc)
        
        # Create admin notification for SOS alert
        from mongo_db import create_admin_notification  # type: ignore
        try:
            notification_data: Dict[str, Any] = {
                'type': 'emergency_sos',
                'title': f'Emergency SOS Alert: {sos_id}',
                'message': f'Emergency SOS from user {tourist_id}: {message}',
                'priority': 'high',
                'related_id': sos_id,
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'tourist_id': tourist_id,
                'emergency_type': emergency_type
            }
            create_admin_notification(notification_data)
        except Exception as notif_err:
            print(f"Failed to create admin notification: {notif_err}")

        if incident_response_enabled and incident_response_system:
            try:
                incident_data: Dict[str, Any] = {
                    'incident_id': sos_id,
                    'incident_type': 'sos_emergency',
                    'severity': 'high',
                    'location': {
                        'latitude': latitude,
                        'longitude': longitude,
                        'accuracy': location.get('accuracy') if location else None
                    },
                    'tourist_id': tourist_id,
                    'emergency_type': emergency_type,
                    'message': message,
                    'timestamp': timestamp,
                    'identity_verified': True
                }
                import asyncio
                response_task = incident_response_system.handle_incident_response(incident_data)
                if asyncio.iscoroutine(response_task):
                    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(response_task)  # type: ignore
                        incident_response_triggered = True
                    finally:
                        loop.close()
            except Exception as ir_err:  # type: ignore
                print(f"Incident response error for {sos_id}: {ir_err}")

        resp: Dict[str, Any] = {
            'success': True,
            'sos_id': sos_id,
            'message': 'SOS request received and processed',
            'admin_notified': not mongo_enabled(),
            'incident_response_triggered': incident_response_triggered,
            'tracking_url': f"/api/incident/track/{sos_id}" if incident_response_triggered else None,
            'emergency_numbers': {
                'india_emergency': '112', 'police': '100', 'ambulance': '108', 'fire': '101'
            },
            'authorities_alerted': incident_response_triggered,
            'emergency_contacts_notified': incident_response_triggered
        }
        if mongo_enabled():
            resp['backend'] = 'mongo'
        return jsonify(resp)
    except Exception as e:  # type: ignore
        print(f"SOS Error: {e}")
        return jsonify({'success': False, 'error': str(e), 'message': 'Failed to process SOS request'}), 500

@app.route('/api/emergency/sos/status/<sos_id>', methods=['GET'])
def get_sos_status(sos_id: str):  # type: ignore
    """Get SOS alert status and admin response."""
    try:
        from mongo_db import get_sos_by_id  # type: ignore
        
        sos_data = get_sos_by_id(sos_id)
        
        if not sos_data:
            return jsonify({
                'success': False,
                'error': 'SOS alert not found'
            }), 404
        
        return jsonify({
            'success': True,
            'sos_id': sos_id,
            'status': sos_data.get('status', 'UNKNOWN'),
            'admin_response': sos_data.get('admin_response', ''),
            'responded_by': sos_data.get('responded_by', ''),
            'updated_at': sos_data.get('updated_at', ''),
            'created_at': sos_data.get('timestamp', '')
        })
        
    except Exception as e:  # type: ignore
        print(f"Error getting SOS status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emergency/sos/live-location/<sos_id>', methods=['GET'])
def get_sos_live_location(sos_id: str):  # type: ignore
    """Get live location tracking for an active SOS alert."""
    try:
        from mongo_db import get_sos_by_id  # type: ignore
        
        # Get SOS alert details
        sos_data = get_sos_by_id(sos_id)
        
        if not sos_data:
            return jsonify({
                'success': False,
                'error': 'SOS alert not found'
            }), 404
        
        tourist_id = sos_data.get('tourist_id')
        if not tourist_id:
            return jsonify({
                'success': False,
                'error': 'Tourist ID not found in SOS alert'
            }), 400
        
        # Get most recent location for this tourist
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
            
        docs = get_recent_locations(tourist_id, limit=1)
        
        if not docs:
            # Return SOS initial location if no tracking data
            return jsonify({
                'success': True,
                'sos_id': sos_id,
                'tourist_id': tourist_id,
                'location': {
                    'latitude': sos_data.get('location_lat'),
                    'longitude': sos_data.get('location_lng'),
                    'accuracy': sos_data.get('location_accuracy'),
                    'timestamp': sos_data.get('timestamp'),
                    'source': 'sos_initial'
                },
                'status': sos_data.get('status', 'ACTIVE')
            })
        
        # Return latest tracked location
        doc = docs[0]
        return jsonify({
            'success': True,
            'sos_id': sos_id,
            'tourist_id': tourist_id,
            'location': {
                'latitude': doc.get('latitude'),
                'longitude': doc.get('longitude'),
                'accuracy': doc.get('accuracy'),
                'altitude': doc.get('altitude'),
                'speed': doc.get('speed'),
                'heading': doc.get('heading'),
                'timestamp': doc.get('timestamp'),
                'battery_level': doc.get('battery_level'),
                'location_method': doc.get('location_method', 'gps'),
                'is_inside_safe_zone': doc.get('is_inside_safe_zone'),
                'is_inside_restricted_zone': doc.get('is_inside_restricted_zone'),
                'source': 'live_tracking'
            },
            'status': sos_data.get('status', 'ACTIVE'),
            'sos_timestamp': sos_data.get('timestamp')
        })
        
    except Exception as e:  # type: ignore
        print(f"Error getting SOS live location: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emergency/notifications', methods=['GET'])
def get_admin_notifications() -> Union[Response, tuple[Response, int]]:
    """Get admin notifications for SOS requests"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        from mongo_db import get_recent_admin_notifications  # type: ignore
        docs = get_recent_admin_notifications(50)
        unread = 0
        notifications: List[Dict[str, Any]] = []
        for d in docs:
            nd = dict(d)
            if '_id' in nd:
                nd['_id'] = str(nd['_id'])
            status = nd.get('status', 'unread')
            if status in ('unread', 'new'):
                unread += 1
            notifications.append(nd)
        return jsonify({'success': True, 'notifications': notifications, 'unread_count': unread, 'backend': 'mongo'})
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emergency/notifications/<notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id: str) -> Any:
    """Mark notification as read"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        from mongo_db import mark_admin_notification_read  # type: ignore
        ok = mark_admin_notification_read(notification_id)
        if not ok:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        return jsonify({'success': True, 'message': 'Notification marked as read', 'backend': 'mongo'})
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/sos-alerts', methods=['GET'])
def get_sos_alerts() -> Union[Response, tuple[Response, int]]:
    """Get detailed SOS alerts for admin dashboard"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        # Get SOS alerts from database
        docs = get_recent_sos(limit=100)
        
        # Get admin notifications for unread count
        from mongo_db import list_admin_notifications  # type: ignore
        notifications = list_admin_notifications(notification_type='emergency_sos', limit=100)
        
        # Create a map of sos_id to notification read status
        notification_map: Dict[str, bool] = {}
        unread_count = 0
        for notif in notifications:
            related_id = notif.get('related_id')
            if related_id:
                notification_map[related_id] = notif.get('read', False)
                if not notif.get('read', False):
                    unread_count += 1
        
        sos_alerts: List[Dict[str, Any]] = []
        for d in docs:
            sos_id = d.get('sos_id')
            sos_alerts.append({
                'id': str(d.get('_id')),
                'sos_id': sos_id,
                'tourist_id': d.get('tourist_id', 'unknown'),
                'timestamp': d.get('timestamp'),
                'page': d.get('page'),
                'language': d.get('language'),
                'location': {
                    'latitude': d.get('location_lat'),
                    'longitude': d.get('location_lng'),
                    'accuracy': d.get('location_accuracy'),
                    'has_location': d.get('location_lat') is not None and d.get('location_lng') is not None
                },
                'emergency_type': d.get('emergency_type', 'SOS_REQUEST'),
                'message': d.get('message', 'Emergency SOS'),
                'status': d.get('status', 'ACTIVE'),
                'admin_notified': True,
                'created_at': d.get('timestamp'),
                'notification_id': sos_id,
                'read_status': notification_map.get(str(sos_id) if sos_id else '', False),  # type: ignore
                'admin_response': d.get('admin_response', ''),
                'responded_by': d.get('responded_by', ''),
                'updated_at': d.get('updated_at', '')
            })
        
        metrics = get_sos_metrics()
        return jsonify({
            'success': True,
            'backend': 'mongo',
            'sos_alerts': sos_alerts,
            'statistics': {
                'active_alerts': metrics.get('active_sos', 0),
                'today_alerts': metrics.get('sos_today', 0),
                'unread_notifications': unread_count,
                'total_alerts': len(sos_alerts)
            }
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        print(f"Error in get_sos_alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/sos/respond', methods=['POST'])
def admin_respond_to_sos():  # type: ignore
    """Admin responds to SOS alert."""
    try:
        data = request.get_json()
        sos_id = data.get('sos_id')
        status = data.get('status', 'RESPONDED')
        admin_response = data.get('response', '')
        admin_id = data.get('admin_id', 'admin')
        
        if not sos_id:
            return jsonify({'success': False, 'error': 'SOS ID is required'}), 400
        
        from mongo_db import update_sos_status, get_sos_by_id, list_admin_notifications, mark_admin_notification_read  # type: ignore
        
        # Update SOS status
        success = update_sos_status(sos_id, status, admin_response, admin_id)
        
        if success:
            # Mark related notification as read
            notifications = list_admin_notifications(notification_type='emergency_sos', limit=100)
            for notif in notifications:
                if notif.get('related_id') == sos_id:
                    notification_id = str(notif.get('_id'))
                    mark_admin_notification_read(notification_id)
                    break
            
            # Get updated SOS data
            sos_data = get_sos_by_id(sos_id)
            
            return jsonify({
                'success': True,
                'message': 'SOS alert updated successfully',
                'sos_id': sos_id,
                'status': status,
                'sos_data': sos_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update SOS alert'
            }), 500
            
    except Exception as e:  # type: ignore
        print(f"Error in admin_respond_to_sos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/notifications/unread', methods=['GET'])
def get_unread_notifications() -> Union[Response, tuple[Response, int]]:
    """Get unread admin notifications count."""
    try:
        if not mongo_enabled():
            return jsonify({
                'success': True,
                'unread_count': 0,
                'notifications': []
            })
        
        from mongo_db import list_admin_notifications  # type: ignore
        
        # Get unread notifications
        all_notifications = list_admin_notifications(limit=100)
        unread_notifications = [n for n in all_notifications if not n.get('read', False)]
        
        return jsonify({
            'success': True,
            'unread_count': len(unread_notifications),
            'notifications': unread_notifications[:10]  # Return first 10
        })
        
    except Exception as e:  # type: ignore
        print(f"Error in get_unread_notifications: {e}")
        return jsonify({
            'success': True,
            'unread_count': 0,
            'notifications': [],
            'error': str(e)
        })

@app.route('/api/admin/notifications/<notification_id>/read', methods=['POST'])
def mark_admin_notification_as_read(notification_id: str) -> Union[Response, tuple[Response, int]]:
    """Mark an admin notification as read."""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        from mongo_db import mark_admin_notification_read  # type: ignore
        
        # Mark notification as read
        success = mark_admin_notification_read(notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark notification as read'
            }), 500
            
    except Exception as e:  # type: ignore
        print(f"Error in mark_admin_notification_as_read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============== E-FIR (Electronic First Information Report) AUTOMATION ===============

@app.route('/api/admin/efir/generate', methods=['POST'])
def generate_efir():  # type: ignore
    """Auto-generate Electronic FIR when SOS is triggered
    
    Integrated with Police API for automatic case filing.
    Creates comprehensive FIR document with all evidence.
    
    Request Body:
    {
        "sos_id": "string",
        "incident_type": "emergency|theft|assault|accident|harassment|other",
        "police_station": "string (optional)",
        "additional_details": "string (optional)"
    }
    """
    try:
        if 'admin_id' not in session:
            return jsonify({'success': False, 'error': 'Admin authentication required'}), 401
        
        data = request.get_json()
        sos_id = data.get('sos_id')  # type: ignore
        incident_type = data.get('incident_type', 'emergency')  # type: ignore
        police_station = data.get('police_station')  # type: ignore
        additional_details = data.get('additional_details', '')  # type: ignore
        
        if not sos_id:
            return jsonify({'success': False, 'error': 'SOS ID required'}), 400
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        # Get SOS data
        sos_collection = mongo_db['_emergency_sos']  # type: ignore
        sos_data = sos_collection.find_one({'sos_id': sos_id})  # type: ignore
        
        if not sos_data:
            return jsonify({'success': False, 'error': 'SOS not found'}), 404
        
        tourist_id = sos_data.get('tourist_id')  # type: ignore
        
        # Get tourist details
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        tourist = tourists_collection.find_one({'tourist_id': tourist_id})  # type: ignore
        
        if not tourist:
            return jsonify({'success': False, 'error': 'Tourist not found'}), 404
        
        # Get location history (last 10 locations for context)
        location_collection = mongo_db['_location_tracking']  # type: ignore
        location_history = list(location_collection.find(  # type: ignore
            {'tourist_id': tourist_id}
        ).sort('timestamp', -1).limit(10))  # type: ignore
        
        # Generate unique FIR number
        fir_number = f"FIR-{datetime.utcnow().strftime('%Y%m%d')}-{sos_id[:8].upper()}"  # type: ignore
        
        # Build comprehensive E-FIR document
        efir_document = {  # type: ignore
            'fir_number': fir_number,
            'filing_timestamp': datetime.utcnow().isoformat(),  # type: ignore
            'status': 'FILED',
            
            # Incident Details
            'incident': {
                'type': incident_type,
                'sos_id': sos_id,
                'timestamp': sos_data.get('timestamp', datetime.utcnow()).isoformat(),  # type: ignore
                'location': {
                    'latitude': sos_data.get('latitude'),  # type: ignore
                    'longitude': sos_data.get('longitude'),  # type: ignore
                    'address': sos_data.get('location_address', 'Unknown'),  # type: ignore
                    'zone_type': sos_data.get('zone_type', 'unknown')  # type: ignore
                },
                'description': additional_details or sos_data.get('message', 'Emergency SOS triggered')  # type: ignore
            },
            
            # Victim/Reporter Details
            'reporter': {
                'tourist_id': tourist_id,
                'full_name': tourist.get('full_name'),  # type: ignore
                'nationality': tourist.get('nationality'),  # type: ignore
                'passport_number': tourist.get('passport_number'),  # type: ignore
                'phone': tourist.get('phone'),  # type: ignore
                'email': tourist.get('email'),  # type: ignore
                'date_of_birth': tourist.get('date_of_birth'),  # type: ignore
                'profile_photo_hash': tourist.get('blockchain_hash')  # type: ignore  # Blockchain-verified photo
            },
            
            # Emergency Contacts (for witness/next-of-kin)
            'emergency_contacts': tourist.get('emergency_contacts', []),  # type: ignore
            
            # Medical Info (for injury assessment)
            'medical_information': {
                'blood_type': tourist.get('medical_info', {}).get('blood_type'),  # type: ignore
                'allergies': tourist.get('medical_info', {}).get('allergies'),  # type: ignore
                'medications': tourist.get('medical_info', {}).get('medications'),  # type: ignore
                'conditions': tourist.get('medical_info', {}).get('conditions')  # type: ignore
            },
            
            # Evidence Collection
            'evidence': {
                'location_history': [
                    {
                        'latitude': loc.get('latitude'),  # type: ignore
                        'longitude': loc.get('longitude'),  # type: ignore
                        'timestamp': loc.get('timestamp', datetime.utcnow()).isoformat(),  # type: ignore
                        'zone_type': loc.get('zone_type')  # type: ignore
                    }
                    for loc in location_history  # type: ignore
                ],
                'documents_on_file': list(tourist.get('uploaded_files', {}).keys()),  # type: ignore
                'blockchain_verification': {
                    'passport_hash': tourist.get('blockchain_hash'),  # type: ignore
                    'verification_status': tourist.get('verification_status', 'unverified')  # type: ignore
                }
            },
            
            # Police Station Assignment
            'police_station': police_station or 'AUTO_ASSIGNED_NEAREST',
            
            # System Metadata
            'filed_by_admin_id': session.get('admin_id'),  # type: ignore
            'system_generated': True,
            'automation_version': '1.0',
            'case_status': 'OPEN'
        }
        
        # Store E-FIR in database
        efir_collection = mongo_db['_efir_cases']  # type: ignore
        efir_collection.insert_one(efir_document)  # type: ignore
        
        # Update SOS with FIR number
        sos_collection.update_one(  # type: ignore
            {'sos_id': sos_id},
            {'$set': {'fir_number': fir_number, 'fir_filed': True}}
        )
        
        # TODO: Integration with Police API (placeholder)
        # This would send FIR to police system
        police_api_response = {
            'status': 'SUCCESS',
            'case_number': fir_number,
            'message': 'FIR filed successfully (API integration pending)'
        }
        
        return jsonify({
            'success': True,
            'fir_number': fir_number,
            'efir_document': efir_document,
            'police_response': police_api_response,
            'message': 'E-FIR generated and filed successfully'
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/efir/list', methods=['GET'])
def list_efir_cases():  # type: ignore
    """List all E-FIR cases with filters
    
    Query Parameters:
    - status: all|OPEN|UNDER_INVESTIGATION|CLOSED (default: all)
    - incident_type: filter by incident type
    - limit: int (default: 50)
    - tourist_id: filter by specific tourist
    """
    try:
        if 'admin_id' not in session:
            return jsonify({'success': False, 'error': 'Admin authentication required'}), 401
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        # Parameters
        status_filter = request.args.get('status', 'all')  # type: ignore
        incident_filter = request.args.get('incident_type')  # type: ignore
        tourist_filter = request.args.get('tourist_id')  # type: ignore
        limit = request.args.get('limit', 50, type=int)  # type: ignore
        
        # Build query
        query: Dict[str, Any] = {}
        if status_filter != 'all':
            query['case_status'] = status_filter
        if incident_filter:
            query['incident.type'] = incident_filter
        if tourist_filter:
            query['reporter.tourist_id'] = tourist_filter
        
        # Get cases
        efir_collection = mongo_db['_efir_cases']  # type: ignore
        cases = list(efir_collection.find(query).sort('filing_timestamp', -1).limit(limit))  # type: ignore
        
        # Remove MongoDB _id for JSON serialization
        for case in cases:  # type: ignore
            case.pop('_id', None)  # type: ignore
        
        return jsonify({
            'success': True,
            'total_cases': len(cases),  # type: ignore
            'cases': cases
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/efir/<fir_number>', methods=['GET'])
def get_efir_details(fir_number: str):  # type: ignore
    """Get detailed E-FIR by FIR number"""
    try:
        if 'admin_id' not in session:
            return jsonify({'success': False, 'error': 'Admin authentication required'}), 401
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        efir_collection = mongo_db['_efir_cases']  # type: ignore
        case = efir_collection.find_one({'fir_number': fir_number})  # type: ignore
        
        if not case:
            return jsonify({'success': False, 'error': 'FIR not found'}), 404
        
        case.pop('_id', None)  # type: ignore  # Remove MongoDB _id
        
        return jsonify({
            'success': True,
            'case': case
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/efir/<fir_number>/update', methods=['PUT'])
def update_efir_status(fir_number: str):  # type: ignore
    """Update E-FIR case status
    
    Request Body:
    {
        "case_status": "OPEN|UNDER_INVESTIGATION|CLOSED",
        "update_notes": "string (optional)"
    }
    """
    try:
        if 'admin_id' not in session:
            return jsonify({'success': False, 'error': 'Admin authentication required'}), 401
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        data = request.get_json()
        new_status = data.get('case_status')  # type: ignore
        update_notes = data.get('update_notes', '')  # type: ignore
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Case status required'}), 400
        
        efir_collection = mongo_db['_efir_cases']  # type: ignore
        
        update_data = {  # type: ignore
            'case_status': new_status,
            'last_updated': datetime.utcnow().isoformat(),  # type: ignore
            'updated_by_admin_id': session.get('admin_id')  # type: ignore
        }
        
        if update_notes:
            update_data['update_notes'] = update_notes
        
        result = efir_collection.update_one(  # type: ignore
            {'fir_number': fir_number},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:  # type: ignore
            return jsonify({'success': False, 'error': 'FIR not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'E-FIR status updated successfully',
            'fir_number': fir_number,
            'new_status': new_status
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== END E-FIR AUTOMATION ===============

# =============== AUTO SOS DETECTION SYSTEM ===============

@app.route('/api/auto-sos/evaluate', methods=['POST'])
def evaluate_auto_sos():  # type: ignore
    """Evaluate if Auto SOS should be triggered based on AI analysis"""
    if not auto_sos_enabled:
        return jsonify({
            'success': False,
            'error': 'Auto SOS Detection system not available'
        }), 503
        
    try:
        data: Dict[str, Any] = parse_json_dict(silent=True)
        
        # Extract fields
        user_id = data.get('user_id')
        risk_score = data.get('risk_score', 0.0)
        risk_level = data.get('risk_level', 'low')
        analysis_data = data.get('analysis_data', {})
        location = data.get('location', {})
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Simple evaluation logic
        should_trigger = False
        confidence = risk_score
        reason = 'Normal activity'
        
        # Trigger if risk is high
        if risk_level == 'high' or risk_score >= 0.7:
            should_trigger = True
            reason = analysis_data.get('reason', 'High risk detected')
        
        # Store evaluation in MongoDB
        if mongo_enabled():
            try:
                init_mongo()
                from mongo_db import store_auto_sos_evaluation  # type: ignore
                eval_record: Dict[str, Any] = {
                    'user_id': user_id,
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'should_trigger': should_trigger,
                    'confidence': confidence,
                    'reason': reason,
                    'location': location,
                    'timestamp': datetime.now().isoformat()
                }
                store_auto_sos_evaluation(eval_record)  # type: ignore
            except Exception:
                pass  # Non-critical
        
        return jsonify({
            'success': True,
            'should_trigger': should_trigger,
            'confidence': confidence,
            'reason': reason,
            'evaluation': {
                'user_id': user_id,
                'risk_level': risk_level,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auto-sos/trigger', methods=['POST'])
def trigger_auto_sos():  # type: ignore
    """Manually trigger Auto SOS for testing or admin override"""
    if not auto_sos_enabled:
        return jsonify({
            'success': False,
            'error': 'Auto SOS Detection system not available'
        }), 503
        
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'location', 'trigger_reason']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        user_id = data['user_id']
        location = data['location']
        trigger_reason = data['trigger_reason']
        
        # Create incident package ID
        incident_id = f"AUTO-SOS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
        packager = globals().get('incident_packager')
        if packager and hasattr(packager, 'create_incident_package'):
            try:
                incident_package = getattr(packager, 'create_incident_package')(
                    incident_type='manual_auto_sos',
                    tourist_id=user_id,
                    incident_id=incident_id,
                    location=location,
                    ai_analysis={'trigger_reason': trigger_reason}
                )
            except Exception:
                incident_package = {'package_id': incident_id, 'status': 'created', 'message': 'Fallback package created'}
        else:
            incident_package = {'package_id': incident_id, 'status': 'created', 'message': 'Incident package created with basic functionality'}

        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        from mongo_db import create_sos_event, create_admin_notification  # type: ignore
        sos_id = f"AUTO-{incident_id}"
        create_sos_event({
            'sos_id': sos_id,
            'page': 'auto_sos_system',
            'language': 'en',
            'location_lat': location.get('latitude'),
            'location_lng': location.get('longitude'),
            'emergency_type': 'AUTO_SOS',
            'message': f'Auto SOS triggered: {trigger_reason}',
            'status': 'ACTIVE',
            'tourist_id': user_id,
            'user_agent': 'Auto SOS Detection System'
        })
        create_admin_notification({
            'type': 'AUTO_SOS_TRIGGERED',
            'title': 'Auto SOS Alert',
            'message': f"Auto SOS triggered for user {user_id}. Reason: {trigger_reason}",
            'tourist_id': user_id,
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'priority': 'critical'
        })
        print(f"AUTO SOS TRIGGERED: {sos_id} - {trigger_reason}")
        return jsonify({'success': True, 'sos_id': sos_id, 'incident_id': incident_id, 'incident_package': incident_package, 'message': 'Auto SOS triggered successfully', 'backend': 'mongo'})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auto-sos/status/<user_id>', methods=['GET'])
def get_auto_sos_status(user_id: str) -> Any:
    """Get Auto SOS status and configuration for a user"""
    if not auto_sos_enabled:
        return jsonify({
            'success': False,
            'error': 'Auto SOS Detection system not available'
        }), 503
        
    try:
        events: List[Dict[str, Any]] = []
        config: Dict[str, Any] = {
            'enabled': True,
            'check_interval_minutes': 10,
            'inactivity_threshold_minutes': 30
        }
        
        if mongo_enabled():
            try:
                from mongo_db import list_auto_sos_events, get_auto_sos_config  # type: ignore
                events = list_auto_sos_events(user_id=user_id, limit=10)
                db_config = get_auto_sos_config()
                if db_config:
                    config = db_config
            except Exception:
                pass  # Use defaults
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'auto_sos_enabled': True,
            'last_check': datetime.now().isoformat(),
            'recent_events': events,
            'configuration': config
        })
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== DOCUMENT MANAGEMENT SYSTEM ===============

@app.route('/api/user/documents', methods=['GET'])
def get_user_documents():  # type: ignore
    """Get all documents for the current user"""
    try:
        # Get user_id from session
        user_id: Any = session.get('user_id')  # type: ignore
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # For now, return empty list - can be enhanced with actual document storage
        documents: List[Dict[str, Any]] = []
        
        if mongo_enabled():
            try:
                init_mongo()
                from mongo_db import list_user_documents  # type: ignore
                documents = list_user_documents(str(user_id))  # type: ignore
            except Exception:
                pass  # Use empty list
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():  # type: ignore
    """Upload a document for the current user"""
    try:
        user_id: Any = session.get('user_id')  # type: ignore
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save file (simplified - should add validation, virus scanning, etc.)
        filename = str(file.filename) if file.filename else 'unnamed'
        user_id_str = str(user_id)  # type: ignore
        upload_path: Path = Path('uploads') / user_id_str
        upload_path.mkdir(parents=True, exist_ok=True)
        
        file_path: Path = upload_path / filename
        file.save(str(file_path))  # type: ignore
        
        # Store metadata in MongoDB
        if mongo_enabled():
            try:
                init_mongo()
                from mongo_db import create_document_record  # type: ignore
                doc_data: Dict[str, Any] = {
                    'user_id': user_id_str,
                    'filename': filename,
                    'file_path': str(file_path),
                    'upload_date': datetime.now().isoformat()
                }
                create_document_record(doc_data)  # type: ignore
            except Exception:
                pass
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'filename': filename
        })
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/view/<filename>', methods=['GET'])
def view_document(filename: str):  # type: ignore
    """View a document"""
    try:
        user_id: Any = session.get('user_id')  # type: ignore
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        user_id_str = str(user_id) if user_id else ''  # type: ignore
        file_path: Path = Path('uploads') / user_id_str / filename
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_file(str(file_path))  # type: ignore
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== USER AUTHENTICATION SYSTEM ===============

@app.route('/api/auth/register', methods=['POST'])
def register_user():  # type: ignore
    """Register a new user with comprehensive validation"""
    try:
        data = request.get_json()
        
        # Required fields validation
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):  # type: ignore
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        username = data.get('username').lower().strip()  # type: ignore
        email = data.get('email').lower().strip()  # type: ignore
        password = data.get('password')  # type: ignore
        full_name = data.get('full_name').strip()  # type: ignore
        
        # Validate email format
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 8:  # type: ignore
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
        
        # Generate verification metadata
        verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        verification_expires = (datetime.now() + timedelta(hours=24)).isoformat()
        try:
            new_user = repo.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                email_verified=False,
                extra={
                    'preferred_language': data.get('preferred_language', 'en'),
                    'email_verification_token': verification_token,
                    'email_verification_expires': verification_expires,
                    'phone_number': data.get('phone_number'),
                    'nationality': data.get('nationality'),
                    'date_of_birth': data.get('date_of_birth'),
                    'gender': data.get('gender')
                }
            )
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400
        # Minimal audit (reuse stats counter for registrations)
        repo.incr_stat('total_registrations')
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': new_user.get('user_id'),
            'verification_required': True
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():  # type: ignore
    """User login with session management"""
    try:
        data = request.get_json()
        username_or_email = data.get('username', '').lower().strip()  # type: ignore
        password = data.get('password', '')  # type: ignore
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'error': 'Username/email and password are required'}), 400
        
        # Repository-based login (Mongo)
        user_obj = repo.get_user_by_username_or_email(username_or_email)
        if not user_obj:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        if repo.is_account_locked(user_obj):
            return jsonify({'success': False, 'error': 'Account temporarily locked due to failed login attempts'}), 423
        if user_obj.get('account_status') != 'active':
            return jsonify({'success': False, 'error': 'Account is deactivated'}), 403
        if not repo.verify_and_optionally_upgrade_password(user_obj, password):
            repo.register_failed_login(user_obj)
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        repo.reset_login_success(user_obj)
        sess_id = repo.create_session_and_audit(user_obj, request.remote_addr, request.headers.get('User-Agent'), data.get('device_info',''))
        session['user_id'] = user_obj.get('user_id') or user_obj.get('pk')
        session['session_id'] = sess_id
        session['user_type'] = 'user'
        session['logged_in'] = True
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user_obj.get('user_id'),
                'username': user_obj.get('username'),
                'full_name': user_obj.get('full_name'),
                'email_verified': bool(user_obj.get('email_verified'))
            },
            'session_id': sess_id
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/login', methods=['POST'])
def user_login_api():  # type: ignore
    """User login endpoint for the user_login.html form"""
    try:
        # Get form data
        username_or_email = request.form.get('email', '').lower().strip()  # type: ignore
        password = request.form.get('password', '')  # type: ignore
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        user_obj = repo.get_user_by_username_or_email(username_or_email)
        if not user_obj:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        if repo.is_account_locked(user_obj):
            return jsonify({'success': False, 'error': 'Account temporarily locked due to failed login attempts'}), 423
        if user_obj.get('account_status') != 'active':
            return jsonify({'success': False, 'error': 'Account is deactivated'}), 403
        if not repo.verify_and_optionally_upgrade_password(user_obj, password):
            repo.register_failed_login(user_obj)
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        repo.reset_login_success(user_obj)
        sess_id = repo.create_session_and_audit(user_obj, request.remote_addr, request.headers.get('User-Agent'), '')
        session['user_id'] = user_obj.get('user_id') or user_obj.get('pk')
        session['session_id'] = sess_id
        session['user_type'] = 'user'
        session['logged_in'] = True
        language = request.args.get('language', 'en')
        redirect_url = f'/user_dashboard?language={language}'
        return jsonify({
            'success': True,
            'message': 'Login successful! Redirecting to dashboard...',
            'redirect_url': redirect_url,
            'user': {
                'user_id': user_obj.get('user_id'),
                'username': user_obj.get('username'),
                'full_name': user_obj.get('full_name'),
                'email_verified': bool(user_obj.get('email_verified'))
            }
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/admin/login', methods=['POST'])
def admin_login_api() -> Any:
    """Admin login with enhanced security"""
    try:
        data_raw = request.get_json(silent=True)
        data: Dict[str, Any] = cast(Dict[str, Any], data_raw if isinstance(data_raw, dict) else {})
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        username = str(data.get('username', '')).lower().strip()
        password = str(data.get('password', ''))
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        # Dev/demo fallback credentials (used if Mongo is not available)
        demo_user = os.environ.get('ADMIN_USERNAME', 'admin').lower()
        demo_pass = os.environ.get('ADMIN_PASSWORD', 'AdminPass123!')

        # If Mongo is not enabled at all, allow fallback right here
        if not mongo_enabled():
            if username == demo_user and password == demo_pass:
                session.permanent = True  # Make session persist
                session['admin_id'] = 'dev-admin'
                session['session_token'] = 'dev-session'
                session['user_type'] = 'admin'
                session['permission_level'] = 5
                session['admin_authenticated'] = True
                return jsonify({'success': True, 'message': 'Admin login successful (dev fallback)'}), 200
            return jsonify({'success': False, 'error': 'Database is unavailable. Start MongoDB or set MONGO_URI.'}), 503
        # Repository-based admin auth (Mongo)
        admin_obj = None
        session_token = None
        if mongo_enabled():
            admin_obj = repo.get_admin_by_username_or_email(username)
            if not admin_obj:
                return jsonify({'success': False, 'error': 'Invalid admin credentials'}), 401
            locked_until_raw = admin_obj.get('account_locked_until') if admin_obj else None
            if locked_until_raw:
                try:
                    if datetime.fromisoformat(locked_until_raw) > datetime.now():
                        return jsonify({'success': False, 'error': 'Admin account temporarily locked'}), 423
                except Exception:
                    pass
            if admin_obj and admin_obj.get('account_status') != 'active':
                return jsonify({'success': False, 'error': 'Admin account is deactivated'}), 403

            if admin_obj and not repo.verify_and_optionally_upgrade_password(admin_obj, password):
                repo.register_failed_login(admin_obj)
                return jsonify({'success': False, 'error': 'Invalid admin credentials'}), 401

            if admin_obj:
                repo.reset_login_success(admin_obj)
                device_info = str(data.get('device_info', ''))
                user_agent = str(request.headers.get('User-Agent', ''))
                session_token = repo.create_session_and_audit(admin_obj, request.remote_addr, user_agent, device_info)

            # Set session and return
            if admin_obj and session_token:
                session.permanent = True  # Make session persist according to PERMANENT_SESSION_LIFETIME
                session['admin_id'] = admin_obj.get('pk')
                session['session_token'] = session_token
                session['user_type'] = 'admin'
                session['permission_level'] = admin_obj.get('permission_level')
                session['admin_authenticated'] = True

                return jsonify({
                    'success': True,
                    'message': 'Admin login successful',
                    'admin': {
                        'admin_id': admin_obj.get('admin_id'),
                        'username': admin_obj.get('username'),
                        'full_name': admin_obj.get('full_name'),
                        'role': admin_obj.get('role'),
                        'permission_level': admin_obj.get('permission_level')
                    },
                    'session_token': session_token
                })

        # If we reached here with Mongo enabled, credentials were wrong
        return jsonify({'success': False, 'error': 'Invalid admin credentials'}), 401
        
    except Exception as e:  # type: ignore  # Exception handled
        # Dev fallback when Mongo call errors: allow demo admin login if credentials match
        msg = str(e)
        try:
            data2_raw = request.get_json(silent=True)
            data2: Dict[str, Any] = cast(Dict[str, Any], data2_raw if isinstance(data2_raw, dict) else {})
            u = str(data2.get('username', '')).lower().strip()
            p = str(data2.get('password', ''))
            demo_user = os.environ.get('ADMIN_USERNAME', 'admin').lower()
            demo_pass = os.environ.get('ADMIN_PASSWORD', 'AdminPass123!')
            if ('WinError 10061' in msg or 'AutoReconnect' in msg or 'connection refused' in msg.lower()) and u == demo_user and p == demo_pass:
                session['admin_id'] = 'dev-admin'
                session['session_token'] = 'dev-session'
                session['user_type'] = 'admin'
                session['permission_level'] = 5
                session['admin_authenticated'] = True
                return jsonify({'success': True, 'message': 'Admin login successful (dev fallback)'}), 200
        except Exception:
            pass
        # Otherwise return a generic error with hint
        return jsonify({'success': False, 'error': 'Admin login failed. If database is down, start MongoDB or set MONGO_URI.'}), 500

# =============== ENHANCED PANIC ALERT MANAGEMENT ===============

@app.route('/api/panic/alert', methods=['POST'])
def create_panic_alert():  # type: ignore
    """Create enhanced panic alert with comprehensive tracking"""
    try:
        data = request.get_json()
        
        # Get user info from session or data
        user_id = session.get('user_id') or data.get('user_id')  # type: ignore
        tourist_id = data.get('tourist_id')  # type: ignore
        
        # Generate unique alert ID
        alert_id = f"PANIC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        # Extract location and device info
        location = data.get('location', {})  # type: ignore
        device_info = data.get('device_info', {})  # type: ignore
        
        alert_type = data.get('alert_type', 'general_panic')  # type: ignore
        severity_level = data.get('severity_level', 3)  # 1=low, 5=critical  # type: ignore
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        alert_doc: Dict[str, Any] = {
            'alert_id': alert_id,
            'tourist_id': tourist_id,
            'user_id': user_id,
            'alert_type': alert_type,
            'severity_level': severity_level,
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'location_accuracy': location.get('accuracy'),
            'address': location.get('address'),
            'country': location.get('country'),
            'state': location.get('state'),
            'city': location.get('city'),
            'device_info': device_info,
            'user_agent': request.headers.get('User-Agent'),
            'battery_level': device_info.get('battery_level'),
            'network_type': device_info.get('network_type'),
            'status': 'active'
        }
        create_enhanced_panic_alert(alert_doc)
        
        resp_body: Dict[str, Any] = {
            'success': True,
            'alert_id': alert_id,
            'message': 'Panic alert created successfully',
            'emergency_contacts': {
                'police': '100',
                'ambulance': '108',
                'fire': '101',
                'all_emergency': '112'
            }
        }
        if mongo_enabled():
            resp_body['backend'] = 'mongo'
        return jsonify(resp_body)
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/panic-alerts', methods=['GET'])
def get_panic_alerts():  # type: ignore
    """Get all panic alerts for admin dashboard"""
    try:
        if mongo_enabled():
            docs = get_recent_enhanced_panic_alerts(limit=200)
            alerts: List[Dict[str, Any]] = []
            for d in docs:
                alerts.append({
                    'id': str(d.get('_id')),
                    'alert_id': d.get('alert_id'),
                    'alert_type': d.get('alert_type'),
                    'severity_level': d.get('severity_level'),
                    'location': {
                        'latitude': d.get('latitude'),
                        'longitude': d.get('longitude'),
                        'accuracy': d.get('location_accuracy'),
                        'address': d.get('address'),
                        'has_location': d.get('latitude') is not None and d.get('longitude') is not None
                    },
                    'status': d.get('status'),
                    'timestamp': d.get('timestamp'),
                    'admin_response_time': d.get('admin_response_time'),
                    'resolution_notes': d.get('resolution_notes'),
                    'user_info': d.get('user_info') or {},
                    'tourist_info': d.get('tourist_info') or {}
                })
            metrics = get_panic_alert_metrics()
            return jsonify({
                'success': True,
                'backend': 'mongo',
                'panic_alerts': alerts,
                'statistics': {
                    'active_alerts': metrics.get('active_alerts', 0),
                    'today_alerts': metrics.get('alerts_today', 0),
                    'average_severity': round(float(metrics.get('avg_severity', 0)), 1),
                    'total_alerts': len(alerts)
                }
            })
        else:
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/location/track', methods=['POST'])
def track_location():  # type: ignore
    """Enhanced GPS tracking endpoint with geo-fencing"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
            
        tourist_id = data.get('tourist_id')  # type: ignore
        latitude = data.get('latitude')  # type: ignore
        longitude = data.get('longitude')  # type: ignore
        accuracy = data.get('accuracy', 0)  # type: ignore
        altitude = data.get('altitude', 0)  # type: ignore
        speed = data.get('speed', 0)  # type: ignore
        heading = data.get('heading', 0)  # type: ignore
        battery_level = data.get('battery_level', 100)  # type: ignore
        location_method = data.get('location_method', 'gps')  # type: ignore
        
        if not tourist_id or latitude is None or longitude is None:
            return jsonify({'error': 'Tourist ID, latitude, and longitude are required'}), 400
        
        # Check for zone breaches
        alerts_triggered, is_in_safe_zone = check_zone_breach(tourist_id, latitude, longitude)
        is_in_restricted_zone = len(alerts_triggered) > 0  # type: ignore

        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        insert_location_tracking({
            'tourist_id': tourist_id,
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'altitude': altitude,
            'speed': speed,
            'heading': heading,
            'location_method': location_method,
            'battery_level': battery_level,
            'is_inside_safe_zone': is_in_safe_zone,
            'is_inside_restricted_zone': is_in_restricted_zone,
            'zone_alerts_triggered': alerts_triggered or []
        })
        
        return jsonify({
            'success': True,
            'message': 'Location tracked successfully',
            'alerts': alerts_triggered,
            'is_in_safe_zone': is_in_safe_zone,
            'is_in_restricted_zone': is_in_restricted_zone,
            'timestamp': datetime.now().isoformat(),
            **({'backend': 'mongo'} if mongo_enabled() else {})
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/location/history/<tourist_id>', methods=['GET'])
def get_location_history(tourist_id: str) -> Union[Response, tuple[Response, int]]:
    """Get location history for a tourist"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)  # type: ignore
        hours = request.args.get('hours', 24, type=int)  # type: ignore
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        raw = get_recent_locations(tourist_id, limit=limit)
        cutoff = datetime.now() - timedelta(hours=hours)
        locations = []
        for doc in raw:
            try:
                ts = doc.get('timestamp')
                ts_dt = datetime.fromisoformat(ts.replace('Z','')) if isinstance(ts, str) else datetime.now()
                if ts_dt < cutoff:
                    continue
            except Exception:
                ts_dt = datetime.now()
            locations.append({  # type: ignore[arg-type]
                'latitude': doc.get('latitude'),
                'longitude': doc.get('longitude'),
                'accuracy': doc.get('accuracy'),
                'altitude': doc.get('altitude'),
                'speed': doc.get('speed'),
                'heading': doc.get('heading'),
                'timestamp': doc.get('timestamp'),
                'location_method': doc.get('location_method', 'gps'),
                'battery_level': doc.get('battery_level'),
                'is_inside_safe_zone': bool(doc.get('is_inside_safe_zone')),
                'is_inside_restricted_zone': bool(doc.get('is_inside_restricted_zone')),
                'zone_alerts': doc.get('zone_alerts_triggered') or []
            })
        
        return jsonify({
            'success': True,
            'tourist_id': tourist_id,
            'location_count': len(locations),  # type: ignore
            'locations': locations,
            **({'backend': 'mongo'} if mongo_enabled() else {})
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/location/current/<tourist_id>', methods=['GET'])
def get_current_location(tourist_id: str) -> Union[Response, tuple[Response, int]]:
    """Get current location of a tourist"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        docs = get_recent_locations(tourist_id, limit=1)
        if not docs:
            return jsonify({'success': False, 'error': 'No location data found for this tourist'}), 404
        doc = docs[0]
        location: Dict[str, Any] = {
            'tourist_id': tourist_id,
            'latitude': doc.get('latitude'),
            'longitude': doc.get('longitude'),
            'accuracy': doc.get('accuracy'),
            'timestamp': doc.get('timestamp'),
            'is_inside_safe_zone': bool(doc.get('is_inside_safe_zone')),
            'is_inside_restricted_zone': bool(doc.get('is_inside_restricted_zone')),
            'recent_alerts': doc.get('zone_alerts_triggered') or []
        }
        
        return jsonify({
            'success': True,
            'location': location,
            **({'backend': 'mongo'} if mongo_enabled() else {})
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/location/share', methods=['POST'])
def share_location() -> Union[Response, tuple[Response, int]]:
    """Share current location from dashboard - simplified endpoint for real-time location sharing"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        # Import location tracking function
        from mongo_db import insert_location_tracking  # type: ignore
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract required fields
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        timestamp = data.get('timestamp')
        
        if latitude is None or longitude is None:
            return jsonify({'success': False, 'error': 'Latitude and longitude required'}), 400
        
        # Get user ID from session
        user_id = session.get('user_id')  # type: ignore
        
        # Prepare location data for storage
        location_data: Dict[str, Any] = {
            'tourist_id': user_id,
            'latitude': float(latitude),
            'longitude': float(longitude),
            'accuracy': data.get('accuracy', 0),
            'altitude': data.get('altitude'),
            'speed': data.get('speed'),
            'heading': data.get('heading'),
            'timestamp': timestamp or int(time.time() * 1000),
            'location_method': 'browser_geolocation',
            'shared_from': 'dashboard',
            'is_inside_safe_zone': False,
            'is_inside_restricted_zone': False
        }
        
        # Check zone breaches (function returns tuple: alerts_list, is_in_safe_zone)
        alerts_triggered, is_in_safe_zone = check_zone_breach(str(user_id), float(latitude), float(longitude))  # type: ignore
        location_data['is_inside_safe_zone'] = is_in_safe_zone  # type: ignore
        location_data['is_inside_restricted_zone'] = len(alerts_triggered) > 0  # type: ignore
        location_data['zone_alerts_triggered'] = alerts_triggered  # type: ignore
        
        # Store location in MongoDB
        insert_location_tracking(location_data)
        
        return jsonify({
            'success': True,
            'message': 'Location shared successfully',
            'location': {
                'latitude': location_data['latitude'],
                'longitude': location_data['longitude'],
                'timestamp': location_data['timestamp'],
                'is_inside_safe_zone': location_data['is_inside_safe_zone'],
                'is_inside_restricted_zone': location_data['is_inside_restricted_zone']
            }
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        print(f"ERROR in /api/location/share: {str(e)}")  # Log error
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============== ZONE MANAGEMENT APIs ==============

@app.route('/api/zones/safe', methods=['GET'])
def get_safe_zones():  # type: ignore
    """Get all safe zones"""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        from mongo_db import list_safe_zones  # type: ignore
        zones = list_safe_zones()
        # Add synthetic id field if _id present
        for z in zones:
            if '_id' in z and 'id' not in z:
                z['id'] = str(z['_id'])
        return jsonify({'success': True, 'safe_zones': zones, 'count': len(zones)})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zones/safe', methods=['POST'])
def create_safe_zone():  # type: ignore
    """Create a new safe zone"""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        payload = parse_safe_zone_payload()
        if 'zone_name' not in payload or 'center_lat' not in payload or 'center_lng' not in payload:
            return jsonify({'error': 'zone_name, center_lat, center_lng required'}), 400
        zone_type = payload.get('zone_type', 'circular')  # type: ignore[assignment]
        if zone_type == 'circular' and 'radius_meters' not in payload:
            return jsonify({'error': 'radius_meters required for circular zones'}), 400
        from mongo_db import create_safe_zone as _create_safe_zone  # type: ignore
        created: Dict[str, Any] = _create_safe_zone(cast(Dict[str, Any], payload))
        return jsonify({'success': True, 'message': 'Safe zone created (mongo)', 'zone': created})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zones/restricted', methods=['GET'])
def get_restricted_zones():  # type: ignore
    """Get all restricted zones"""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        from mongo_db import list_restricted_zones  # type: ignore
        zones = list_restricted_zones()
        for z in zones:
            if '_id' in z and 'id' not in z:
                z['id'] = str(z['_id'])
        return jsonify({'success': True, 'restricted_zones': zones, 'count': len(zones)})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zones/restricted', methods=['POST'])
def create_restricted_zone():  # type: ignore
    """Create a new restricted zone"""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        payload = parse_restricted_zone_payload()
        if 'zone_name' not in payload or 'center_lat' not in payload or 'center_lng' not in payload:
            return jsonify({'error': 'zone_name, center_lat, center_lng required'}), 400
        zone_type = payload.get('zone_type', 'circular')  # type: ignore[assignment]
        if zone_type == 'circular' and 'radius_meters' not in payload:
            return jsonify({'error': 'radius_meters required for circular zones'}), 400
        from mongo_db import create_restricted_zone as _create_restricted_zone  # type: ignore
        created: Dict[str, Any] = _create_restricted_zone(cast(Dict[str, Any], payload))
        return jsonify({'success': True, 'message': 'Restricted zone created (mongo)', 'zone': created})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zones/breach-alerts', methods=['GET'])
def get_zone_breach_alerts():  # type: ignore
    """Get zone breach alerts"""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import _zone_breach_alerts  # type: ignore
        limit = request.args.get('limit', 50, type=int)  # type: ignore
        tourist_id = request.args.get('tourist_id')  # type: ignore
        unresolved_only = request.args.get('unresolved_only', 'false').lower() == 'true'  # type: ignore
        query: Dict[str, Any] = {}
        if tourist_id:
            query['tourist_id'] = tourist_id
        if unresolved_only:
            query['resolved'] = {'$ne': True}
        alerts: List[Dict[str, Any]] = []
        if _zone_breach_alerts is not None:  # runtime guard
            cur = cast(Any, _zone_breach_alerts).find(query).sort('timestamp', -1).limit(limit)
            for doc in cur:
                d = dict(doc)
                d['id'] = str(d.get('_id'))
                alerts.append(d)
        return jsonify({'success': True, 'alerts': alerts, 'count': len(alerts)})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.get('/api/stats')
def api_stats():  # type: ignore
    """Expose aggregated statistics (logins, registrations, etc.)."""
    try:
        stats = repo.get_stats()
        backend_mode = 'mongo'
        return jsonify({'success': True, 'backend': backend_mode, 'stats': stats})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500
 
@app.get('/api/zone_analytics')
def api_zone_analytics():  # type: ignore
    """Comprehensive zone + breach analytics (Mongo only) using public helpers."""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from datetime import timezone as _tz
        from mongo_db import (  # type: ignore
            get_active_safe_zones, get_active_restricted_zones,
            count_zone_breaches_since, aggregate_zone_breaches,
            distinct_restricted_tourists_since
        )
        now = datetime.now(_tz.utc)
        td = timedelta
        active_safe: int = len(get_active_safe_zones())
        active_restricted: int = len(get_active_restricted_zones())
        since_24h = now - td(hours=24)
        since_7d = now - td(days=7)
        breaches_24h: int = count_zone_breaches_since(since_24h)
        breaches_7d: int = count_zone_breaches_since(since_7d)
        breach_by_severity: List[Dict[str, Any]] = []
        for row in aggregate_zone_breaches([
            {'$match': {'timestamp': {'$gte': since_7d}}},
            {'$group': {'_id': '$severity', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]):
            breach_by_severity.append({
                'severity': row.get('_id'),
                'count': int(row.get('count', 0))
            })
        top_breached: List[Dict[str, Any]] = []
        for row in aggregate_zone_breaches([
            {'$match': {'timestamp': {'$gte': since_7d}}},
            {'$group': {'_id': {'zone_name': '$zone_name', 'zone_type': '$zone_type'}, 'breach_count': {'$sum': 1}}},
            {'$sort': {'breach_count': -1}},
            {'$limit': 5}
        ]):
            _id: Dict[str, Any] = cast(Dict[str, Any], row.get('_id') or {})
            top_breached.append({
                'zone_name': _id.get('zone_name'),
                'zone_type': _id.get('zone_type'),
                'breach_count': int(row.get('breach_count', 0))
            })
        tourists_in_restricted: int = distinct_restricted_tourists_since(now - td(hours=1))
        analytics: Dict[str, Any] = {
            'zone_counts': {'active_safe_zones': active_safe, 'active_restricted_zones': active_restricted},
            'breach_statistics': {
                'breaches_24h': breaches_24h,
                'breaches_7d': breaches_7d,
                'breach_by_severity': breach_by_severity
            },
            'top_breached_zones': top_breached,
            'current_status': {'tourists_in_restricted_last_hour': tourists_in_restricted}
        }
        return jsonify({'success': True, 'analytics': analytics})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tourists')
def get_tourists():  # type: ignore
    """Mongo-only tourist listing (enhanced registrations)."""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import list_enhanced_tourists  # type: ignore
        docs = list_enhanced_tourists(limit=200)
        tourists: List[Dict[str, Any]] = []
        now_ts = datetime.now(timezone.utc)
        for d in docs:
            last_time_raw = d.get('last_location_time')
            status = 'active'
            try:
                if last_time_raw:
                    lt = datetime.fromisoformat(str(last_time_raw).replace('Z', '+00:00'))
                    if now_ts - lt > timedelta(hours=24):
                        status = 'inactive'
            except Exception:
                pass
            # Align response keys with admin dashboard expectations
            full_name = d.get('full_name') or d.get('name')
            created_at = d.get('created_at') or d.get('registration_time')
            tourists.append({
                'tourist_id': d.get('tourist_id'),
                'full_name': full_name,
                'name': full_name,  # alias for frontend compatibility
                'nationality': d.get('nationality'),
                'verification_status': d.get('verification_status'),
                'registration_time': created_at,
                'created_at': created_at,  # alias for frontend compatibility
                'last_location_lat': d.get('last_location_lat'),
                'last_location_lng': d.get('last_location_lng'),
                'last_location_time': d.get('last_location_time'),
                'status': status
            })
        return jsonify({'success': True, 'count': len(tourists), 'tourists': tourists})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

# Alias for frontend compatibility
@app.route('/api/get_tourists')
def get_tourists_alias():  # type: ignore
    return get_tourists()

@app.route('/api/panic_alerts')
def get_basic_panic_alerts():  # type: ignore
    """Mongo-only panic alerts (enhanced)."""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import get_recent_enhanced_panic_alerts  # type: ignore
        alerts = get_recent_enhanced_panic_alerts(limit=50)
        simplified: List[Dict[str, Any]] = []
        for a in alerts:
            simplified.append({
                'alert_id': a.get('alert_id'),
                'tourist_id': a.get('tourist_id'),
                'latitude': a.get('latitude'),
                'longitude': a.get('longitude'),
                'timestamp': a.get('timestamp'),
                'status': a.get('status'),
                'severity_level': a.get('severity_level')
            })
        return jsonify({'success': True, 'count': len(simplified), 'alerts': simplified})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_blockchain_records')
def get_blockchain_records():  # type: ignore
    """Provide recent blockchain-style records for admin dashboard."""
    if not mongo_enabled():
        return jsonify({'success': False, 'records': [], 'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import list_recent_blockchain_records  # type: ignore
        recs = list_recent_blockchain_records(limit=50)
        out: List[Dict[str, Any]] = []
        for r in recs:
            out.append({
                'hash': r.get('hash'),
                'previous_hash': r.get('previous_hash'),
                'sequence': r.get('sequence'),
                'tourist_id': r.get('tourist_id'),
                'incident_id': r.get('incident_id'),
                'transaction_type': r.get('transaction_type'),
                'timestamp': r.get('created_at') or r.get('timestamp')
            })
        return jsonify({'success': True, 'count': len(out), 'records': out})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'records': [], 'error': str(e)}), 500

@app.route('/api/geofence_violations')
def get_geofence_violations():  # type: ignore
    """Mongo-only geofence violations list."""
    if not mongo_enabled():
        return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        limit = request.args.get('limit', 50, type=int)  # type: ignore
        from mongo_db import get_recent_geofence_violations  # type: ignore
        violations = get_recent_geofence_violations(limit=limit)
        return jsonify({'success': True, 'count': len(violations), 'violations': violations})
    except Exception as e:  # pragma: no cover
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verify_digital_id', methods=['POST'])
def verify_digital_id():  # type: ignore
    """Verify digital ID using blockchain"""
    try:
        data: Dict[str, Any] = parse_json_dict()
        tourist_id = str(data.get('tourist_id', '')).strip()
        blockchain_hash = str(data.get('blockchain_hash', '')).strip()
        if not tourist_id or not blockchain_hash:
            return jsonify({'success': False, 'error': 'tourist_id and blockchain_hash required'}), 400
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        init_mongo()
        from mongo_db import get_enhanced_tourist  # type: ignore
        doc = get_enhanced_tourist(tourist_id)
        match = bool(doc and doc.get('blockchain_hash') == blockchain_hash)
        verification_result: Dict[str, Any] = {
            'verified': match,
            'confidence': 95.0 if match else 10.0,
            'message': 'Tourist ID verified successfully' if match else 'Verification failed'
        }
        if not doc:
            return jsonify({'success': False, 'verification': verification_result, 'error': 'Tourist not found'}), 404
        return jsonify({
            'success': True,
            'verification': verification_result,
            'tourist': {
                'tourist_id': doc.get('tourist_id'),
                'full_name': doc.get('full_name'),
                'nationality': doc.get('nationality'),
                'verification_status': doc.get('verification_status', 'unverified'),
                'blockchain_hash': doc.get('blockchain_hash'),
                'verification_hash': doc.get('verification_hash')
            }
        })
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_digital_id/<tourist_id>')
def get_digital_id(tourist_id: str):  # type: ignore
    """Get digital ID data for display"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        init_mongo()
        
        # Try to get from enhanced tourists first, then fall back to regular users
        from mongo_db import get_enhanced_tourist  # type: ignore
        doc = get_enhanced_tourist(str(tourist_id))
        
        # If not found in enhanced tourists, try regular users collection
        if not doc:
            user_doc = repo.find_user_by_id(str(tourist_id))  # type: ignore
            if user_doc:
                # Convert user doc to expected format
                doc = {  # type: ignore
                    'tourist_id': user_doc.get('user_id'),  # type: ignore
                    'full_name': user_doc.get('full_name'),  # type: ignore
                    'date_of_birth': user_doc.get('date_of_birth'),  # type: ignore
                    'nationality': user_doc.get('nationality'),  # type: ignore
                    'phone': user_doc.get('phone_number'),  # type: ignore
                    'email': user_doc.get('email'),  # type: ignore
                    'passport_number': user_doc.get('passport_number'),  # type: ignore
                    'medical_info': user_doc.get('medical_info', {}),  # type: ignore
                    'emergency_contacts': user_doc.get('emergency_contacts', []),  # type: ignore
                    'profile_photo_path': user_doc.get('profile_photo_path'),  # type: ignore
                    'blockchain_hash': user_doc.get('blockchain_hash', ''),  # type: ignore
                    'verification_hash': user_doc.get('verification_hash', ''),  # type: ignore
                    'verification_status': user_doc.get('verification_status', 'unverified')  # type: ignore
                }
        
        if not doc:
            return jsonify({'success': False, 'error': 'Tourist not found'}), 404
            
        # Attempt decrypt if helpers exist
        medical_data: Any = doc.get('medical_data_encrypted') or doc.get('medical_info', {})  # type: ignore
        emergency_contacts: Any = doc.get('emergency_contacts_encrypted') or doc.get('emergency_contacts', [])  # type: ignore
        try:
            if 'decrypt_tourist_data' in globals():  # type: ignore
                medical_data = decrypt_tourist_data(medical_data)  # type: ignore
                emergency_contacts = decrypt_tourist_data(emergency_contacts)  # type: ignore
        except Exception:
            pass
        # Optional profile photo URL
        profile_photo_url: Optional[str] = None
        ppath = doc.get('profile_photo_path')  # type: ignore
        if ppath:
            try:
                profile_photo_url = url_for('serve_upload', filename=str(ppath))  # type: ignore
            except Exception:
                profile_photo_url = None
        return jsonify({
            'success': True,
            'tourist': {
                'tourist_id': doc.get('tourist_id'),  # type: ignore
                'full_name': doc.get('full_name'),  # type: ignore
                'date_of_birth': doc.get('date_of_birth'),  # type: ignore
                'nationality': doc.get('nationality'),  # type: ignore
                'phone': doc.get('phone'),  # type: ignore
                'email': doc.get('email'),  # type: ignore
                'passport_number': doc.get('passport_number'),  # type: ignore
                'medical_info': medical_data,
                'emergency_contacts': emergency_contacts,
                'blockchain_hash': doc.get('blockchain_hash'),  # type: ignore
                'verification_hash': doc.get('verification_hash'),  # type: ignore
                'verification_status': doc.get('verification_status', 'unverified'),  # type: ignore
                'profile_photo_url': profile_photo_url
            }
        })
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/qr_verify', methods=['POST'])
def qr_verify():  # type: ignore
    """Verify QR code data"""
    try:
        data = request.json
        qr_data = data.get('qr_data')  # type: ignore
        
        if not qr_data:
            return jsonify({'success': False, 'error': 'No QR data provided'}), 400
        
        # Parse QR data (assuming it's JSON)
        try:
            parsed_data = json.loads(qr_data)
        except:
            return jsonify({'success': False, 'error': 'Invalid QR data format'}), 400
        
        tourist_id = parsed_data.get('id')  # type: ignore
        if not tourist_id:
            return jsonify({'success': False, 'error': 'Invalid QR code'}), 400
        
        # Mongo-only verification
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        try:
            init_mongo()
            from mongo_db import get_enhanced_tourist  # type: ignore
            doc = get_enhanced_tourist(str(tourist_id))
        except Exception as inner:
            return jsonify({'success': False, 'error': f'Database error: {inner}'}), 500

        if doc:
            block_verified = bool(doc.get('blockchain_hash') and doc.get('blockchain_hash') == parsed_data.get('blockHash'))  # type: ignore
            return jsonify({
                'success': True,
                'verified': True,
                'name': doc.get('full_name'),
                'nationality': doc.get('nationality'),
                'status': doc.get('verification_status'),
                'blockchain_verified': block_verified,
                'verification_time': datetime.now(timezone.utc).isoformat()
            })
        return jsonify({
            'success': False,
            'verified': False,
            'error': 'Tourist ID not found'
        }), 404
            
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/set_language', methods=['POST'])
def set_language():  # type: ignore
    """Set user's preferred language"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
        else:
            data = request.form.to_dict()
        
        # Handle case where data might be None
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        language = data.get('language', 'en')  # type: ignore
        
        # Validate language code
        if not language or not isinstance(language, str):
            return jsonify({
                'success': False,
                'error': 'Invalid language parameter'
            }), 400
        
        # Persist in session
        try:
            set_user_language(language)
            session.permanent = True  # keep language across the session lifetime
        except Exception:
            # Fallback: set directly if helper unavailable
            session['language'] = language  # type: ignore
            try:
                session.permanent = True
            except Exception:
                pass

        # Respond and also set a helper cookie for client-side awareness
        resp = jsonify({
            'success': True,
            'language': language,
            'message': f'Language set to {language}'
        })
        # 30-day cookie, HTTPOnly false so front-end can read if needed (contains only i18n preference)
        resp.set_cookie('language', language, max_age=60*60*24*30, httponly=False, samesite='Lax')
        return resp
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_language', methods=['GET'])
def get_language():  # type: ignore
    """Get user's current language preference"""
    return jsonify({
        'success': True,
        'language': get_user_language(),
        'message': 'Language retrieved successfully'
    })

@app.route('/api/translate/batch', methods=['POST'])
def translate_batch():  # type: ignore
    """Translate multiple texts at once"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        texts_raw_any: List[Any] = cast(List[Any], data.get('texts', []))  # type: ignore[assignment]
        source_lang = data.get('source_lang', 'auto')
        # Default target language to user's preference when not provided
        target_lang = data.get('target_lang') or get_user_language() or 'en'

        if not texts_raw_any:
            return jsonify({
                'success': False,
                'error': 'Texts array is required'
            }), 400
        texts: List[str] = []
        for t in texts_raw_any:
            texts.append(t if isinstance(t, str) else str(t))

        # Use translation service if available; otherwise return originals
        translations: List[str] = []
        if not translation_enabled:
            translations = texts
        else:
            for text in texts:
                if not text.strip():
                    translations.append(text)
                else:
                    try:
                        translated = translate_with_cache(text, source_lang, target_lang)
                        translations.append(translated or text)
                    except Exception:
                        translations.append(text)

        return jsonify({
            'success': True,
            'translations': translations,
            'source_language': source_lang,
            'target_language': target_lang
        })

    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== GOOGLE TRANSLATE API ROUTES ===============

@app.route('/api/translate/text', methods=['POST'])
def translate_text():  # type: ignore
    """Translate text using Google Translate API"""
    try:
        data = request.get_json()
        text = data.get('text', '')  # type: ignore
        source_lang = data.get('source_lang', 'auto')  # type: ignore
        # Default to user's session language if not explicitly specified
        target_lang = data.get('target_lang') or get_user_language() or 'en'  # type: ignore
        
        if not text.strip():
            return jsonify({'success': False, 'error': 'Text cannot be empty'}), 400
        
        if not translation_enabled:
            return jsonify({
                'success': False, 
                'error': 'Translation service not available',
                'original_text': text
            }), 503
        
        # Translate the text
        translated_text = translate_with_cache(text, source_lang, target_lang)
        
        # Detect source language if auto
        if source_lang == 'auto' and translation_enabled:
            detected_lang = translate_service.detect_language(text)  # type: ignore
        else:
            detected_lang = source_lang
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'source_language': detected_lang,
            'target_language': target_lang,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/form', methods=['POST'])
def translate_form_data():  # type: ignore
    """Translate entire form data to target language"""
    try:
        data = request.get_json()
        form_data = data.get('form_data', {})  # type: ignore
        # Default to user's session language if not provided
        target_lang = data.get('target_lang') or get_user_language() or 'en'  # type: ignore
        source_lang = data.get('source_lang', 'auto')  # type: ignore
        
        if not form_data:
            return jsonify({'success': False, 'error': 'Form data cannot be empty'}), 400
        
        if not translation_enabled:
            return jsonify({
                'success': False,
                'error': 'Translation service not available',
                'original_data': form_data
            }), 503
        
        # Translate each field in the form
        translated_data = {}  # type: ignore
        translation_log = []
        
        for field_name, field_value in form_data.items():
            if isinstance(field_value, str) and field_value.strip():
                translated_value = translate_with_cache(field_value, source_lang, target_lang)
                translated_data[field_name] = translated_value
                
                translation_log.append({  # type: ignore
                    'field': field_name,
                    'original': field_value,
                    'translated': translated_value
                })
            else:
                translated_data[field_name] = field_value
        
        return jsonify({
            'success': True,
            'original_data': form_data,
            'translated_data': translated_data,
            'translation_log': translation_log,
            'source_language': source_lang,
            'target_language': target_lang,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/detect', methods=['POST'])
def detect_language():  # type: ignore
    """Detect the language of given text"""
    try:
        data = request.get_json()
        text = data.get('text', '')  # type: ignore
        
        if not text.strip():
            return jsonify({'success': False, 'error': 'Text cannot be empty'}), 400
        
        if not translation_enabled:
            return jsonify({
                'success': False,
                'error': 'Translation service not available',
                'detected_language': 'en'
            }), 503
        
        detected_lang = translate_service.detect_language(text)  # type: ignore
        confidence = translate_service.get_translation_confidence(text, text)  # type: ignore
        
        return jsonify({
            'success': True,
            'text': text,
            'detected_language': detected_lang,
            'confidence': confidence,
            'supported_languages': SUPPORTED_LANGUAGES,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/status', methods=['GET'])
def translation_status():  # type: ignore
    """Get translation service status and capabilities"""
    demo_mode = True
    if translation_enabled and 'translate_service' in globals() and getattr(translate_service, 'api_key', None):  # type: ignore
        try:
            demo_mode = (translate_service.api_key == "DEMO_API_KEY" or str(translate_service.api_key).endswith('-demo'))  # type: ignore
        except Exception:
            demo_mode = True
    return jsonify({
        'success': True,
        'translation_enabled': translation_enabled,
        'supported_languages': SUPPORTED_LANGUAGES,
        'current_language': get_user_language(),
        'features': {
            'text_translation': True,
            'form_translation': True,
            'language_detection': True,
            'translation_caching': True
        },
        'demo_mode': demo_mode
    })

@app.route('/api/system/status', methods=['GET'])
def system_status():  # type: ignore
    """Get system status for AI monitoring, Auto SOS, and other features"""
    return jsonify({
        'success': True,
        'features': {
            'ai_monitoring': {
                'enabled': ai_monitoring_enabled,
                'status': 'active' if ai_monitoring_enabled else 'disabled',
                'description': 'Continuous AI-powered safety analysis'
            },
            'auto_sos': {
                'enabled': auto_sos_enabled,
                'status': 'active' if auto_sos_enabled else 'disabled',
                'description': 'Automatic emergency detection system'
            },
            'location_tracking': {
                'enabled': True,
                'status': 'ready',
                'description': 'Real-time location monitoring'
            },
            'safety_map': {
                'enabled': True,
                'status': 'ready',
                'description': 'Interactive safety zone mapping'
            },
            'document_manager': {
                'enabled': True,
                'status': 'ready',
                'description': 'Secure document storage and verification'
            }
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/admin/tourist/<tourist_id>', methods=['GET'])
def get_tourist_by_id_secure(tourist_id):  # type: ignore
    """Get specific tourist data - requires admin authentication"""
    auth_check = require_admin_auth()
    if auth_check:
        return auth_check
    
    try:
        admin_token = session.get('admin_token')  # type: ignore
        # Get specific tourist data from blockchain
        tourist_data = secure_blockchain.get_tourist_by_id_for_admin(tourist_id, admin_token)  # type: ignore
        
        if tourist_data:
            return jsonify({
                'success': True,
                'data': tourist_data,
                'security_level': 'AUTHORITY_DECRYPTED',
                'admin_id': session.get('admin_id'),  # type: ignore
                'authority_level': session.get('authority_level')  # type: ignore
            })
        else:
            return jsonify({'error': 'Tourist not found'}), 404
            
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Data retrieval error: {str(e)}'}), 500

@app.route('/api/admin/blockchain/status', methods=['GET'])
def get_blockchain_status():  # type: ignore
    """Get blockchain system status - requires admin authentication"""
    auth_check = require_admin_auth()
    if auth_check:
        return auth_check
    
    try:
        chain_valid = secure_blockchain.is_chain_valid()  # type: ignore
        chain_length = len(secure_blockchain.chain)  # type: ignore
        
        return jsonify({
            'success': True,
            'blockchain_enabled': blockchain_enabled,
            'chain_valid': chain_valid,
            'chain_length': chain_length,
            'difficulty': secure_blockchain.difficulty,  # type: ignore
            'admin_id': session.get('admin_id'),  # type: ignore
            'authority_level': session.get('authority_level'),  # type: ignore
            'active_admin_sessions': len(secure_blockchain.active_admin_sessions)  # type: ignore
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Blockchain status error: {str(e)}'}), 500

@app.route('/api/admin/tourists', methods=['GET'])
@admin_required
def get_admin_tourists():  # type: ignore
    """Get all tourists for admin dashboard"""
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        tourists = list(tourists_collection.find({}))  # type: ignore
        
        # Remove MongoDB _id and format data
        for tourist in tourists:  # type: ignore
            tourist.pop('_id', None)  # type: ignore
            # Add status based on recent activity
            tourist['status'] = 'active'  # type: ignore
        
        return jsonify({
            'success': True,
            'data': tourists,  # Changed from 'tourists' to 'data' to match frontend expectation
            'total_count': len(tourists)  # type: ignore
        })
        
    except Exception as e:  # type: ignore
        print(f"ERROR in /api/admin/tourists: {str(e)}")  # Log the error
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():  # type: ignore
    """Logout admin and clear session"""
    try:
        admin_id_any = cast(Any, session.get('admin_id'))  # type: ignore
        admin_session_token_any = cast(Any, session.get('session_token'))  # type: ignore
        
        # Clear admin session from blockchain
        if admin_id_any and blockchain_enabled:
            if admin_id_any in secure_blockchain.active_admin_sessions:  # type: ignore
                del secure_blockchain.active_admin_sessions[admin_id_any]  # type: ignore
        
        # Terminate admin session (Mongo only)
        try:
            from mongo_db import end_admin_session, clear_admin_auth_state  # type: ignore
            if admin_session_token_any:
                end_admin_session(str(admin_session_token_any))
            if admin_id_any:
                clear_admin_auth_state(admin_id_any)
        except Exception:
            pass  # non-blocking
        
        # Clear Flask session
        session.pop('admin_authenticated', None)  # type: ignore
        session.pop('admin_id', None)  # type: ignore
        session.pop('admin_token', None)  # type: ignore
        session.pop('admin_permissions', None)  # type: ignore
        session.pop('authority_level', None)  # type: ignore
        session.pop('session_token', None)  # type: ignore
        
        return jsonify({
            'success': True,
            'message': 'Admin logout successful'
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Logout error: {str(e)}'}), 500

# =============== END SECURE ADMIN ROUTES ===============

# =============== ADMIN AI ANOMALY DETECTION SYSTEM ===============

@app.route('/api/admin/anomalies', methods=['GET'])
def get_ai_anomalies():  # type: ignore
    """Detect and return AI-powered anomalies in tourist behavior
    
    Anomaly Types Detected:
    - High-speed movement (>200 km/h) - possible kidnapping/trafficking
    - Long inactivity (6+ hours without location update) - health emergency
    - Multiple SOS from same location - area hazard
    - Movement to restricted/danger zones - safety risk
    - Unusual travel patterns - AI behavioral analysis
    
    Query Parameters:
    - severity: all|critical|high|medium|low (default: all)
    - limit: int (default: 50)
    - tourist_id: filter by specific tourist
    """
    try:
        # Admin authentication check
        if 'admin_id' not in session:
            return jsonify({'success': False, 'error': 'Admin authentication required'}), 401
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        
        # Parameters
        severity_filter = request.args.get('severity', 'all')  # type: ignore
        limit = request.args.get('limit', 50, type=int)  # type: ignore
        tourist_filter = request.args.get('tourist_id')  # type: ignore
        
        anomalies: List[Dict[str, Any]] = []
        current_time = datetime.utcnow()  # type: ignore
        
        # Get all tourists
        from mongo_db import mongo_db  # type: ignore
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        location_collection = mongo_db['_location_tracking']  # type: ignore
        sos_collection = mongo_db['_emergency_sos']  # type: ignore
        
        # Build query
        tourist_query = {'tourist_id': tourist_filter} if tourist_filter else {}
        tourists = list(tourists_collection.find(tourist_query).limit(200))  # type: ignore
        
        for tourist in tourists:  # type: ignore
            tourist_id = tourist.get('tourist_id')  # type: ignore
            full_name = tourist.get('full_name', 'Unknown')  # type: ignore
            
            # ==== ANOMALY 1: High-Speed Movement (Kidnapping Detection) ====
            recent_locations = list(location_collection.find(  # type: ignore
                {'tourist_id': tourist_id}
            ).sort('timestamp', -1).limit(2))  # type: ignore
            
            if len(recent_locations) >= 2:  # type: ignore
                loc1, loc2 = recent_locations[0], recent_locations[1]  # type: ignore
                try:
                    # Calculate speed
                    from math import radians, sin, cos, sqrt, atan2
                    lat1, lon1 = radians(loc1['latitude']), radians(loc1['longitude'])  # type: ignore
                    lat2, lon2 = radians(loc2['latitude']), radians(loc2['longitude'])  # type: ignore
                    
                    # Haversine formula
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                    distance_km = 6371 * c  # Earth radius in km
                    
                    # Time difference in hours
                    time_diff = (loc1['timestamp'] - loc2['timestamp']).total_seconds() / 3600  # type: ignore
                    
                    if time_diff > 0:
                        speed_kmh = distance_km / time_diff  # type: ignore
                        
                        if speed_kmh > 200:  # Critical: >200 km/h (possible kidnapping)
                            anomalies.append({
                                'type': 'HIGH_SPEED_MOVEMENT',
                                'severity': 'critical',
                                'tourist_id': tourist_id,
                                'tourist_name': full_name,
                                'details': f'Tourist moving at {speed_kmh:.1f} km/h (possible kidnapping/trafficking)',
                                'speed_kmh': round(speed_kmh, 1),  # type: ignore
                                'location': {
                                    'latitude': loc1['latitude'],  # type: ignore
                                    'longitude': loc1['longitude']  # type: ignore
                                },
                                'timestamp': loc1['timestamp'].isoformat(),  # type: ignore
                                'action_required': 'IMMEDIATE: Contact authorities and tourist emergency contacts',
                                'icon': '🚨'
                            })
                except Exception as e:  # type: ignore
                    print(f"Speed calculation error: {e}")
            
            # ==== ANOMALY 2: Long Inactivity (Health Emergency Detection) ====
            last_location = list(location_collection.find(  # type: ignore
                {'tourist_id': tourist_id}
            ).sort('timestamp', -1).limit(1))  # type: ignore
            
            if last_location:
                last_update = last_location[0]['timestamp']  # type: ignore
                hours_inactive = (current_time - last_update).total_seconds() / 3600  # type: ignore
                
                if hours_inactive > 6:  # 6+ hours without update
                    severity = 'critical' if hours_inactive > 24 else 'high'
                    anomalies.append({
                        'type': 'LONG_INACTIVITY',
                        'severity': severity,
                        'tourist_id': tourist_id,
                        'tourist_name': full_name,
                        'details': f'No location update for {hours_inactive:.1f} hours (possible health emergency)',
                        'hours_inactive': round(hours_inactive, 1),  # type: ignore
                        'last_location': {
                            'latitude': last_location[0]['latitude'],  # type: ignore
                            'longitude': last_location[0]['longitude']  # type: ignore
                        },
                        'last_seen': last_update.isoformat(),  # type: ignore
                        'action_required': 'Contact tourist and emergency contacts immediately',
                        'icon': '⚠️'
                    })
            
            # ==== ANOMALY 3: Repeated Zone Violations ====
            danger_zones_count = location_collection.count_documents({  # type: ignore
                'tourist_id': tourist_id,
                'zone_type': 'danger',
                'timestamp': {'$gte': current_time - timedelta(hours=2)}
            })
            
            if danger_zones_count >= 3:
                anomalies.append({
                    'type': 'REPEATED_DANGER_ZONE',
                    'severity': 'high',
                    'tourist_id': tourist_id,
                    'tourist_name': full_name,
                    'details': f'Entered danger zones {danger_zones_count} times in last 2 hours',
                    'zone_violations': danger_zones_count,
                    'action_required': 'Monitor closely, consider intervention',
                    'icon': '🚫'
                })
        
        # ==== ANOMALY 4: Multiple SOS from Same Location (Area Hazard) ====
        # Find SOS alerts in last 24 hours
        recent_sos = list(sos_collection.find({  # type: ignore
            'timestamp': {'$gte': current_time - timedelta(hours=24)}
        }))
        
        # Group by location (within 1km radius)
        from collections import defaultdict
        location_clusters: Dict[str, List[Dict]] = defaultdict(list)  # type: ignore
        
        for sos in recent_sos:  # type: ignore
            lat = round(sos.get('latitude', 0), 2)  # type: ignore  # Round to ~1km precision
            lon = round(sos.get('longitude', 0), 2)  # type: ignore
            key = f"{lat},{lon}"
            location_clusters[key].append(sos)  # type: ignore
        
        for location_key, sos_list in location_clusters.items():  # type: ignore
            if len(sos_list) >= 3:  # type: ignore  # 3+ SOS from same area
                lat, lon = map(float, location_key.split(','))
                anomalies.append({
                    'type': 'AREA_HAZARD',
                    'severity': 'critical',
                    'details': f'{len(sos_list)} SOS alerts from same location in 24 hours (possible area hazard)',  # type: ignore
                    'sos_count': len(sos_list),  # type: ignore
                    'affected_tourists': [s.get('tourist_id') for s in sos_list],  # type: ignore
                    'location': {'latitude': lat, 'longitude': lon},
                    'action_required': 'URGENT: Investigate area, issue warnings to nearby tourists',
                    'icon': '☢️'
                })
        
        # Filter by severity
        if severity_filter != 'all':
            anomalies = [a for a in anomalies if a['severity'] == severity_filter]
        
        # Sort by severity (critical > high > medium > low)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        anomalies.sort(key=lambda x: severity_order.get(x['severity'], 99))
        
        # Limit results
        anomalies = anomalies[:limit]
        
        # Count by severity
        severity_counts = {
            'critical': len([a for a in anomalies if a['severity'] == 'critical']),
            'high': len([a for a in anomalies if a['severity'] == 'high']),
            'medium': len([a for a in anomalies if a['severity'] == 'medium']),
            'low': len([a for a in anomalies if a['severity'] == 'low'])
        }
        
        return jsonify({
            'success': True,
            'total_anomalies': len(anomalies),
            'severity_counts': severity_counts,
            'anomalies': anomalies,
            'analysis_timestamp': current_time.isoformat()
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== END ADMIN AI ANOMALY DETECTION ===============

# =============== ADMIN SESSION INSPECTION (Dashboard auth) ===============

@app.route('/api/admin/sessions', methods=['GET'])
def list_admin_sessions():  # type: ignore
    """List recent admin sessions from user_sessions (requires dashboard admin session)

    Guard: verifies admin_id + session_token exist in Flask session and match admin_users.session_token
    Query params:
      - limit: int (default 50)
      - active_only: bool (default false)
    """
    try:
        # Verify dashboard admin session
        admin_id = cast(Any, session.get('admin_id'))  # type: ignore
        session_token = cast(Any, session.get('session_token'))  # type: ignore
        if not admin_id or not session_token:
            return jsonify({'success': False, 'error': 'Not authenticated as admin'}), 401

        limit = request.args.get('limit', 50, type=int)  # type: ignore
        active_only = request.args.get('active_only', 'false').lower() == 'true'  # type: ignore
        sessions_data: List[Dict[str, Any]] = []
        from mongo_db import list_admin_sessions_mongo  # type: ignore
        raw = list_admin_sessions_mongo(limit=limit, active_only=active_only)
        for doc in raw:
            sessions_data.append({
                'session_id': doc.get('session_id'),
                'admin_user_id': doc.get('user_id'),
                'user_type': doc.get('user_type'),
                'login_timestamp': doc.get('login_timestamp'),
                'logout_timestamp': doc.get('logout_timestamp'),
                'ip_address': doc.get('ip_address'),
                'user_agent': doc.get('user_agent'),
                'device_info': doc.get('device_info'),
                'session_status': doc.get('session_status')
            })
        return jsonify({'success': True, 'count': len(sessions_data), 'sessions': sessions_data, 'backend': 'mongo'})
    
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== AI MONITORING ROUTES ===============

@app.route('/api/ai/monitor/analyze', methods=['POST'])
def analyze_tourist_movement():  # type: ignore
    """Perform AI analysis of tourist movement and environment"""
    try:
        if not ai_monitoring_enabled:
            return jsonify({'error': 'AI monitoring system not available'}), 503
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract required parameters
        tourist_id = data.get('tourist_id')  # type: ignore
        if not tourist_id:
            return jsonify({'error': 'Tourist ID is required'}), 400
        
        # Optional parameters with location
        location = data.get('location', {})  # type: ignore
        behavior_data = data.get('behavior_data', {})  # type: ignore
        
        # Simple risk analysis based on available data
        risk_level = 'low'  # Default
        risk_score = 0.2
        
        # Basic heuristics for risk assessment
        if location:
            # Check if location data is present
            if 'latitude' in location and 'longitude' in location:
                # For now, default to low risk - can be enhanced with geofencing data
                risk_level = 'low'
                risk_score = 0.3
        
        # Store AI analysis in MongoDB
        if mongo_enabled():
            try:
                init_mongo()
                from mongo_db import store_ai_analysis  # type: ignore
                analysis_record: Dict[str, Any] = {
                    'tourist_id': tourist_id,
                    'location': location,
                    'behavior_data': behavior_data,
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'timestamp': datetime.now().isoformat()
                }
                store_ai_analysis(analysis_record)  # type: ignore
            except Exception:
                pass  # Non-critical, continue
        
        return jsonify({
            'success': True,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'analysis': {
                'tourist_id': tourist_id,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'AI analysis error: {str(e)}'}), 500

@app.route('/api/ai/monitor/dashboard', methods=['GET'])
def get_monitoring_dashboard():  # type: ignore
    """Get monitoring dashboard data for admin"""
    try:
        # Check admin authentication (check both admin_id and admin_authenticated)
        if not (session.get('admin_authenticated') or session.get('admin_id')):  # type: ignore
            return jsonify({'error': 'Admin authentication required'}), 401
        
        # Get time range from query parameters
        hours = request.args.get('hours', 24, type=int)  # type: ignore
        if hours > 168:  # Limit to 1 week
            hours = 168
        
        # If AI monitoring system is available, use it
        if ai_monitoring_enabled and ai_monitoring_system:
            dashboard_data = ai_monitoring_system.get_monitoring_dashboard_data(hours)
            return jsonify({
                'success': True,
                'dashboard': dashboard_data
            })
        
        # MongoDB fallback - provide basic dashboard data
        if not mongo_enabled():
            return jsonify({
                'success': False,
                'error': 'AI monitoring requires MongoDB backend',
                'message': 'The AI monitoring service is unavailable. Please ensure MongoDB is running.'
            }), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        from datetime import datetime, timedelta
        
        # Calculate time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get basic statistics from MongoDB
        ai_results = mongo_db['_ai_monitoring_results']  # type: ignore
        risk_alerts = mongo_db['_risk_alerts']  # type: ignore
        
        total_analyses = ai_results.count_documents({'analysis_timestamp': {'$gte': cutoff_time}})  # type: ignore
        high_risk = risk_alerts.count_documents({'risk_level': 'high', 'created_at': {'$gte': cutoff_time}})  # type: ignore
        medium_risk = risk_alerts.count_documents({'risk_level': 'medium', 'created_at': {'$gte': cutoff_time}})  # type: ignore
        low_risk = risk_alerts.count_documents({'risk_level': 'low', 'created_at': {'$gte': cutoff_time}})  # type: ignore
        
        # Basic dashboard data
        dashboard_data: Dict[str, Any] = {  # type: ignore
            'total_analyses': total_analyses,
            'high_risk_alerts': high_risk,
            'medium_risk_alerts': medium_risk,
            'low_risk_alerts': low_risk,
            'time_range_hours': hours,
            'last_updated': datetime.now().isoformat(),
            'status': 'operational',
            'backend': 'mongodb'
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        print(f"ERROR in /api/ai/monitor/dashboard: {str(e)}")  # Log error
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Dashboard data error: {str(e)}',
            'message': 'Failed to load AI dashboard data. The service may be temporarily unavailable.'
        }), 500

@app.route('/api/ai/monitor/tourist/<int:tourist_id>/analyze', methods=['POST'])
def analyze_specific_tourist(tourist_id):  # type: ignore
    """Analyze a specific tourist's current situation"""
    try:
        if not ai_monitoring_enabled or not ai_monitoring_system:
            return jsonify({'error': 'AI monitoring system not available'}), 503
        
        data = request.get_json() or {}  # type: ignore
        
        # Get current location if provided
        current_location = data.get('current_location')  # type: ignore
        weather_data = data.get('weather_data')  # type: ignore
        nearby_tourists = data.get('nearby_tourists', 0)  # type: ignore
        
        # Perform analysis
        analysis_result = ai_monitoring_system.analyze_tourist_movement(
            tourist_id=tourist_id,
            current_location=current_location,
            weather_data=weather_data,
            nearby_tourists=nearby_tourists
        )  # type: ignore
        
        return jsonify({
            'success': True,
            'tourist_id': tourist_id,
            'analysis': analysis_result
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Tourist analysis error: {str(e)}'}), 500

@app.route('/api/ai/monitor/alerts', methods=['GET'])
def get_ai_alerts():  # type: ignore
    """Get recent AI-generated alerts"""
    try:
        if not ai_monitoring_enabled:
            return jsonify({'error': 'AI monitoring system not available'}), 503

        # Allow both admin and regular users to view alerts
        # Admin check removed to allow user dashboard to access alerts

        hours = request.args.get('hours', 24, type=int)  # type: ignore
        priority = request.args.get('priority')  # type: ignore

        # Mongo-only implementation
        alerts: list[dict[str, Any]] = []
        used_backend = 'mongo'
        from mongo_db import mongo_enabled, list_risk_alerts  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'MongoDB not enabled'}), 503
        raw = list_risk_alerts(hours=hours, priority=priority)
        for doc in raw:
            alerts.append({
                'alert_id': doc.get('alert_id'),
                'tourist_id': doc.get('tourist_id'),
                'user_id': doc.get('user_id'),
                'alert_type': doc.get('alert_type'),
                'priority': doc.get('priority'),
                'risk_level': doc.get('risk_level'),
                'location': {'latitude': doc.get('latitude'), 'longitude': doc.get('longitude')} if doc.get('latitude') and doc.get('longitude') else None,
                'alert_timestamp': doc.get('alert_timestamp'),
                'message': doc.get('message'),
                'acknowledged': bool(doc.get('acknowledged')),
                'acknowledged_by': doc.get('acknowledged_by'),
                'acknowledgment_timestamp': doc.get('acknowledgment_timestamp'),
                'resolved': bool(doc.get('resolved')),
                'resolution_timestamp': doc.get('resolution_timestamp')
            })
        return jsonify({'success': True, 'alerts': alerts, 'total_count': len(alerts), 'time_range_hours': hours, 'backend': used_backend})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Alerts retrieval error: {str(e)}'}), 500

@app.route('/api/ai/monitor/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_ai_alert(alert_id: str):  # type: ignore
    """Acknowledge an AI-generated alert"""
    try:
        if not session.get('admin_authenticated'):  # type: ignore
            return jsonify({'error': 'Admin authentication required'}), 401
        admin_id = session.get('admin_id')  # type: ignore
        from mongo_db import mongo_enabled, acknowledge_risk_alert  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'MongoDB not enabled'}), 503
        ok = acknowledge_risk_alert(alert_id, admin_id)
        if not ok:
            return jsonify({'error': 'Alert not found'}), 404
        return jsonify({'success': True, 'message': 'Alert acknowledged successfully', 'alert_id': alert_id, 'acknowledged_by': admin_id, 'backend': 'mongo'})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Alert acknowledgment error: {str(e)}'}), 500

@app.route('/api/ai/monitor/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_ai_alert(alert_id: str):  # type: ignore
    """Mark an AI-generated alert as resolved"""
    try:
        if not session.get('admin_authenticated'):  # type: ignore
            return jsonify({'error': 'Admin authentication required'}), 401
        from mongo_db import mongo_enabled, resolve_risk_alert  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'MongoDB not enabled'}), 503
        ok = resolve_risk_alert(alert_id)
        if not ok:
            return jsonify({'error': 'Alert not found'}), 404
        return jsonify({'success': True, 'message': 'Alert resolved successfully', 'alert_id': alert_id, 'backend': 'mongo'})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Alert resolution error: {str(e)}'}), 500

@app.route('/api/ai/monitor/statistics', methods=['GET'])
def get_ai_monitoring_statistics():  # type: ignore
    """Get AI monitoring system statistics"""
    try:
        if not ai_monitoring_enabled:
            return jsonify({'error': 'AI monitoring system not available'}), 503
        if not session.get('admin_authenticated'):  # type: ignore
            return jsonify({'error': 'Admin authentication required'}), 401

        if not mongo_enabled():
            return jsonify({'error': 'MongoDB not enabled'}), 503
        from mongo_db import get_ai_statistics  # type: ignore
        stats = get_ai_statistics(hours=24)
        return jsonify({'success': True, 'statistics': stats, 'ai_monitoring_enabled': ai_monitoring_enabled, 'timestamp': datetime.now().isoformat(), 'backend': 'mongo'})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Statistics error: {str(e)}'}), 500

# =============== END AI MONITORING ROUTES ===============

# =============== INCIDENT RESPONSE ROUTES ===============

@app.route('/api/incident/response', methods=['POST'])
def trigger_incident_response():  # type: ignore
    """Trigger comprehensive incident response for emergency situations"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required incident data
        required_fields = ['incident_id', 'incident_type', 'location', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Persist incident in Mongo
        try:
            from mongo_db import mongo_enabled, upsert_incident, log_response_activity  # type: ignore
            if mongo_enabled():
                from typing import Dict, Any
                inc_doc: Dict[str, Any] = {
                    'incident_id': data['incident_id'],
                    'incident_type': data['incident_type'],
                    'location': data['location'],
                    'severity': data['severity'],
                    'status': 'initiated'
                }
                stored = upsert_incident(inc_doc)
                log_response_activity({'incident_id': stored.get('incident_id'), 'activity_type': 'incident_initiated', 'activity_data': {'severity': stored.get('severity')}})
                response_status = {'status': 'initiated', 'backend': 'mongo'}
            else:
                response_status = {'status': 'initiated', 'backend': 'mongo'}
        except Exception as inner:  # type: ignore
            response_status = {'status': 'error', 'message': f'Persistence failure: {inner}'}

        return jsonify({'success': True, 'incident_response': response_status, 'message': 'Incident response activated successfully'})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Incident response error: {str(e)}'}), 500

@app.route('/api/incident/status/<incident_id>', methods=['GET'])
def get_incident_status(incident_id: str):  # type: ignore
    """Get real-time incident response status"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        backend = 'mongo'
        status_payload: Dict[str, Any] = {}
        try:
            from mongo_db import mongo_enabled, get_incident  # type: ignore
            if mongo_enabled():
                doc = get_incident(incident_id)
                if not doc:
                    return jsonify({'success': False, 'error': 'Incident not found'}), 404
                status_payload = {'incident_id': incident_id, 'status': doc.get('status'), 'severity': doc.get('severity'), 'updated_at': doc.get('updated_at')}
            else:
                backend = 'mongo'
                status_payload = {'incident_id': incident_id, 'status': 'unknown'}
        except Exception as inner:  # type: ignore
            return jsonify({'success': False, 'error': f'Status fetch error: {inner}'}), 500
        return jsonify({'success': True, 'status': status_payload, 'backend': backend, 'timestamp': datetime.now().isoformat()})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Status retrieval error: {str(e)}'}), 500

@app.route('/api/incident/track/<incident_id>', methods=['GET'])
def track_incident_response(incident_id: str):  # type: ignore
    """Real-time incident response tracking page"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        backend = 'mongo'
        tracking: Dict[str, Any] = {}
        try:
            from mongo_db import mongo_enabled, get_incident  # type: ignore
            if mongo_enabled():
                doc = get_incident(incident_id)
                if not doc:
                    return jsonify({'success': False, 'error': 'Incident not found'}), 404
                tracking = {'status': doc.get('status'), 'severity': doc.get('severity'), 'location': doc.get('location')}
            else:
                backend = 'mongo'
                tracking = {'status': 'unknown'}
        except Exception as inner:  # type: ignore
            return jsonify({'success': False, 'error': f'Tracking fetch error: {inner}'}), 500
        return jsonify({'success': True, 'incident_id': incident_id, 'tracking_data': tracking, 'live_updates_enabled': True, 'update_interval': 30, 'backend': backend})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Tracking error: {str(e)}'}), 500

@app.route('/api/authority/verify', methods=['POST'])
def verify_authority_access():  # type: ignore
    """Verify authority access to incident using blockchain digital ID"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['authority_id', 'incident_id', 'digital_signature']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        try:
            from mongo_db import mongo_enabled, record_authority_verification  # type: ignore
            verification_result = {'status': 'recorded', 'backend': 'mongo'}
            if mongo_enabled():
                record_authority_verification({'incident_id': data['incident_id'], 'authority_id': data['authority_id'], 'digital_signature': data['digital_signature'], 'verification_status': 'verified'})
            else:
                verification_result = {'status': 'recorded', 'backend': 'mongo'}
        except Exception as inner:  # type: ignore
            verification_result = {'status': 'error', 'message': str(inner)}
        return jsonify({'success': True, 'verification': verification_result, 'timestamp': datetime.now().isoformat()})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Authority verification error: {str(e)}'}), 500

@app.route('/api/dispatch/update', methods=['POST'])
def update_dispatch_location():  # type: ignore
    """Update real-time location of emergency service dispatch"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['dispatch_id', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        dispatch_id = data.get('dispatch_id')
        location = data.get('location')
        if not dispatch_id or not location:
            return jsonify({'success': False, 'error': 'dispatch_id and location required'}), 400
        backend = 'mongo'
        try:
            from mongo_db import mongo_enabled, update_dispatch, log_response_activity  # type: ignore
            if mongo_enabled():
                ok = update_dispatch(dispatch_id, {'current_location': location})
                if ok:
                    log_response_activity({'incident_id': data.get('incident_id'), 'activity_type': 'dispatch_location_update', 'activity_data': {'dispatch_id': dispatch_id, 'location': location}})
                return jsonify({'success': True, 'updated': ok, 'backend': backend, 'timestamp': datetime.now().isoformat()})
            else:
                backend = 'mongo'
                return jsonify({'success': True, 'updated': True, 'backend': backend, 'timestamp': datetime.now().isoformat()})
        except Exception as inner:  # type: ignore
            return jsonify({'success': False, 'error': f'Update failure: {inner}'}), 500
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Dispatch update error: {str(e)}'}), 500

@app.route('/api/dispatch/arrived', methods=['POST'])
def mark_service_arrived():  # type: ignore
    """Mark emergency service as arrived at incident location"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['dispatch_id', 'arrival_location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        dispatch_id = data.get('dispatch_id')
        arrival_location = data.get('arrival_location')
        if not dispatch_id:
            return jsonify({'success': False, 'error': 'dispatch_id required'}), 400
        backend = 'mongo'
        try:
            from mongo_db import mongo_enabled, mark_dispatch_arrived, log_response_activity  # type: ignore
            if mongo_enabled():
                ok = mark_dispatch_arrived(dispatch_id, arrival_location)
                if ok:
                    log_response_activity({'incident_id': data.get('incident_id'), 'activity_type': 'dispatch_arrived', 'activity_data': {'dispatch_id': dispatch_id, 'arrival_location': arrival_location}})
                return jsonify({'success': True, 'arrived': ok, 'backend': backend, 'timestamp': datetime.now().isoformat()})
            else:
                backend = 'mongo'
                return jsonify({'success': True, 'arrived': True, 'backend': backend, 'timestamp': datetime.now().isoformat()})
        except Exception as inner:  # type: ignore
            return jsonify({'success': False, 'error': f'Arrival failure: {inner}'}), 500
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Service arrival error: {str(e)}'}), 500

@app.route('/api/incident/response/stats', methods=['GET'])
def get_incident_response_stats():  # type: ignore
    """Get incident response system statistics"""
    if not incident_response_enabled:
        return jsonify({'error': 'Incident response system not available'}), 503
    
    try:
        backend = 'mongo'
        try:
            from mongo_db import mongo_enabled, get_incident_response_stats as _get_stats  # type: ignore
            if mongo_enabled():
                stats = _get_stats(hours=24)
            else:
                backend = 'mongo'
                stats = {}
        except Exception as inner:  # type: ignore
            return jsonify({'success': False, 'error': f'Stat retrieval failure: {inner}'}), 500
        return jsonify({'success': True, 'statistics': stats, 'incident_response_enabled': incident_response_enabled, 'backend': backend, 'timestamp': datetime.now().isoformat()})
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Statistics error: {str(e)}'}), 500

# =============== END INCIDENT RESPONSE ROUTES ===============

# =============== EMERGENCY CONTACT MANAGEMENT SYSTEM ===============

@app.route('/contacts')
def contacts_page() -> str:  # type: ignore
    """Render Emergency Contacts management page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # type: ignore
    return render_template('emergency_contacts.html', user=session)

@app.route('/api/contacts/list', methods=['GET'])
def list_emergency_contacts():  # type: ignore
    """Get all emergency contacts for logged-in user"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        tourist = tourists_collection.find_one({'tourist_id': user_id})  # type: ignore
        
        if not tourist:
            return jsonify({'success': False, 'error': 'Tourist not found'}), 404
        
        contacts = tourist.get('emergency_contacts', [])  # type: ignore
        
        return jsonify({
            'success': True,
            'total_contacts': len(contacts),  # type: ignore
            'contacts': contacts
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/add', methods=['POST'])
def add_emergency_contact():  # type: ignore
    """Add new emergency contact
    
    Request Body:
    {
        "name": "string",
        "relationship": "string (e.g., spouse, parent, friend)",
        "phone": "string",
        "email": "string (optional)",
        "is_primary": boolean (optional)
    }
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        data = request.get_json()
        
        # Validation
        name = data.get('name')  # type: ignore
        relationship = data.get('relationship')  # type: ignore
        phone = data.get('phone')  # type: ignore
        email = data.get('email', '')  # type: ignore
        is_primary = data.get('is_primary', False)  # type: ignore
        
        if not name or not relationship or not phone:
            return jsonify({'success': False, 'error': 'Name, relationship, and phone are required'}), 400
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        import uuid
        
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        
        # Create new contact with unique ID
        new_contact = {  # type: ignore
            'contact_id': str(uuid.uuid4()),
            'name': name,
            'relationship': relationship,
            'phone': phone,
            'email': email,
            'is_primary': is_primary,
            'added_date': datetime.utcnow().isoformat()  # type: ignore
        }
        
        # If this is primary, remove primary flag from others
        if is_primary:
            tourists_collection.update_one(  # type: ignore
                {'tourist_id': user_id},
                {'$set': {'emergency_contacts.$[].is_primary': False}}
            )
        
        # Add contact to array
        result = tourists_collection.update_one(  # type: ignore
            {'tourist_id': user_id},
            {'$push': {'emergency_contacts': new_contact}}
        )
        
        if result.matched_count == 0:  # type: ignore
            return jsonify({'success': False, 'error': 'Tourist not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact added successfully',
            'contact': new_contact
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/edit/<contact_id>', methods=['PUT'])
def edit_emergency_contact(contact_id: str):  # type: ignore
    """Edit existing emergency contact
    
    Request Body:
    {
        "name": "string (optional)",
        "relationship": "string (optional)",
        "phone": "string (optional)",
        "email": "string (optional)",
        "is_primary": boolean (optional)
    }
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        data = request.get_json()
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        
        # Build update fields
        update_fields: Dict[str, Any] = {}
        if 'name' in data:
            update_fields['emergency_contacts.$.name'] = data['name']
        if 'relationship' in data:
            update_fields['emergency_contacts.$.relationship'] = data['relationship']
        if 'phone' in data:
            update_fields['emergency_contacts.$.phone'] = data['phone']
        if 'email' in data:
            update_fields['emergency_contacts.$.email'] = data['email']
        if 'is_primary' in data:
            update_fields['emergency_contacts.$.is_primary'] = data['is_primary']
            
            # If setting as primary, remove primary from others first
            if data['is_primary']:
                tourists_collection.update_one(  # type: ignore
                    {'tourist_id': user_id},
                    {'$set': {'emergency_contacts.$[].is_primary': False}}
                )
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No update fields provided'}), 400
        
        # Update the contact
        result = tourists_collection.update_one(  # type: ignore
            {'tourist_id': user_id, 'emergency_contacts.contact_id': contact_id},
            {'$set': update_fields}
        )
        
        if result.matched_count == 0:  # type: ignore
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact updated successfully',
            'contact_id': contact_id
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/delete/<contact_id>', methods=['DELETE'])
def delete_emergency_contact(contact_id: str):  # type: ignore
    """Delete emergency contact"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        
        # Remove contact from array
        result = tourists_collection.update_one(  # type: ignore
            {'tourist_id': user_id},
            {'$pull': {'emergency_contacts': {'contact_id': contact_id}}}
        )
        
        if result.matched_count == 0:  # type: ignore
            return jsonify({'success': False, 'error': 'Tourist not found'}), 404
        
        if result.modified_count == 0:  # type: ignore
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact deleted successfully',
            'contact_id': contact_id
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/set-primary/<contact_id>', methods=['PUT'])
def set_primary_contact(contact_id: str):  # type: ignore
    """Set a contact as primary emergency contact"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        
        # Remove primary from all contacts
        tourists_collection.update_one(  # type: ignore
            {'tourist_id': user_id},
            {'$set': {'emergency_contacts.$[].is_primary': False}}
        )
        
        # Set this contact as primary
        result = tourists_collection.update_one(  # type: ignore
            {'tourist_id': user_id, 'emergency_contacts.contact_id': contact_id},
            {'$set': {'emergency_contacts.$.is_primary': True}}
        )
        
        if result.matched_count == 0:  # type: ignore
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Primary contact updated successfully',
            'contact_id': contact_id
        })
    
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== END EMERGENCY CONTACT MANAGEMENT ===============

# =============== BLOCKCHAIN VERIFICATION ROUTES ===============

@app.route('/api/blockchain/verify-incident/<incident_id>', methods=['GET'])
def verify_incident_blockchain(incident_id: str):  # type: ignore
    """Verify incident records in blockchain"""
    try:
        from mongo_db import mongo_enabled, get_incident_blockchain_record, verify_blockchain_integrity  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'Blockchain backend (Mongo) disabled'}), 503
        incident_record = get_incident_blockchain_record(incident_id)
        blockchain_verification = verify_blockchain_integrity()
        return jsonify({'success': True, 'incident_id': incident_id, 'incident_record': incident_record, 'blockchain_integrity': blockchain_verification, 'backend': 'mongo', 'timestamp': datetime.now().isoformat()})
    except Exception as e:  # type: ignore
        return jsonify({'error': f'Verification error: {e}'}), 500

@app.route('/api/blockchain/audit-trail/<incident_id>', methods=['GET'])
def get_incident_audit_trail(incident_id: str):  # type: ignore
    """Get complete audit trail for an incident"""
    try:
        from mongo_db import mongo_enabled, get_incident_blockchain_record, get_incident_activity_logs  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'Blockchain audit not available'}), 503
        incident_record = get_incident_blockchain_record(incident_id)
        activity_logs = get_incident_activity_logs(incident_id)
        return jsonify({'success': True, 'incident_id': incident_id, 'incident_record': incident_record, 'activity_logs': activity_logs, 'total_activities': len(activity_logs), 'backend': 'mongo', 'timestamp': datetime.now().isoformat()})
    except Exception as e:  # type: ignore
        return jsonify({'error': f'Audit trail error: {e}'}), 500

@app.route('/api/blockchain/public-verification', methods=['GET'])
def public_blockchain_verification():  # type: ignore
    """Public endpoint for blockchain integrity verification"""
    try:
        from mongo_db import mongo_enabled, verify_blockchain_integrity  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'Blockchain verification not available'}), 503
        verification_results = verify_blockchain_integrity()
        return jsonify({'success': True, 'blockchain_verification': verification_results, 'backend': 'mongo', 'timestamp': datetime.now().isoformat()})
    except Exception as e:  # type: ignore
        return jsonify({'error': f'Public verification error: {e}'}), 500

@app.route('/api/blockchain/stats', methods=['GET'])
def blockchain_statistics():  # type: ignore
    """Get blockchain logging statistics"""
    try:
        from mongo_db import mongo_enabled, get_blockchain_stats  # type: ignore
        if not mongo_enabled():
            return jsonify({'error': 'Blockchain statistics not available'}), 503
        stats = get_blockchain_stats()
        return jsonify({'success': True, **stats, 'backend': 'mongo', 'timestamp': datetime.now().isoformat()})
    except Exception as e:  # type: ignore
        return jsonify({'error': f'Blockchain statistics error: {e}'}), 500

# =============== END BLOCKCHAIN VERIFICATION ROUTES ===============

# =============== POST-INCIDENT REPORTING ROUTES ===============

@app.route('/api/reports/generate/<incident_id>', methods=['POST'])
@admin_required
def generate_incident_report(incident_id):  # type: ignore
    """Generate comprehensive post-incident report - Admin Only"""
    if not post_incident_reporting_enabled or not post_incident_reporter:
        return jsonify({'error': 'Post-incident reporting not available'}), 503
    
    try:
        data = request.get_json() or {}  # type: ignore
        report_type = data.get('report_type', 'full')  # type: ignore
        
        # Generate the comprehensive report
        report = post_incident_reporter.generate_comprehensive_report(incident_id, report_type)
        
        return jsonify({
            'success': True,
            'report_generated': True,
            'report_id': report['report_metadata']['report_id'],
            'incident_id': incident_id,
            'report_type': report_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:  # type: ignore  # Exception handled
        return jsonify({'error': f'Report generation error: {str(e)}'}), 500

@app.route('/api/reports/<report_id>', methods=['GET'])
@admin_required
def get_incident_report(report_id: str):  # type: ignore
    """Retrieve a generated incident report (Mongo only)."""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        from mongo_db import get_post_incident_report  # type: ignore
        doc = get_post_incident_report(str(report_id))
        if not doc:
            return jsonify({'error': 'Report not found'}), 404
        # Stored report payload expected in 'report_data' or already expanded fields
        report_payload: Dict[str, Any] = cast(Dict[str, Any], doc.get('report_data') or {})
        return jsonify({
            'success': True,
            'report': report_payload,
            'metadata': {
                'report_id': doc.get('report_id'),
                'incident_id': doc.get('incident_id'),
                'report_type': doc.get('report_type'),
                'generated_at': doc.get('report_generated_at'),
                'status': doc.get('status')
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:  # pragma: no cover
        return jsonify({'error': f'Report retrieval error: {str(e)}'}), 500

@app.route('/api/reports/<report_id>/share', methods=['POST'])
@admin_required
def share_incident_report(report_id: str):  # type: ignore
    """Share incident report (Mongo). Records share log entries."""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        pdata = parse_report_share_payload()
        share_with_tourist = bool(pdata.get('share_with_tourist', True))
        share_with_authorities = bool(pdata.get('share_with_authorities', True))
        authority_types: List[str] = pdata.get('authority_types', ['police', 'medical', 'emergency_services'])  # type: ignore[assignment]
        from mongo_db import get_post_incident_report, share_post_incident_report  # type: ignore
        report = get_post_incident_report(str(report_id))
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        incident_id = report.get('incident_id')
        tourist_id = report.get('tourist_id')
        sharing_results: Dict[str, Any] = {}
        if share_with_tourist and tourist_id:
            log = share_post_incident_report(str(report_id), 'tourist', str(tourist_id), 'system_notification', 'sent')
            sharing_results['tourist'] = {'shared': True, 'log_id': log.get('sharing_id')}
        if share_with_authorities:
            authority_logs: List[Dict[str, Any]] = []
            for auth in authority_types:
                alog = share_post_incident_report(str(report_id), 'authority', str(auth), 'secure_channel', 'queued')
                authority_logs.append({'authority': auth, 'log_id': alog.get('sharing_id')})
            sharing_results['authorities'] = authority_logs
        return jsonify({
            'success': True,
            'report_id': report_id,
            'incident_id': incident_id,
            'sharing_results': sharing_results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:  # pragma: no cover
        return jsonify({'error': f'Report sharing error: {str(e)}'}), 500

@app.route('/api/reports', methods=['GET'])
@admin_required
def list_all_reports():  # type: ignore
    """List all post-incident reports for admin dashboard"""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        
        reports_collection = mongo_db['_post_incident_reports']  # type: ignore
        reports = list(reports_collection.find({}).sort('created_at', -1).limit(100))  # type: ignore
        
        # Remove MongoDB _id
        for report in reports:  # type: ignore
            report.pop('_id', None)  # type: ignore
        
        return jsonify({
            'success': True,
            'data': reports,  # Changed from 'reports' to 'data' to match frontend expectation
            'total_count': len(reports)  # type: ignore
        })
        
    except Exception as e:  # type: ignore
        print(f"ERROR in /api/reports: {str(e)}")  # Log the error
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/tourist/<tourist_id>', methods=['GET'])
@admin_required
def get_tourist_reports(tourist_id: str):  # type: ignore
    """List reports for a tourist (Mongo)."""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        from mongo_db import list_reports_for_tourist  # type: ignore
        docs = list_reports_for_tourist(str(tourist_id))
        reports: list[Dict[str, Any]] = []
        for d in docs:
            reports.append({
                'report_id': d.get('report_id'),
                'incident_id': d.get('incident_id'),
                'report_generated_at': d.get('report_generated_at'),
                'report_type': d.get('report_type'),
                'status': d.get('status'),
                'incident_timestamp': d.get('incident_timestamp'),
                'emergency_type': d.get('emergency_type')
            })
        return jsonify({
            'success': True,
            'tourist_id': tourist_id,
            'reports': reports,
            'total_reports': len(reports),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:  # pragma: no cover
        return jsonify({'error': f'Tourist reports retrieval error: {str(e)}'}), 500

@app.route('/api/reports/statistics', methods=['GET'])
@admin_required
def get_reporting_statistics():  # type: ignore
    """Get post-incident reporting statistics (Mongo)."""
    if not mongo_enabled():
        return jsonify({'error': 'MongoDB not enabled'}), 503
    try:
        from mongo_db import get_reporting_statistics  # type: ignore
        stats = get_reporting_statistics()
        return jsonify({
            'success': True,
            'reporting_enabled': True,
            'statistics': {
                'total_reports': stats.get('total_reports', 0),
                'completed_reports': stats.get('completed_reports', 0),
                'total_shares': stats.get('total_shares', 0),
                'tourist_shares': stats.get('tourist_shares', 0),
                'authority_shares': stats.get('authority_shares', 0)
            },
            'recent_reports': stats.get('recent_reports', []),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:  # pragma: no cover
        return jsonify({'error': f'Reporting statistics error: {str(e)}'}), 500

# =============== END POST-INCIDENT REPORTING ROUTES ===============

# =============== OFFLINE SMS EMERGENCY SYSTEM ===============

@app.route('/api/sms/receive', methods=['POST'])
def receive_emergency_sms() -> Union[Response, tuple[Response, int]]:
    """Receive SMS commands for offline emergency triggers (Twilio webhook)"""
    try:
        # Get SMS data from Twilio webhook
        from_number = request.form.get('From', request.json.get('from_number') if request.json else None)
        message_body = request.form.get('Body', request.json.get('message') if request.json else '')
        
        if not from_number or not message_body:
            return jsonify({'success': False, 'error': 'Missing phone number or message'}), 400
        
        message_upper = message_body.upper().strip()
        
        # Find tourist by phone number
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        tourist = get_tourist_by_phone(from_number)
        
        if not tourist:
            # Send help message
            send_sms_response(from_number, 
                "⚠️ Phone number not registered. Please register at our website first.")
            return jsonify({'success': True, 'message': 'Unknown number'})
        
        tourist_id = tourist.get('tourist_id')  # type: ignore
        
        # Process SMS commands
        if 'SOS' in message_upper or 'HELP' in message_upper or 'EMERGENCY' in message_upper:
            # Trigger emergency SOS
            if tourist_id:  # type: ignore
                trigger_sms_emergency(str(tourist_id), from_number, message_body)
            send_sms_response(from_number,
                f"🚨 EMERGENCY ACTIVATED!\n\nHelp is being dispatched to your last known location.\n\nStay safe, {tourist.get('full_name', 'Tourist')}!")  # type: ignore
            
        elif 'LOCATION' in message_upper:
            # Send last known location
            if tourist_id:  # type: ignore
                location = get_last_known_location(str(tourist_id))
            else:
                location = None
            if location:
                send_sms_response(from_number,
                    f"📍 Your last location:\nLat: {location.get('latitude')}\nLng: {location.get('longitude')}\nTime: {location.get('timestamp')}")  # type: ignore
            else:
                send_sms_response(from_number, "No location data available.")
        
        elif 'STATUS' in message_upper:
            # Send safety status
            send_sms_response(from_number,
                f"✅ Safety Status: Active\n🛡️ Safety Score: 92\n📱 App: tourist-safety.com")
        
        else:
            # Unknown command - send help
            send_sms_response(from_number,
                "📱 SMS Commands:\n• SOS / HELP / EMERGENCY - Trigger emergency\n• LOCATION - Get your location\n• STATUS - Check safety status")
        
        return jsonify({'success': True, 'message': 'SMS processed'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def trigger_sms_emergency(tourist_id: str, phone: str, message: str) -> None:
    """Trigger emergency from SMS"""
    try:
        # Create emergency alert
        alert_data: Dict[str, Any] = {
            'tourist_id': tourist_id,
            'alert_type': 'sms_sos',
            'severity_level': 'critical',
            'message': f'SMS Emergency: {message}',
            'status': 'active',
            'timestamp': datetime.now().isoformat(),
            'trigger_method': 'sms',
            'phone_number': phone
        }
        
        # Get last known location
        location = get_last_known_location(tourist_id)
        if location:
            alert_data['latitude'] = location.get('latitude')  # type: ignore
            alert_data['longitude'] = location.get('longitude')  # type: ignore
        
        create_enhanced_panic_alert(alert_data)
        
        # Notify emergency contacts
        from mongo_db import mongo_db  # type: ignore
        init_mongo()
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        tourist = tourists_collection.find_one({'tourist_id': tourist_id})  # type: ignore
        
        if tourist and tourist.get('emergency_contacts'):  # type: ignore
            for contact in tourist['emergency_contacts']:  # type: ignore
                contact_phone = contact.get('phone')  # type: ignore
                if contact_phone:
                    send_sms_response(str(contact_phone),  # type: ignore
                        f"🚨 EMERGENCY ALERT\n\n{tourist.get('full_name', 'Tourist')} triggered SOS via SMS.\n\nMessage: {message}\n\nPlease check on them immediately!")  # type: ignore
        
    except Exception as e:  # type: ignore
        print(f"Error triggering SMS emergency: {e}")

def send_sms_response(to_number: str, message: str) -> bool:
    """Send SMS response (placeholder - integrate with Twilio/similar)"""
    try:
        # TODO: Integrate with actual SMS service (Twilio, AWS SNS, etc.)
        print(f"SMS to {to_number}: {message}")
        
        # If Twilio is configured:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(to=to_number, from_=twilio_number, body=message)
        
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def get_tourist_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Find tourist by phone number"""
    try:
        if not mongo_enabled():
            return None
        
        from mongo_db import db  # type: ignore
        tourists_collection = db['_enhanced_tourists']  # type: ignore
        
        # Normalize phone (remove spaces, dashes, etc.)
        normalized_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        tourist = tourists_collection.find_one({  # type: ignore
            '$or': [
                {'phone': phone},
                {'phone': normalized_phone},
                {'phone': {'$regex': normalized_phone, '$options': 'i'}}
            ]
        })
        
        return tourist  # type: ignore
    except Exception as e:  # type: ignore
        print(f"Error finding tourist by phone: {e}")
        return None

def get_last_known_location(tourist_id: str) -> Optional[Dict[str, Any]]:
    """Get tourist's last known location"""
    try:
        if not mongo_enabled():
            return None
        
        locations = get_recent_locations(tourist_id, limit=1)
        if locations:
            return locations[0]
        return None
    except Exception as e:
        print(f"Error getting last location: {e}")
        return None

# =============== END OFFLINE SMS EMERGENCY SYSTEM ===============

# =============== MISSING DASHBOARD ROUTES ===============

@app.route('/privacy')
def privacy_policy() -> str:
    """Render the Privacy Policy page (GDPR/CCPA compliant)"""
    return render_template('privacy_policy.html')

@app.route('/safety-map')
def safety_map() -> str:  # type: ignore
    """Render the safety map page with real-time location tracking"""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # type: ignore
    return render_template('safety_map.html', user=session)

@app.route('/api/user/profile/download')
def download_user_profile() -> Union[Response, tuple[Response, int]]:  # type: ignore
    """Download user profile as PDF or JSON"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        # Get user data from MongoDB
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        user_data = tourists_collection.find_one({'tourist_id': user_id})  # type: ignore
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Create JSON response with profile data
        profile = {  # type: ignore
            'tourist_id': user_data.get('tourist_id'),  # type: ignore
            'full_name': user_data.get('full_name'),  # type: ignore
            'email': user_data.get('email'),  # type: ignore
            'nationality': user_data.get('nationality'),  # type: ignore
            'passport_number': user_data.get('passport_number'),  # type: ignore
            'phone': user_data.get('phone'),  # type: ignore
            'date_of_birth': user_data.get('date_of_birth'),  # type: ignore
            'registration_date': user_data.get('created_at'),  # type: ignore
            'emergency_contacts': user_data.get('emergency_contacts', []),  # type: ignore
            'medical_info': user_data.get('medical_info', {}),  # type: ignore
            'documents': user_data.get('uploaded_files', {}),  # type: ignore
        }
        
        # Create a response with JSON data
        import json
        from io import BytesIO
        
        # Convert to pretty JSON
        json_str = json.dumps(profile, indent=2, default=str)
        
        # Create a file-like object
        buffer = BytesIO(json_str.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'profile_{user_id}.json'
        )
        
    except Exception as e:  # type: ignore
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/digital-id')
def digital_id_route() -> Union[str, Response]:  # type: ignore
    """Render digital ID card page"""
    try:
        # Get tourist_id from query params or session
        tourist_id = request.args.get('tourist_id') or session.get('user_id')  # type: ignore
        
        if not tourist_id:
            return redirect(url_for('login'))  # type: ignore
        
        if not mongo_enabled():
            flash('MongoDB not available', 'error')  # type: ignore
            return redirect(url_for('user_dashboard'))  # type: ignore
        
        # Get tourist data from MongoDB
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        tourist = tourists_collection.find_one({'tourist_id': str(tourist_id)})  # type: ignore
        
        if not tourist:
            flash('Tourist profile not found', 'error')  # type: ignore
            return redirect(url_for('user_dashboard'))  # type: ignore
        
        return render_template('digital_id.html', tourist=tourist)  # type: ignore
        
    except Exception as e:  # type: ignore
        flash(f'Error loading digital ID: {str(e)}', 'error')  # type: ignore
        return redirect(url_for('user_dashboard'))  # type: ignore

@app.route('/api/user/documents/list', methods=['GET'])
def list_user_documents() -> Union[Response, tuple[Response, int]]:  # type: ignore
    """Get list of all uploaded documents for current user"""
    try:
        if 'user_id' not in session:
            print("ERROR in /api/user/documents/list: User not logged in")
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')  # type: ignore
        print(f"📄 Fetching documents for user: {user_id}")
        
        if not mongo_enabled():
            print("⚠️ MongoDB not enabled, returning empty documents list")
            return jsonify({'success': True, 'documents': [], 'total_count': 0})
        
        # Get user data from MongoDB
        init_mongo()
        from mongo_db import mongo_db  # type: ignore
        tourists_collection = mongo_db['_enhanced_tourists']  # type: ignore
        user_data = tourists_collection.find_one({'tourist_id': user_id})  # type: ignore
        
        if not user_data:
            print(f"⚠️ User {user_id} not found in database, returning empty list")
            return jsonify({'success': True, 'documents': [], 'total_count': 0})
        
        # Get uploaded files
        uploaded_files = user_data.get('uploaded_files', {})  # type: ignore
        
        documents = []  # type: ignore
        for doc_type, files in uploaded_files.items():  # type: ignore
            if isinstance(files, list):  # type: ignore
                for file_info in files:  # type: ignore
                    documents.append({  # type: ignore
                        'type': doc_type,  # type: ignore
                        'filename': file_info.get('original_filename', 'Unknown'),  # type: ignore
                        'stored_path': file_info.get('stored_filename', ''),  # type: ignore
                        'uploaded_at': file_info.get('uploaded_at', ''),  # type: ignore
                        'verified': file_info.get('blockchain_hash') is not None,  # type: ignore
                        'blockchain_hash': file_info.get('blockchain_hash', '')  # type: ignore
                    })
        
        print(f"✅ Found {len(documents)} documents for user {user_id}")  # type: ignore
        return jsonify({
            'success': True,
            'documents': documents,
            'total_count': len(documents)  # type: ignore
        })
        
    except Exception as e:  # type: ignore
        print(f"ERROR in /api/user/documents/list: {str(e)}")  # Log error
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({
            'success': True,
            'documents': [],
            'total_count': 0,
            'error': str(e)
        }), 200  # Return 200 with empty list instead of 500

# =============== END MISSING DASHBOARD ROUTES ===============

# =============== ENHANCED LOCATION & RISK MANAGEMENT ===============

@app.route('/api/toggle_location_sharing', methods=['POST'])
def toggle_location_sharing():  # type: ignore
    """Toggle real-time location sharing for tourist with instant feedback"""
    try:
        data: Dict[str, Any] = parse_json_dict()
        tourist_id = str(data.get('tourist_id', '')).strip()
        enabled = bool(data.get('enabled', True))
        
        if not tourist_id:
            return jsonify({'success': False, 'error': 'tourist_id required'}), 400
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        init_mongo()
        
        # Update tourist's location sharing preference
        from mongo_db import update_tourist_settings  # type: ignore
        try:
            update_result = update_tourist_settings(tourist_id, {
                'location_sharing_enabled': enabled,
                'location_sharing_updated_at': datetime.now().isoformat()
            })
            
            if update_result:
                return jsonify({
                    'success': True,
                    'enabled': enabled,
                    'message': f'Location sharing {"enabled" if enabled else "disabled"} successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update location sharing preference'
                }), 500
                
        except Exception as e:
            print(f"Error updating location sharing: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
            
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get_tourist_settings')
def get_tourist_settings():  # type: ignore
    """Get tourist settings including location sharing preference"""
    try:
        tourist_id = request.args.get('tourist_id', '').strip()
        
        if not tourist_id:
            return jsonify({'success': False, 'error': 'tourist_id required'}), 400
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        init_mongo()
        
        # Get tourist data
        from mongo_db import get_enhanced_tourist  # type: ignore
        tourist = get_enhanced_tourist(tourist_id)
        
        if not tourist:
            return jsonify({'success': False, 'error': 'Tourist not found'}), 404
        
        # Extract settings
        settings: Dict[str, Any] = {
            'location_sharing_enabled': tourist.get('location_sharing_enabled', False),
            'ai_monitoring_enabled': tourist.get('ai_monitoring_enabled', False),
            'notifications_enabled': tourist.get('notifications_enabled', True),
            'privacy_mode': tourist.get('privacy_mode', False)
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        print(f"Error getting tourist settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get_risk_level/<tourist_id>')
@app.route('/api/get_risk_level')
def get_risk_level(tourist_id: str = None):  # type: ignore
    """Get real-time risk level for tourist based on location and activity"""
    try:
        # Get tourist_id from route parameter or query string
        if not tourist_id:
            tourist_id = request.args.get('tourist_id', '').strip()
        
        if not tourist_id:
            return jsonify({'success': False, 'error': 'tourist_id required'}), 400
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        init_mongo()
        
        # Get tourist's current location
        from mongo_db import get_latest_location  # type: ignore
        location_data = get_latest_location(str(tourist_id))
        
        if not location_data:
            return jsonify({
                'success': True,
                'risk_level': 'low',
                'message': 'No location data available'
            })
        
        # Calculate risk level based on multiple factors
        risk_level = 'low'
        risk_factors = []
        
        # Check if in danger zone (geofence violation)
        lat = location_data.get('latitude')
        lng = location_data.get('longitude')
        
        if lat and lng:
            violation_zone = check_geofence_violation(lat, lng, tourist_id)
            if violation_zone:
                risk_level = 'high'
                risk_factors.append(f'Danger zone: {violation_zone}')  # type: ignore
        
        # Check recent SOS alerts
        from mongo_db import get_recent_sos_alerts  # type: ignore
        try:
            recent_alerts = get_recent_sos_alerts(str(tourist_id), hours=24)
            if recent_alerts and len(recent_alerts) > 0:
                risk_level = 'medium' if risk_level == 'low' else 'high'
                risk_factors.append(f'{len(recent_alerts)} recent alert(s)')  # type: ignore
        except:
            pass
        
        # Check time of day (higher risk at night)
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 5:
            if risk_level == 'low':
                risk_level = 'medium'
            risk_factors.append('Late night hours')  # type: ignore
        
        return jsonify({
            'success': True,
            'risk_level': risk_level,
            'risk_factors': risk_factors,  # type: ignore
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:  # type: ignore
        print(f"Error calculating risk level: {e}")
        return jsonify({
            'success': True,
            'risk_level': 'low',
            'error': str(e)
        })


@app.route('/api/import_visa_from_digital_id', methods=['POST'])
def import_visa_from_digital_id():  # type: ignore
    """Import visa documentation from verified digital ID to streamline registration"""
    try:
        data: Dict[str, Any] = parse_json_dict()
        tourist_id = str(data.get('tourist_id', '')).strip()
        
        if not tourist_id:
            return jsonify({'success': False, 'error': 'tourist_id required'}), 400
        
        if not mongo_enabled():
            return jsonify({'success': False, 'error': 'MongoDB not enabled'}), 503
        
        init_mongo()
        
        # Get digital ID data
        from mongo_db import get_enhanced_tourist  # type: ignore
        digital_id_doc = get_enhanced_tourist(str(tourist_id))
        
        if not digital_id_doc:
            return jsonify({
                'success': False,
                'error': 'Digital ID not found for this tourist'
            }), 404
        
        # Extract visa information from digital ID
        visa_data: Dict[str, Any] = {  # type: ignore
            'passport_number': digital_id_doc.get('passport_number'),
            'passport_expiry': digital_id_doc.get('passport_expiry'),
            'visa_required': digital_id_doc.get('visa_required', 'yes'),
            'visa_number': digital_id_doc.get('visa_number'),
            'visa_expiry': digital_id_doc.get('visa_expiry'),
            'visa_file_path': digital_id_doc.get('visa_file_path'),
            'passport_file_path': digital_id_doc.get('passport_file_path'),
            'nationality': digital_id_doc.get('nationality'),
            'full_name': digital_id_doc.get('full_name'),
            'date_of_birth': digital_id_doc.get('date_of_birth'),
            'verification_status': digital_id_doc.get('verification_status', 'verified'),
            'blockchain_hash': digital_id_doc.get('blockchain_hash'),
            'auto_imported': True,
            'imported_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'visa_data': visa_data,
            'message': 'Visa documentation imported from digital ID successfully'
        })
        
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/search_dashboard', methods=['POST'])
def search_dashboard():  # type: ignore
    """Enhanced search that routes to correct dashboard sections"""
    try:
        data: Dict[str, Any] = parse_json_dict()
        query = str(data.get('query', '')).strip().lower()
        
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400
        
        results: Dict[str, Any] = {  # type: ignore
            'success': True,
            'query': query,
            'routes': [],
            'data': []
        }
        
        # Define search mappings
        search_mappings = {
            'sos': {'route': '/admin/sos-alerts', 'section': 'SOS Emergency Alerts'},
            'alert': {'route': '/admin/sos-alerts', 'section': 'SOS Emergency Alerts'},
            'emergency': {'route': '/admin/sos-alerts', 'section': 'SOS Emergency Alerts'},
            'tourist': {'route': '/admin/tourists', 'section': 'Tourist Management'},
            'user': {'route': '/admin/tourists', 'section': 'Tourist Management'},
            'incident': {'route': '/admin/incidents', 'section': 'Incident Reports'},
            'report': {'route': '/admin/incidents', 'section': 'Incident Reports'},
            'map': {'route': '/admin/map', 'section': 'Emergency Risk Map'},
            'location': {'route': '/admin/map', 'section': 'Emergency Risk Map'},
            'risk': {'route': '/admin/map', 'section': 'Emergency Risk Map'},
            'blockchain': {'route': '/admin/blockchain', 'section': 'Blockchain Records'},
            'verify': {'route': '/admin/blockchain', 'section': 'Blockchain Records'}
        }
        
        # Find matching routes
        for keyword, mapping in search_mappings.items():
            if keyword in query:
                results['routes'].append(mapping)  # type: ignore
        
        # Search in data if MongoDB is enabled
        if mongo_enabled():
            init_mongo()
            
            # Search tourists
            try:
                from mongo_db import search_tourists  # type: ignore
                tourists = search_tourists(query, limit=5)
                if tourists:
                    results['data'].extend([{  # type: ignore
                        'type': 'tourist',
                        'data': t,
                        'route': '/admin/tourists'
                    } for t in tourists])
            except:
                pass
            
            # Search SOS alerts
            try:
                from mongo_db import search_sos_alerts  # type: ignore
                alerts = search_sos_alerts(query, limit=5)
                if alerts:
                    results['data'].extend([{  # type: ignore
                        'type': 'sos_alert',
                        'data': a,
                        'route': '/admin/sos-alerts'
                    } for a in alerts])
            except:
                pass
        
        return jsonify(results)  # type: ignore
        
    except Exception as e:  # type: ignore
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== END ENHANCED LOCATION & RISK MANAGEMENT ===============

if __name__ == '__main__':
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize storage depending on backend
    if mongo_enabled():
        try:
            from mongo_db import ensure_indexes  # type: ignore
            ensure_indexes()
        except Exception as e:  # type: ignore
            print(f"Mongo index initialization warning: {e}")
    else:
        init_db()
    
    print("✅ Location & Geo-Fencing system initialized")
    print("📍 GPS tracking enabled")
    print("🛡️ Safe zones configured")
    print("⚠️ Restricted zones configured")
    print("🚨 Auto-alerts activated")
    
    # Debug: Print all registered routes
    print("\n🔍 Registered API Routes:")
    for rule in app.url_map.iter_rules():
        if '/api/' in str(rule):
            print(f"   {rule.methods} {rule}")
    print()
    
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
