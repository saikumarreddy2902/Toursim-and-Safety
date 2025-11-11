"""
Auto SOS Detection System
========================

This module implements AI-powered automatic SOS detection that triggers when dangerous
situations are detected through the AI monitoring system.

Features:
- Automatic SOS trigger based on AI risk assessment
- Smart thresholds to prevent false positives
- Integration with existing manual SOS system
- Emergency escalation protocols
- Digital ID verification for emergency response
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TypedDict, cast
from mongo_db import (
    mongo_enabled,
    get_auto_sos_config,
    is_auto_sos_enabled as mongo_auto_sos_enabled,
    is_in_auto_sos_cooldown,
    cooldown_remaining_seconds,
    sustained_high_risk,
    create_auto_sos_event as mongo_create_auto_sos_event,
    update_auto_sos_event as mongo_update_auto_sos_event,
    auto_sos_statistics as mongo_auto_sos_statistics,
    get_recent_locations,
    get_enhanced_tourist,
    get_user_by_id,
    create_emergency_sos,
    store_incident_package,
)

class AutoSOSDetector:
    """Detects emergency situations and automatically triggers SOS alerts"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        
        # Auto SOS thresholds (configurable)
        class AutoSosThresholds(TypedDict):
            critical_risk_score: float
            high_risk_score: float
            sustained_risk_duration: int
            movement_anomaly_threshold: int
            confidence_threshold: float

        self.auto_sos_thresholds: AutoSosThresholds = {
            'critical_risk_score': 0.85,      # Immediate auto SOS
            'high_risk_score': 0.75,          # Auto SOS after confirmation period
            'sustained_risk_duration': 300,   # 5 minutes of sustained high risk
            'movement_anomaly_threshold': 3,   # Multiple severe anomalies
            'confidence_threshold': 0.7,      # Minimum confidence for auto trigger
        }
        
        # False positive prevention
        class FalsePositivePreventionCfg(TypedDict):
            cooldown_period: int
            verification_checks: bool
            tourist_confirmation_timeout: int
            location_verification: bool

        self.false_positive_prevention: FalsePositivePreventionCfg = {
            'cooldown_period': 1800,           # 30 minutes between auto SOS
            'verification_checks': True,       # Enable additional verification
            'tourist_confirmation_timeout': 60, # 1 minute for tourist to cancel
            'location_verification': True,     # Verify location makes sense
        }
        
        # Mongo is the only supported datastore for Auto SOS.
        # Legacy SQLite initialization is no-op now.
        self._initialize_auto_sos_tables()
    
    def _initialize_auto_sos_tables(self):
        """SQLite legacy initialization removed. Mongo-only mode; nothing to initialize here."""
        return
    
    def evaluate_auto_sos_trigger(self, ai_analysis_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate if an AI analysis result should trigger auto SOS
        
        Args:
            ai_analysis_result: Result from AI monitoring system
            
        Returns:
            Dict with auto SOS decision and details, or None if no trigger
        """
        
        # Normalize/cast tourist_id to int when possible
        tourist_id_raw: Any = ai_analysis_result.get('tourist_id')
        tourist_id: Optional[int] = None
        if isinstance(tourist_id_raw, int):
            tourist_id = tourist_id_raw
        elif isinstance(tourist_id_raw, str) and tourist_id_raw.isdigit():
            try:
                tourist_id = int(tourist_id_raw)
            except Exception:
                tourist_id = None
        _risk_level = ai_analysis_result.get('risk_level', 'low')
        risk_score = ai_analysis_result.get('risk_score', 0.0)
        confidence = ai_analysis_result.get('confidence', 0.0)
        monitoring_id_any: Any = ai_analysis_result.get('monitoring_id')
        monitoring_id: str = str(monitoring_id_any) if monitoring_id_any is not None else ''
        
        # Check if auto SOS is enabled
        if mongo_enabled():
            if not mongo_auto_sos_enabled():
                return None
        else:
            if not self._is_auto_sos_enabled():
                return None
        
        # Check cooldown period
        if tourist_id is not None:
            if mongo_enabled():
                if is_in_auto_sos_cooldown(str(tourist_id), self.false_positive_prevention['cooldown_period']):
                    return {
                        'trigger_decision': False,
                        'reason': 'Tourist in cooldown period',
                        'cooldown_remaining': cooldown_remaining_seconds(str(tourist_id), self.false_positive_prevention['cooldown_period'])
                    }
            elif self._is_in_cooldown_period(tourist_id):
                return {
                    'trigger_decision': False,
                    'reason': 'Tourist in cooldown period',
                    'cooldown_remaining': self._get_cooldown_remaining(tourist_id)
                }
        
        # Evaluate trigger conditions
        trigger_decision: bool = False
        trigger_type: Optional[str] = None
        trigger_reason: List[str] = []
        
        # Critical risk score - immediate trigger
        if risk_score >= self.auto_sos_thresholds['critical_risk_score'] and confidence >= self.auto_sos_thresholds['confidence_threshold']:
            trigger_decision = True
            trigger_type = 'critical_risk'
            trigger_reason.append(f'Critical risk score: {risk_score:.3f}')
        
        # High risk score with additional checks
        elif risk_score >= self.auto_sos_thresholds['high_risk_score'] and confidence >= self.auto_sos_thresholds['confidence_threshold']:
            # Check for sustained high risk
            if tourist_id is not None and (sustained_high_risk(str(tourist_id), self.auto_sos_thresholds['sustained_risk_duration'], self.auto_sos_thresholds['high_risk_score']) if mongo_enabled() else self._check_sustained_high_risk(tourist_id)):
                trigger_decision = True
                trigger_type = 'sustained_high_risk'
                trigger_reason.append(f'Sustained high risk: {risk_score:.3f}')
        
        # Multiple severe movement anomalies
        movement_analysis: Dict[str, Any] = ai_analysis_result.get('movement_analysis', {})
        severe_anomaly_count = self._count_severe_anomalies(movement_analysis)
        if severe_anomaly_count >= self.auto_sos_thresholds['movement_anomaly_threshold']:
            trigger_decision = True
            trigger_type = 'movement_anomalies'
            trigger_reason.append(f'Severe movement anomalies: {severe_anomaly_count}')
        
        # Environmental emergency indicators
        environmental_analysis: Dict[str, Any] = ai_analysis_result.get('environmental_analysis', {})
        if self._check_environmental_emergency(environmental_analysis):
            trigger_decision = True
            trigger_type = 'environmental_emergency'
            trigger_reason.append('Environmental emergency detected')
        
        if trigger_decision:
            # Require a valid tourist_id for event creation
            if tourist_id is None:
                return {
                    'trigger_decision': False,
                    'reason': 'Missing or invalid tourist_id for auto SOS event',
                    'risk_score': risk_score,
                    'confidence': confidence
                }
            # Create auto SOS event
            trig_type_str: str = trigger_type or 'unknown'
            if mongo_enabled():
                loc = cast(Dict[str, Any], ai_analysis_result.get('current_location') or {})
                created = mongo_create_auto_sos_event({
                    'tourist_id': str(tourist_id),
                    'user_id': ai_analysis_result.get('user_id'),
                    'trigger_type': trig_type_str,
                    'risk_score': risk_score,
                    'confidence': confidence,
                    'ai_monitoring_id': monitoring_id,
                    'location_lat': loc.get('latitude'),
                    'location_lng': loc.get('longitude'),
                    'location_accuracy': loc.get('accuracy'),
                    'trigger_reason': '; '.join(trigger_reason),
                })
                event_id = created['event_id']
            else:
                event_id = self._create_auto_sos_event(
                    tourist_id=tourist_id,
                    user_id=ai_analysis_result.get('user_id'),
                    trigger_type=trig_type_str,
                    risk_score=risk_score,
                    confidence=confidence,
                    monitoring_id=monitoring_id,
                    location=ai_analysis_result.get('current_location'),
                    trigger_reason='; '.join(trigger_reason)
                )
            
            return {
                'trigger_decision': True,
                'event_id': event_id,
                'trigger_type': trigger_type,
                'trigger_reason': trigger_reason,
                'risk_score': risk_score,
                'confidence': confidence,
                'requires_confirmation': trigger_type != 'critical_risk',
                'confirmation_timeout': self.false_positive_prevention['tourist_confirmation_timeout']
            }
        
        return {
            'trigger_decision': False,
            'reason': 'Thresholds not met',
            'risk_score': risk_score,
            'confidence': confidence
        }
    
    def _create_auto_sos_event(
        self,
        tourist_id: int,
        user_id: Optional[int],
        trigger_type: str,
        risk_score: float,
        confidence: float,
        monitoring_id: str,
        location: Optional[Dict[str, Any]],
        trigger_reason: str
    ) -> str:
        """Create a new auto SOS event (Mongo-only)."""
        loc = location or {}
        created = mongo_create_auto_sos_event({
            'tourist_id': str(tourist_id),
            'user_id': user_id,
            'trigger_type': trigger_type,
            'risk_score': risk_score,
            'confidence': confidence,
            'ai_monitoring_id': monitoring_id,
            'location_lat': loc.get('latitude'),
            'location_lng': loc.get('longitude'),
            'location_accuracy': loc.get('accuracy'),
            'trigger_reason': trigger_reason,
        })
        return created['event_id']
    
    def process_tourist_response(self, event_id: str, response: str) -> Dict[str, Any]:
        """
        Process tourist's response to auto SOS alert
        
        Args:
            event_id: Auto SOS event ID
            response: 'confirm' (escalate to SOS) or 'cancel' (false alarm)
            
        Returns:
            Dict with processing result
        """
        # Mongo-only implementation for processing response
        if not mongo_enabled():
            return {'success': False, 'error': 'MongoDB not enabled'}
        existing = mongo_update_auto_sos_event  # type: ignore[unused-ignore]
        # We need current event doc for coords
        from mongo_db import get_auto_sos_event  # local import to avoid circular at module load
        doc = get_auto_sos_event(event_id)
        if not doc or doc.get('status') != 'pending':
            return {'success': False, 'error': 'Event not found or already processed'}
        tourist_id = doc.get('tourist_id')
        lat = doc.get('location_lat')
        lng = doc.get('location_lng')
        if response == 'confirm':
            manual = create_emergency_sos({
                'tourist_id': tourist_id,
                'latitude': lat,
                'longitude': lng,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'ACTIVE',
                'alert_type': 'auto_ai_detection',
                'trigger_source': 'auto_sos',
                'auto_sos_event_id': event_id,
            })
            mongo_update_auto_sos_event(event_id, {
                'status': 'escalated',
                'tourist_response': 'confirm',
                'tourist_response_timestamp': datetime.now(timezone.utc).isoformat(),
                'auto_escalated': True,
                'escalation_timestamp': datetime.now(timezone.utc).isoformat(),
                'manual_sos_id': manual.get('sos_id'),
            })
            return {
                'success': True,
                'action': 'escalated',
                'manual_sos_id': manual.get('sos_id'),
                'message': 'Auto SOS escalated to emergency services'
            }
        elif response == 'cancel':
            mongo_update_auto_sos_event(event_id, {
                'status': 'cancelled',
                'tourist_response': 'cancel',
                'tourist_response_timestamp': datetime.now(timezone.utc).isoformat(),
                'resolved': True,
                'resolution_timestamp': datetime.now(timezone.utc).isoformat(),
                'resolution_notes': 'Cancelled by tourist - false alarm',
            })
            return {
                'success': True,
                'action': 'cancelled',
                'message': 'Auto SOS cancelled by tourist'
            }
        else:
            return {'success': False, 'error': 'Invalid response'}
    
    def auto_escalate_expired_events(self) -> List[Dict[str, Any]]:
        """
        Auto-escalate events that have exceeded the confirmation timeout
        
        Returns:
            List of escalated events
        """
        
        if not mongo_enabled():
            return []
        timeout_seconds = self.false_positive_prevention['tourist_confirmation_timeout']
        from mongo_db import find_pending_auto_sos_older_than  # local import
        expired = find_pending_auto_sos_older_than(timeout_seconds)
        escalated_events: List[Dict[str, Any]] = []
        for e in expired:
            manual = create_emergency_sos({
                'tourist_id': e.get('tourist_id'),
                'latitude': e.get('location_lat'),
                'longitude': e.get('location_lng'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'ACTIVE',
                'alert_type': 'auto_ai_detection',
                'trigger_source': 'auto_sos',
                'auto_sos_event_id': e.get('event_id'),
            })
            evt_id = e.get('event_id')
            if not evt_id:
                continue
            mongo_update_auto_sos_event(str(evt_id), {
                'status': 'auto_escalated',
                'auto_escalated': True,
                'escalation_timestamp': datetime.now(timezone.utc).isoformat(),
                'manual_sos_id': manual.get('sos_id'),
                'resolution_notes': 'Auto-escalated due to timeout',
            })
            escalated_events.append({
                'event_id': evt_id,
                'tourist_id': e.get('tourist_id'),
                'manual_sos_id': manual.get('sos_id'),
                'reason': 'timeout',
            })
        return escalated_events
    
    def _create_manual_sos_from_auto(self, auto_event_id: str, tourist_id: int, lat: float, lng: float) -> str:
        """Create a manual SOS entry from auto SOS event"""
        
        # Legacy path no longer used; we keep the signature for compatibility
        created = create_emergency_sos({
            'tourist_id': str(tourist_id),
            'latitude': lat,
            'longitude': lng,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'ACTIVE',
            'alert_type': 'auto_ai_detection',
            'trigger_source': 'auto_sos',
            'auto_sos_event_id': auto_event_id,
        })
        return str(created.get('sos_id'))
    
    def _is_auto_sos_enabled(self) -> bool:
        """Check if auto SOS is enabled"""
        return bool(get_auto_sos_config().get('auto_sos_enabled', True))
    
    def _is_in_cooldown_period(self, tourist_id: int) -> bool:
        """Check if tourist is in cooldown period"""
        return is_in_auto_sos_cooldown(str(tourist_id), self.false_positive_prevention['cooldown_period'])
    
    def _get_cooldown_remaining(self, tourist_id: int) -> int:
        """Get remaining cooldown time in seconds"""
        return cooldown_remaining_seconds(str(tourist_id), self.false_positive_prevention['cooldown_period'])
    
    def _check_sustained_high_risk(self, tourist_id: int) -> bool:
        """Check if tourist has sustained high risk over time"""
        return sustained_high_risk(str(tourist_id), self.auto_sos_thresholds['sustained_risk_duration'], self.auto_sos_thresholds['high_risk_score'])
    
    def _count_severe_anomalies(self, movement_analysis: Dict[str, Any]) -> int:
        """Count severe movement anomalies"""
        severe_count = 0
        
        # Count sudden stops with high severity
        sudden_stops = movement_analysis.get('sudden_stops', {})
        for stop in sudden_stops.get('details', []):
            if stop.get('severity') == 'high':
                severe_count += 1
        
        # Count rapid movements with high severity
        rapid_movements = movement_analysis.get('rapid_movements', {})
        for movement in rapid_movements.get('details', []):
            if movement.get('severity') == 'high':
                severe_count += 1
        
        # Count abnormal patterns
        abnormal_patterns = movement_analysis.get('abnormal_patterns', {})
        if abnormal_patterns.get('confidence', 0) > 0.8:
            severe_count += abnormal_patterns.get('abnormal_patterns', 0)
        
        return severe_count
    
    def _check_environmental_emergency(self, environmental_analysis: Dict[str, Any]) -> bool:
        """Check for environmental emergency indicators"""
        risk_factors = environmental_analysis.get('risk_factors', [])
        
        for factor in risk_factors:
            if factor.get('severity') == 'high' and factor.get('type') in ['extreme_heat', 'severe_weather', 'infrastructure']:
                return True
        
        return environmental_analysis.get('total_risk_score', 0) > 0.8
    
    def get_auto_sos_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get auto SOS system statistics"""
        return mongo_auto_sos_statistics(hours)


class IncidentPackager:
    """Packages incident data for emergency response"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
    
    def create_incident_package(
        self,
        incident_type: str,
        tourist_id: int,
        incident_id: str,
        location: Dict[str, Any],
        ai_analysis: Optional[Dict[str, Any]] = None,
        auto_sos_event: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive incident package for emergency response
        
        Args:
            incident_type: Type of incident ('manual_sos', 'auto_sos', 'panic_alert')
            tourist_id: ID of tourist in distress
            incident_id: Unique incident identifier
            location: Current location data
            ai_analysis: AI monitoring analysis results
            auto_sos_event: Auto SOS event data if applicable
            
        Returns:
            Comprehensive incident package
        """
        
        # Get tourist digital identity
        digital_id = self._get_digital_identity(tourist_id)
        
        # Get live GPS data
        live_gps = self._get_live_gps_data(tourist_id, location)
        
        # Get risk assessment
        risk_assessment = self._get_risk_assessment(tourist_id, ai_analysis)
        
        # Get emergency contacts
        emergency_contacts = self._get_emergency_contacts(tourist_id)
        
        # Get medical information
        medical_info = self._get_medical_information(tourist_id)
        
        # Package all data
        incident_package: Dict[str, Any] = {
            'incident_metadata': {
                'incident_id': incident_id,
                'incident_type': incident_type,
                'timestamp': datetime.now().isoformat(),
                'severity': self._determine_severity(risk_assessment, auto_sos_event),
                'priority': self._determine_priority(incident_type, risk_assessment),
                'verification_status': 'verified' if digital_id['verified'] else 'unverified'
            },
            'digital_identity': digital_id,
            'live_gps_location': live_gps,
            'risk_assessment': risk_assessment,
            'emergency_contacts': emergency_contacts,
            'medical_information': medical_info,
            'ai_analysis': ai_analysis,
            'auto_sos_data': auto_sos_event,
            'response_recommendations': self._generate_response_recommendations(
                incident_type, risk_assessment, location, medical_info
            )
        }
        
        # Store incident package
        self._store_incident_package(incident_package)
        
        return incident_package
    
    def _get_digital_identity(self, tourist_id: int) -> Dict[str, Any]:
        """Get verified digital identity information"""
        # Use Mongo data to construct a minimal digital identity payload
        user = get_user_by_id(str(tourist_id))
        enhanced = get_enhanced_tourist(str(tourist_id))
        if user or enhanced:
            return {
                'verified': True,
                'verification_status': 'verified',
                'verification_timestamp': datetime.now().isoformat(),
                'identity_data': {
                    'full_name': (enhanced or {}).get('full_name') or user.get('full_name') if user else None,
                    'id_type': (enhanced or {}).get('id_type'),
                    'id_number': (enhanced or {}).get('id_number'),
                    'emergency_contact': (enhanced or {}).get('emergency_contact') or user.get('emergency_contact') if user else None,
                },
                'contact_data': {
                    'username': user.get('username') if user else None,
                    'email': user.get('email') if user else None,
                    'phone_number': user.get('phone_number') if user else None,
                    'user_id': user.get('user_id') if user else None,
                }
            }
        return {
            'verified': False,
            'verification_status': 'unverified',
            'verification_timestamp': None,
            'identity_data': {},
            'contact_data': {}
        }
    
    def _get_live_gps_data(self, tourist_id: int, current_location: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive live GPS location data"""
        # Pull recent locations from Mongo
        history = get_recent_locations(str(tourist_id), limit=10)
        location_history: List[Dict[str, Any]] = []
        for row in history:
            location_history.append({
                'latitude': row.get('latitude'),
                'longitude': row.get('longitude'),
                'timestamp': row.get('timestamp'),
                'accuracy': row.get('accuracy'),
                'speed': row.get('speed'),
                'heading': row.get('heading'),
            })
        
        return {
            'current_location': {
                'latitude': current_location.get('latitude'),
                'longitude': current_location.get('longitude'),
                'accuracy': current_location.get('accuracy', 0),
                'timestamp': datetime.now().isoformat(),
                'altitude': current_location.get('altitude'),
                'speed': current_location.get('speed'),
                'heading': current_location.get('heading')
            },
            'location_history': location_history,
            'location_confidence': self._calculate_location_confidence(current_location),
            'geographic_context': self._get_geographic_context(current_location),
            'nearest_landmarks': self._get_nearest_landmarks(current_location),
            'emergency_services_nearby': self._get_nearby_emergency_services(current_location)
        }
    
    def _get_risk_assessment(self, tourist_id: int, ai_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get comprehensive risk assessment"""
        if ai_analysis:
            return {
                'current_risk_level': ai_analysis.get('risk_level', 'unknown'),
                'risk_score': ai_analysis.get('risk_score', 0.0),
                'confidence': ai_analysis.get('confidence', 0.0),
                'risk_factors': ai_analysis.get('risk_factors', []),
                'movement_analysis': ai_analysis.get('movement_analysis', {}),
                'environmental_analysis': ai_analysis.get('environmental_analysis', {}),
                'recommendations': ai_analysis.get('recommendations', [])
            }
        else:
            return {
                'current_risk_level': 'unknown',
                'risk_score': 0.0,
                'confidence': 0.0,
                'risk_factors': [],
                'note': 'No AI analysis available'
            }
    
    def _get_emergency_contacts(self, tourist_id: int) -> List[Dict[str, Any]]:
        """Get emergency contact information"""
        user = get_user_by_id(str(tourist_id))
        contact = (user or {}).get('emergency_contact') if user else None
        if contact:
            return [{ 'contact_type': 'primary', 'contact_info': contact, 'verified': False }]
        return []
    
    def _get_medical_information(self, tourist_id: int) -> Dict[str, Any]:
        """Get medical information for emergency response"""
        enhanced = get_enhanced_tourist(str(tourist_id))
        if enhanced:
            return {
                'medical_conditions': enhanced.get('medical_conditions'),
                'allergies': enhanced.get('allergies'),
                'medications': enhanced.get('medications'),
                'blood_type': enhanced.get('blood_type'),
                'emergency_medical_contact': enhanced.get('emergency_medical_contact'),
                'available': True,
            }
        return { 'available': False }
    
    def _determine_severity(self, risk_assessment: Dict[str, Any], auto_sos_event: Optional[Dict[str, Any]]) -> str:
        """Determine incident severity"""
        risk_level = risk_assessment.get('current_risk_level', 'unknown')
        risk_score = risk_assessment.get('risk_score', 0.0)
        
        if auto_sos_event and auto_sos_event.get('trigger_type') == 'critical_risk':
            return 'critical'
        elif risk_level == 'high' or risk_score > 0.8:
            return 'high'
        elif risk_level == 'medium' or risk_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _determine_priority(self, incident_type: str, risk_assessment: Dict[str, Any]) -> str:
        """Determine response priority"""
        if incident_type == 'auto_sos':
            return 'urgent'
        elif incident_type == 'manual_sos':
            return 'immediate'
        elif risk_assessment.get('current_risk_level') == 'high':
            return 'high'
        else:
            return 'normal'
    
    def _calculate_location_confidence(self, location: Dict[str, Any]) -> float:
        """Calculate confidence in location accuracy"""
        accuracy = location.get('accuracy', 1000)  # meters
        
        if accuracy <= 5:
            return 0.95
        elif accuracy <= 20:
            return 0.85
        elif accuracy <= 100:
            return 0.7
        else:
            return 0.5
    
    def _get_geographic_context(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get geographic context for the location"""
        # This would integrate with mapping services
        return {
            'area_type': 'urban',  # Would be determined by geocoding
            'safety_rating': 'medium',
            'tourist_area': True,
            'accessibility': 'good'
        }
    
    def _get_nearest_landmarks(self, location: Dict[str, Any]) -> List[str]:
        """Get nearest recognizable landmarks"""
        # This would integrate with mapping services
        return [
            'Central Park',
            'Metro Station - 200m',
            'Hotel Grand - 500m'
        ]
    
    def _get_nearby_emergency_services(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get nearby emergency services information"""
        # This would integrate with emergency services databases
        return {
            'nearest_hospital': 'City General Hospital - 2.5km',
            'nearest_police': 'Police Station - 1.2km',
            'nearest_fire': 'Fire Station - 1.8km',
            'emergency_numbers': {
                'all_services': '112',
                'police': '100',
                'ambulance': '108',
                'fire': '101'
            }
        }
    
    def _generate_response_recommendations(
        self,
        incident_type: str,
        risk_assessment: Dict[str, Any],
        location: Dict[str, Any],
        medical_info: Dict[str, Any]
    ) -> List[str]:
        """Generate response recommendations for emergency services"""
        recommendations: List[str] = []
        
        if incident_type == 'auto_sos':
            recommendations.append('AI-detected emergency - immediate response recommended')
        
        if risk_assessment.get('current_risk_level') == 'high':
            recommendations.append('High risk situation - deploy emergency response team')
        
        if medical_info.get('available'):
            recommendations.append('Medical information available - review before response')
        
        if location.get('accuracy', 1000) > 100:
            recommendations.append('Location accuracy low - may need triangulation')
        
        return recommendations
    
    def _store_incident_package(self, package: Dict[str, Any]) -> None:
        """Store incident package in database"""
        # Store in Mongo
        store_incident_package(package)