"""Typed schema definitions for MongoDB documents.

These TypedDicts provide structured typing hints for core domain documents
used throughout the backend. They intentionally model only the fields
that are either required or commonly accessed in application code so that
static analysis (e.g. mypy / Pylance) can reduce "partially unknown"
warnings while preserving flexibility for additional dynamic fields.

All timestamps are ISO8601 UTC strings unless otherwise noted.
"""
from __future__ import annotations

from typing import TypedDict, NotRequired, List, Dict, Any

# ---------- Common Small Structures ----------

class GeoPoint(TypedDict):
    lat: float
    lng: float

class LocationReading(TypedDict, total=False):
    lat: float
    lng: float
    accuracy_m: NotRequired[float]
    speed_mps: NotRequired[float]
    heading_deg: NotRequired[float]
    timestamp: NotRequired[str]

class EmergencyContact(TypedDict, total=False):
    name: str
    relation: str
    phone: str
    email: NotRequired[str]

# ---------- Tourist / Registration ----------

class EnhancedTouristDoc(TypedDict, total=False):
    tourist_id: str
    full_name: str
    nationality: str
    date_of_birth: NotRequired[str]
    phone: NotRequired[str]
    email: NotRequired[str]
    passport_number: NotRequired[str]
    verification_status: NotRequired[str]
    blockchain_hash: NotRequired[str]
    verification_hash: NotRequired[str]
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    last_location: NotRequired[LocationReading]
    risk_score: NotRequired[float]
    medical_data_encrypted: NotRequired[str]
    emergency_contacts_encrypted: NotRequired[str]
    emergency_contacts: NotRequired[List[EmergencyContact]]

# ---------- Panic / SOS Alerts ----------

class PanicAlertDoc(TypedDict, total=False):
    alert_id: str
    tourist_id: str
    user_id: NotRequired[str]
    alert_type: str  # basic | enhanced | auto | emergency_sos
    status: str
    severity: NotRequired[str]
    location: NotRequired[LocationReading]
    created_at: str
    resolved_at: NotRequired[str]
    resolution_notes: NotRequired[str]

class AutoSOSDetectionDoc(TypedDict, total=False):
    detection_id: str
    tourist_id: str
    trigger_type: str
    model_version: NotRequired[str]
    confidence: NotRequired[float]
    created_at: str

# ---------- Geofence / Zone ----------

class ZoneDoc(TypedDict, total=False):
    zone_id: NotRequired[str]
    zone_name: str
    zone_type: str  # circular | polygon
    zone_category: NotRequired[str]
    center_lat: NotRequired[float]
    center_lng: NotRequired[float]
    radius_meters: NotRequired[int]
    polygon_coords: NotRequired[List[GeoPoint]]
    active: NotRequired[bool]
    created_at: NotRequired[str]

class ZoneBreachAlertDoc(TypedDict, total=False):
    breach_id: str
    tourist_id: str
    zone_name: str
    zone_type: str
    severity: str
    timestamp: str
    resolved: NotRequired[bool]

# ---------- AI Monitoring / Risk Alerts ----------

class RiskAlertDoc(TypedDict, total=False):
    alert_id: str
    tourist_id: str
    priority: str  # low | medium | high | critical
    category: NotRequired[str]
    message: str
    created_at: str
    acknowledged: NotRequired[bool]
    acknowledged_by: NotRequired[str]
    acknowledged_at: NotRequired[str]
    resolved: NotRequired[bool]
    resolved_at: NotRequired[str]
    resolution_notes: NotRequired[str]

class AIMonitoringResultDoc(TypedDict, total=False):
    result_id: str
    tourist_id: str
    analysis_type: str
    risk_score: float
    contributing_factors: NotRequired[List[str]]
    recommendations: NotRequired[List[str]]
    created_at: str

# ---------- Incident Response ----------

class DispatchDoc(TypedDict, total=False):
    dispatch_id: str
    incident_id: str
    service_type: str  # ambulance | police | fire | rescue | other
    status: str  # dispatched | en_route | arrived | completed
    last_location: NotRequired[LocationReading]
    updated_at: str
    created_at: str

class AuthorityVerificationDoc(TypedDict, total=False):
    verification_id: str
    incident_id: str
    authority_id: str
    authority_role: NotRequired[str]
    status: str  # pending | verified | rejected
    verified_at: NotRequired[str]
    notes: NotRequired[str]

class IncidentDoc(TypedDict, total=False):
    incident_id: str
    incident_type: str
    severity: str
    location: GeoPoint | LocationReading | Dict[str, Any]
    status: str  # active | resolved | closed
    description: NotRequired[str]
    created_at: str
    updated_at: str
    involved_tourists: NotRequired[List[str]]
    dispatches: NotRequired[List[DispatchDoc]]
    authority_verifications: NotRequired[List[AuthorityVerificationDoc]]
    blockchain_hash: NotRequired[str]

class IncidentActivityLogDoc(TypedDict, total=False):
    log_id: str
    incident_id: str
    activity_type: str
    message: str
    actor: NotRequired[str]
    timestamp: str
    metadata: NotRequired[Dict[str, Any]]

# ---------- Blockchain Records ----------

class BlockchainRecordDoc(TypedDict, total=False):
    sequence: int
    incident_id: NotRequired[str]
    record_type: str  # incident | activity | verification | generic
    payload_hash: str
    previous_hash: str
    chain_hash: str
    timestamp: str
    payload: Dict[str, Any]

# ---------- Reporting ----------

class PostIncidentReportDoc(TypedDict, total=False):
    report_id: str
    incident_id: str
    generated_by: str
    status: str  # generating | ready | failed
    sections: NotRequired[Dict[str, Any]]
    created_at: str
    updated_at: NotRequired[str]
    share_tokens: NotRequired[List[str]]

# ---------- Location / SOS Extensions ----------

class LocationTrackingDoc(TypedDict, total=False):
    tourist_id: str
    latitude: float
    longitude: float
    accuracy: NotRequired[float]
    altitude: NotRequired[float]
    speed: NotRequired[float]
    heading: NotRequired[float]
    location_method: NotRequired[str]
    battery_level: NotRequired[int]
    is_inside_safe_zone: NotRequired[bool]
    is_inside_restricted_zone: NotRequired[bool]
    zone_alerts_triggered: NotRequired[List[Dict[str, Any]]]
    timestamp: NotRequired[str]

class EmergencySOSDoc(TypedDict, total=False):
    sos_id: str
    user_id: NotRequired[str]
    tourist_id: NotRequired[str]
    emergency_type: NotRequired[str]
    message: NotRequired[str]
    severity: NotRequired[str]
    location_data: NotRequired[Dict[str, Any]]
    status: NotRequired[str]
    timestamp: NotRequired[str]

class AdminNotificationDoc(TypedDict, total=False):
    notification_id: str
    type: str
    title: str
    message: str
    priority: str
    created_at: str
    read: NotRequired[bool]
    read_at: NotRequired[str]

class PanicAlertMetrics(TypedDict, total=False):
    active_alerts: int
    alerts_today: int
    avg_severity: float

# ---------- Admin / Sessions ----------

class AdminSessionDoc(TypedDict, total=False):
    session_id: str
    admin_id: str
    login_timestamp: str
    logout_timestamp: NotRequired[str]
    ip_address: NotRequired[str]
    user_agent: NotRequired[str]
    device_info: NotRequired[str]
    session_status: str  # active | terminated | expired

class SecurityAuditLogDoc(TypedDict, total=False):
    log_id: str
    event_type: str
    actor_id: NotRequired[str]
    actor_role: NotRequired[str]
    ip_address: NotRequired[str]
    user_agent: NotRequired[str]
    message: str
    created_at: str

__all__ = [
    'GeoPoint','LocationReading','EmergencyContact','EnhancedTouristDoc','PanicAlertDoc','AutoSOSDetectionDoc',
    'ZoneDoc','ZoneBreachAlertDoc','RiskAlertDoc','AIMonitoringResultDoc','DispatchDoc','AuthorityVerificationDoc',
    'IncidentDoc','IncidentActivityLogDoc','BlockchainRecordDoc','PostIncidentReportDoc','AdminSessionDoc','SecurityAuditLogDoc'
]
