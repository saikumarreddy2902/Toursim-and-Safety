"""
Incident Response System
========================

This module implements comprehensive incident response including:
- Alert notifications to authorities (Police, Ambulance)
- Emergency contact notifications
- Blockchain digital ID verification for authorities
- Real-time help dispatch coordination

Features:
- Multi-channel alert distribution
- Authority verification via blockchain
- Real-time incident status tracking
- Emergency service coordination
- Automated escalation protocols
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor

# Feature flags (set defaults first to avoid redefinition warnings)
async_enabled: bool = False
blockchain_enabled: bool = False
blockchain_logging_enabled: bool = False

# Handle async imports gracefully
try:
    import asyncio
    import aiohttp  # type: ignore
    async_enabled = True
except Exception:
    # Ensure name binding to satisfy static analysis when asyncio isn't available
    asyncio = None  # type: ignore[assignment]
    async_enabled = False
    print("⚠️ Async libraries not available, using synchronous fallbacks")

# We provide local shims for verification; enable blockchain features by default
blockchain_enabled = True

# Local fallbacks/shims for verification and record hashing
import hashlib as _hashlib

def create_emergency_blockchain_record(payload: Dict[str, Any]) -> str:
    """Create a deterministic hash for an emergency verification payload.
    Acts as a local shim if no external blockchain helper is provided.
    """
    try:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return _hashlib.sha256(data).hexdigest()
    except Exception:
        return _hashlib.sha256(str(payload).encode()).hexdigest()

def verify_authority_identity(authority_id: str, digital_signature: str, blockchain_hash: str) -> Dict[str, Any]:
    """Lightweight signature check shim.
    NOTE: In production, replace with a real cryptographic verification.
    Current logic: consider verified if digital_signature non-empty and references authority_id.
    """
    ok = bool(digital_signature) and (str(authority_id) in str(digital_signature))
    return {
        'verified': ok,
        'authority_id': authority_id,
        'blockchain_hash': blockchain_hash,
    }

# Import blockchain incident logger
try:
    from blockchain_incident_logger import BlockchainIncidentLogger
    blockchain_logging_enabled = True
    print("✅ Blockchain incident logging system loaded")
except Exception:
    blockchain_logging_enabled = False
    BlockchainIncidentLogger = None  # type: ignore[assignment]
    print("⚠️ Blockchain incident logging not available")

class IncidentResponseSystem:
    """
    Comprehensive incident response coordination system
    """
    # Class-level attribute annotations for better type inference
    logger: logging.Logger
    executor: ThreadPoolExecutor
    blockchain_logger: Optional[Any]
    emergency_services: Dict[str, Dict[str, Any]]
    emergency_contact_settings: Dict[str, Any]
    dispatch_settings: Dict[str, Any]
    _mdb: Any
    
    def __init__(self, database_path: str):
        # database_path kept for legacy signature compatibility; Mongo is used
        self.database_path = database_path

        # Emergency service configurations
        self.emergency_services = {
            'police': {
                'priority': 'high',
                'response_time_target': 300,  # 5 minutes
                'notification_channels': ['sms', 'radio', 'app'],
                'verification_required': True,
            },
            'ambulance': {
                'priority': 'critical',
                'response_time_target': 240,  # 4 minutes
                'notification_channels': ['sms', 'radio', 'app', 'pager'],
                'verification_required': True,
            },
            'fire_department': {
                'priority': 'high',
                'response_time_target': 360,  # 6 minutes
                'notification_channels': ['sms', 'radio', 'app'],
                'verification_required': True,
            },
            'tourist_police': {
                'priority': 'medium',
                'response_time_target': 600,  # 10 minutes
                'notification_channels': ['sms', 'app'],
                'verification_required': False,
            },
        }

        # Emergency contact notification settings
        self.emergency_contact_settings = {
            'max_contacts': 5,
            'notification_interval': 120,  # 2 minutes between attempts
            'max_attempts': 3,
            'notification_channels': ['sms', 'call', 'email'],
        }

        # Real-time dispatch settings
        self.dispatch_settings = {
            'status_update_interval': 30,  # 30 seconds
            'location_update_interval': 60,  # 1 minute
            'response_tracking': True,
            'live_updates': True,
        }

        # MongoDB backend (initialize collections)
        try:
            from . import mongo_db as mdb  # package import
        except Exception:  # pragma: no cover
            import mongo_db as mdb  # fallback
        self._mdb = mdb
        try:
            self._mdb.init_mongo()
        except Exception:
            pass

        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize blockchain incident logger
        self.blockchain_logger = None
        if blockchain_logging_enabled and (BlockchainIncidentLogger is not None):
            try:
                self.blockchain_logger = BlockchainIncidentLogger(database_path)
                self.logger.info("✅ Blockchain incident logging initialized")
            except Exception as e:
                self.logger.error(f"⚠️ Failed to initialize blockchain logging: {e}")
                self.blockchain_logger = None
        # Seed emergency services into Mongo (idempotent)
        self._ensure_default_emergency_services()

    def _ensure_default_emergency_services(self) -> None:
        """Insert default emergency services into Mongo if missing."""
        try:
            from pymongo.collection import Collection  # type: ignore
        except Exception:
            Collection = object  # type: ignore
        try:
            _ = getattr(self._mdb, '_admins', None)  # touch to ensure mongo initialized
        except Exception:
            pass
        # We'll store static emergency services in a dedicated collection 'emergency_services'
        try:
            db = getattr(self._mdb, '_db', None)
            emergency_services = db['emergency_services'] if db is not None else None  # type: ignore[index]
        except Exception:
            emergency_services = None
        default_services: List[Dict[str, Any]] = [
            {
                'service_id': 'POLICE_001', 'service_type': 'police', 'service_name': 'Central Police Station',
                'contact_number': '112', 'contact_email': 'police@emergency.gov', 'radio_frequency': 'FREQ_155.5',
                'jurisdiction_area': 'City Center', 'response_capabilities': 'General Law Enforcement',
                'verification_public_key': None, 'active': True, 'created_at': datetime.now().isoformat()
            },
            {
                'service_id': 'AMB_001', 'service_type': 'ambulance', 'service_name': 'City Ambulance Service',
                'contact_number': '108', 'contact_email': 'ambulance@health.gov', 'radio_frequency': 'FREQ_462.5',
                'jurisdiction_area': 'Metropolitan Area', 'response_capabilities': 'Medical Emergency Response',
                'verification_public_key': None, 'active': True, 'created_at': datetime.now().isoformat()
            },
            {
                'service_id': 'FIRE_001', 'service_type': 'fire_department', 'service_name': 'City Fire Department',
                'contact_number': '101', 'contact_email': 'fire@emergency.gov', 'radio_frequency': 'FREQ_154.5',
                'jurisdiction_area': 'City Limits', 'response_capabilities': 'Fire and Rescue Operations',
                'verification_public_key': None, 'active': True, 'created_at': datetime.now().isoformat()
            },
            {
                'service_id': 'TPOL_001', 'service_type': 'tourist_police', 'service_name': 'Tourist Police Unit',
                'contact_number': '1363', 'contact_email': 'tourist.police@tourism.gov', 'radio_frequency': None,
                'jurisdiction_area': 'Tourist Areas', 'response_capabilities': 'Tourist Safety and Assistance',
                'verification_public_key': None, 'active': True, 'created_at': datetime.now().isoformat()
            }
        ]
        try:
            if emergency_services is not None:
                emergency_services.create_index('service_id', unique=True)  # type: ignore[attr-defined]
                for svc in default_services:
                    emergency_services.update_one({'service_id': svc['service_id']}, {'$setOnInsert': svc}, upsert=True)  # type: ignore[attr-defined]
        except Exception:
            pass
    
    async def handle_incident_response(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate comprehensive incident response
        
        Args:
            incident_data: Incident information including ID, type, location, severity
            
        Returns:
            Response coordination status and tracking information
        """
        if not async_enabled:
            # Fallback to synchronous mode
            return self._handle_incident_response_sync(incident_data)

        incident_id = str(incident_data.get('incident_id') or f"INC-{uuid.uuid4().hex[:8]}")
        incident_type = incident_data.get('incident_type', 'general_emergency')
        severity = incident_data.get('severity', 'medium')
        location = incident_data.get('location', {})
        tourist_id = incident_data.get('tourist_id')

        self.logger.info(f"🚨 Starting incident response for: {incident_id}")

        # Log incident to blockchain first
        if self.blockchain_logger:
            try:
                blockchain_record = self.blockchain_logger.log_incident_record(incident_data)
                self.logger.info(f"🔗 Incident recorded on blockchain: {blockchain_record['record_hash'][:16]}...")
            except Exception as e:
                self.logger.error(f"⚠️ Blockchain logging failed: {str(e)}")

        # Determine required emergency services
        required_services = self._determine_required_services(incident_type, severity)

        # Start concurrent response tasks
        tasks: List[Any] = []

        # Task 1: Alert authorities
        tasks.append(self._alert_authorities(incident_id, required_services, incident_data))

        # Task 2: Notify emergency contacts
        if tourist_id:
            tasks.append(self._notify_emergency_contacts(incident_id, tourist_id, incident_data))

        # Task 3: Initialize blockchain verification for authorities
        if blockchain_enabled:
            tasks.append(self._setup_authority_verification(incident_id, required_services))

        # Task 4: Start real-time dispatch tracking
        tasks.append(self._initialize_dispatch_tracking(incident_id, required_services, location))

        # Execute all tasks concurrently
        # For type checkers, ensure asyncio is not None here
        assert asyncio is not None
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Compile response status
        response_status: Dict[str, Any] = {
            'incident_id': incident_id,
            'response_initiated': True,
            'timestamp': datetime.now().isoformat(),
            'authorities_alerted': not isinstance(results[0], Exception),
            'emergency_contacts_notified': not isinstance(results[1], Exception) if tourist_id else False,
            'blockchain_verification_setup': not isinstance(results[2], Exception) if blockchain_enabled else False,
            'dispatch_tracking_active': not isinstance(results[3], Exception),
            'required_services': required_services,
            'estimated_response_times': self._calculate_response_times(required_services),
            'tracking_url': f"/api/incident/track/{incident_id}"
        }

        # Log any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Task {i} failed: {str(result)}")

        self.logger.info(f"✅ Incident response coordinated for: {incident_id}")
        return response_status
    
    def _handle_incident_response_sync(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous fallback for incident response when async is not available"""
        incident_id = str(incident_data.get('incident_id') or f"INC-{uuid.uuid4().hex[:8]}")
        incident_type = incident_data.get('incident_type', 'general_emergency')
        severity = incident_data.get('severity', 'medium')
        location = incident_data.get('location', {})
        tourist_id = incident_data.get('tourist_id')
        
        self.logger.info(f"🚨 Starting synchronous incident response for: {incident_id}")
        
        required_services = self._determine_required_services(incident_type, severity)
        
        # Execute tasks synchronously
        authorities_alerted: bool = False
        contacts_notified: bool = False
        dispatch_active: bool = False
        try:
            # Alert authorities
            self._alert_authorities_sync(incident_id, required_services, incident_data)
            authorities_alerted = True
        except Exception as e:
            self.logger.error(f"Authority alerts failed: {str(e)}")
            authorities_alerted = False
        
        try:
            # Notify emergency contacts
            if tourist_id:
                self._notify_emergency_contacts_sync(incident_id, tourist_id, incident_data)
                contacts_notified = True
            else:
                contacts_notified = False
        except Exception as e:
            self.logger.error(f"Emergency contact notification failed: {str(e)}")
            contacts_notified = False
        
        try:
            # Initialize dispatch tracking
            self._initialize_dispatch_tracking_sync(incident_id, required_services, location)
            dispatch_active = True
        except Exception as e:
            self.logger.error(f"Dispatch tracking failed: {str(e)}")
            dispatch_active = False
        
        response_status: Dict[str, Any] = {
            'incident_id': incident_id,
            'response_initiated': True,
            'timestamp': datetime.now().isoformat(),
            'authorities_alerted': authorities_alerted,
            'emergency_contacts_notified': contacts_notified,
            'blockchain_verification_setup': False,  # Not available in sync mode (separate task)
            'dispatch_tracking_active': dispatch_active,
            'required_services': required_services,
            'estimated_response_times': self._calculate_response_times(required_services),
            'tracking_url': f"/api/incident/track/{incident_id}"
        }
        
        self.logger.info(f"✅ Synchronous incident response coordinated for: {incident_id}")
        return response_status
    
    def _determine_required_services(self, incident_type: str, severity: str) -> List[str]:
        """Determine which emergency services are required"""
        services: List[str] = []
        
        # Base services for all incidents
        services.append('tourist_police')
        
        # Add services based on incident type
        if incident_type in ['medical_emergency', 'auto_sos', 'health_crisis']:
            services.append('ambulance')
            if severity in ['high', 'critical']:
                services.append('police')
        
        elif incident_type in ['security_threat', 'crime', 'assault']:
            services.append('police')
            if severity in ['high', 'critical']:
                services.append('ambulance')
        
        elif incident_type in ['fire', 'explosion', 'building_collapse']:
            services.extend(['fire_department', 'ambulance', 'police'])
        
        elif incident_type in ['natural_disaster', 'flood', 'earthquake']:
            services.extend(['fire_department', 'ambulance', 'police'])
        
        else:  # General emergency
            if severity in ['high', 'critical']:
                services.extend(['police', 'ambulance'])
            elif severity == 'medium':
                services.append('police')
        
        unique_services: List[str] = list(set(services))
        return unique_services  # Remove duplicates
    
    def _alert_authorities_sync(self, incident_id: str, required_services: List[str], incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of authority alerts"""
        alerts_sent: List[Dict[str, Any]] = []
        
        # Read emergency service details from Mongo collection
        try:
            db = getattr(self._mdb, '_db', None)
            emergency_services = db['emergency_services'] if db is not None else None  # type: ignore[index]
            if emergency_services is None:
                services: List[Dict[str, Any]] = []
            else:
                services = list(emergency_services.find({'service_type': {'$in': required_services}, 'active': True}))  # type: ignore[attr-defined]
        except Exception:
            services = []
        
        for service in services:
            service_id: str = str(service.get('service_id', ''))
            service_type_str: str = str(service.get('service_type', ''))
            service_name: str = str(service.get('service_name', ''))
            contact_number: Optional[str] = service.get('contact_number')
            contact_email: Optional[str] = service.get('contact_email')
            radio_freq: Optional[str] = service.get('radio_frequency')
            
            # Create alert for each notification channel
            service_config = self.emergency_services.get(service_type_str, {})
            channels = service_config.get('notification_channels', ['sms'])
            
            for channel in channels:
                alert_id = f"ALERT-{incident_id}-{service_id}-{channel}-{uuid.uuid4().hex[:8]}"
                
                # Create alert content
                alert_content = self._create_authority_alert_content(incident_data, service_type_str)
                
                # Store alert record in Mongo
                try:
                    self._mdb.insert_incident_alert({
                        'alert_id': alert_id,
                        'incident_id': incident_id,
                        'alert_type': 'authority_notification',
                        'recipient_type': 'emergency_service',
                        'recipient_id': service_id,
                        'alert_channel': channel,
                        'alert_content': alert_content,
                        'delivery_status': 'pending'
                    })
                except Exception:
                    pass
                
                # Send alert (simulate for now)
                delivery_status = self._send_authority_alert_sync(
                    channel, contact_number, contact_email, radio_freq, alert_content
                )
                
                # Update delivery status in Mongo
                try:
                    db = getattr(self._mdb, '_db', None)
                    ial = db['incident_alerts'] if db is not None else None  # type: ignore[index]
                    if ial is not None:
                        ial.update_one({'alert_id': alert_id}, {'$set': {
                            'delivery_status': delivery_status,
                            'delivery_timestamp': datetime.now().isoformat()
                        }})  # type: ignore[attr-defined]
                except Exception:
                    pass
                
                alerts_sent.append({
                    'alert_id': alert_id,
                    'service': service_name,
                    'channel': channel,
                    'status': delivery_status
                })
        
        return {'alerts_sent': alerts_sent, 'total_alerts': len(alerts_sent)}
    
    def _notify_emergency_contacts_sync(self, incident_id: str, tourist_id: int, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of emergency contact notification"""
        contacts_notified: List[Dict[str, Any]] = []
        
        # Get tourist's emergency contact from Mongo users/enhanced profiles
        try:
            user = self._mdb.get_user_by_id(str(tourist_id))
        except Exception:
            user = None
        user_data: Dict[str, Any] = cast(Dict[str, Any], user or {})
        contact_val: Optional[Any] = user_data.get('emergency_contact')
        if not contact_val:
            return {'contacts_notified': [], 'total_contacts': 0}
        
        # Build emergency contact list
        emergency_contacts: List[str] = []
        if isinstance(contact_val, str):
            try:
                parsed = json.loads(contact_val)
                if isinstance(parsed, list):
                    parsed_list: List[Any] = cast(List[Any], parsed)
                    for x in parsed_list:
                        emergency_contacts.append(str(x))
                else:
                    emergency_contacts.append(str(parsed))
            except Exception:
                emergency_contacts.append(contact_val)
        elif isinstance(contact_val, list):
            contact_list: List[Any] = cast(List[Any], contact_val)
            for x in contact_list:
                emergency_contacts.append(str(x))
        else:
            emergency_contacts.append(str(contact_val))
        
        # Send notifications to each contact
        for contact in emergency_contacts[:self.emergency_contact_settings['max_contacts']]:
            contact_type = 'phone' if contact.isdigit() or '+' in contact else 'email'
            
            for channel in self.emergency_contact_settings['notification_channels']:
                if (channel in ['sms', 'call'] and contact_type == 'phone') or \
                   (channel == 'email' and contact_type == 'email'):
                    
                    response_id = f"CONTACT-{incident_id}-{uuid.uuid4().hex[:8]}"
                    
                    # Create notification content
                    notification_content = self._create_emergency_contact_content(incident_data, tourist_id)
                    
                    # Store notification record in Mongo
                    try:
                        self._mdb.record_emergency_contact_response({
                            'response_id': response_id,
                            'incident_id': incident_id,
                            'contact_id': contact,
                            'contact_type': contact_type,
                            'notification_channel': channel,
                            'contact_response': notification_content,
                            'response_status': 'sent'
                        })
                    except Exception:
                        pass
                    
                    # Send notification (simulate for now)
                    status = self._send_emergency_contact_notification_sync(
                        channel, contact, notification_content
                    )
                    
                    # Update status in Mongo
                    try:
                        db = getattr(self._mdb, '_db', None)
                        ecr = db['emergency_contact_responses'] if db is not None else None  # type: ignore[index]
                        if ecr is not None:
                            ecr.update_one({'response_id': response_id}, {'$set': {'response_status': status}})  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    
                    contacts_notified.append({
                        'response_id': response_id,
                        'contact': contact,
                        'channel': channel,
                        'status': status
                    })
        
        return {'contacts_notified': contacts_notified, 'total_contacts': len(contacts_notified)}
    
    def _initialize_dispatch_tracking_sync(self, incident_id: str, required_services: List[str], location: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of dispatch tracking initialization"""
        dispatches_initialized: List[Dict[str, Any]] = []
        
        for service_type in required_services:
            dispatch_id = f"DISPATCH-{incident_id}-{service_type}-{uuid.uuid4().hex[:8]}"
            
            # Calculate estimated arrival time
            service_config = self.emergency_services.get(service_type, {})
            response_time = service_config.get('response_time_target', 600)
            estimated_arrival = datetime.now() + timedelta(seconds=response_time)
            
            # Initialize dispatch tracking in Mongo
            try:
                self._mdb.log_dispatch({
                    'dispatch_id': dispatch_id,
                    'incident_id': incident_id,
                    'service_type': service_type,
                    'dispatch_timestamp': datetime.now().isoformat(),
                    'estimated_arrival': estimated_arrival.isoformat(),
                    'response_status': 'dispatched'
                })
            except Exception:
                pass
            
            dispatches_initialized.append({
                'dispatch_id': dispatch_id,
                'service_type': service_type,
                'estimated_arrival': estimated_arrival.isoformat()
            })
        
        return {
            'dispatch_tracking_initialized': True,
            'dispatches': dispatches_initialized,
            'total_dispatches': len(dispatches_initialized)
        }
    
    def _send_authority_alert_sync(self, channel: str, phone: Optional[str], email: Optional[str], radio: Optional[str], content: Dict[str, Any]) -> str:
        """Synchronous version of authority alert sending"""
        try:
            # Simulate sending alert based on channel
            if channel == 'sms' and phone:
                self.logger.info(f"📱 SMS alert sent to {phone}")
                return 'delivered'
            elif channel == 'email' and email:
                self.logger.info(f"📧 Email alert sent to {email}")
                return 'delivered'
            elif channel == 'radio' and radio:
                self.logger.info(f"📻 Radio alert sent on {radio}")
                return 'delivered'
            elif channel == 'app':
                self.logger.info(f"📱 App notification sent")
                return 'delivered'
            else:
                return 'failed'
        except Exception as e:
            self.logger.error(f"Failed to send {channel} alert: {str(e)}")
            return 'failed'
    
    def _send_emergency_contact_notification_sync(self, channel: str, contact: str, content: Dict[str, Any]) -> str:
        """Synchronous version of emergency contact notification"""
        try:
            # Simulate sending notification
            if channel == 'sms':
                self.logger.info(f"📱 Emergency SMS sent to {contact}")
                return 'sent'
            elif channel == 'call':
                self.logger.info(f"📞 Emergency call initiated to {contact}")
                return 'sent'
            elif channel == 'email':
                self.logger.info(f"📧 Emergency email sent to {contact}")
                return 'sent'
            else:
                return 'failed'
        except Exception as e:
            self.logger.error(f"Failed to send {channel} notification: {str(e)}")
            return 'failed'
    
    async def _alert_authorities(self, incident_id: str, required_services: List[str], incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alerts to all required emergency services (Mongo-backed)."""
        alerts_sent: List[Dict[str, Any]] = []
        # Read emergency service details from Mongo collection
        try:
            db = getattr(self._mdb, '_db', None)
            emergency_services = db['emergency_services'] if db is not None else None  # type: ignore[index]
            if emergency_services is None:
                services: List[Dict[str, Any]] = []
            else:
                services = list(emergency_services.find({'service_type': {'$in': required_services}, 'active': True}))  # type: ignore[attr-defined]
        except Exception:
            services = []

        for service in services:
            service_id = service.get('service_id')
            service_type = service.get('service_type')
            service_name = service.get('service_name')
            contact_number = service.get('contact_number')
            contact_email = service.get('contact_email')
            radio_freq = service.get('radio_frequency')

            # Create alert for each notification channel
            service_config = self.emergency_services.get(str(service_type), {})
            channels = service_config.get('notification_channels', ['sms'])

            for channel in channels:
                alert_id = f"ALERT-{incident_id}-{service_id}-{channel}-{uuid.uuid4().hex[:8]}"
                # Create alert content
                alert_content = self._create_authority_alert_content(incident_data, str(service_type))
                # Store alert record in Mongo
                try:
                    self._mdb.insert_incident_alert({
                        'alert_id': alert_id,
                        'incident_id': incident_id,
                        'alert_type': 'authority_notification',
                        'recipient_type': 'emergency_service',
                        'recipient_id': service_id,
                        'alert_channel': channel,
                        'alert_content': alert_content,
                        'delivery_status': 'pending'
                    })
                except Exception:
                    pass
                # Send alert (simulate for now)
                delivery_status = await self._send_authority_alert(
                    channel, contact_number, contact_email, radio_freq, alert_content
                )
                # Update delivery status in Mongo
                try:
                    db = getattr(self._mdb, '_db', None)
                    ial = db['incident_alerts'] if db is not None else None  # type: ignore[index]
                    if ial is not None:
                        ial.update_one({'alert_id': alert_id}, {'$set': {
                            'delivery_status': delivery_status,
                            'delivery_timestamp': datetime.now().isoformat()
                        }})  # type: ignore[attr-defined]
                except Exception:
                    pass
                # Log activity to blockchain
                if self.blockchain_logger:
                    try:
                        self.blockchain_logger.log_response_activity(
                            incident_id, 'authority_alert',
                            {
                                'service_type': service_type,
                                'service_name': service_name,
                                'channel': channel,
                                'status': delivery_status,
                                'alert_id': alert_id
                            },
                            service_id, 'emergency_service'
                        )
                    except Exception as e:
                        self.logger.error(f"Blockchain activity logging failed: {str(e)}")
                alerts_sent.append({
                    'alert_id': alert_id,
                    'service': service_name,
                    'channel': channel,
                    'status': delivery_status
                })
        return {'alerts_sent': alerts_sent, 'total_alerts': len(alerts_sent)}
    
    async def _notify_emergency_contacts(self, incident_id: str, tourist_id: int, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Notify tourist's emergency contacts (Mongo-backed)."""
        contacts_notified: List[Dict[str, Any]] = []

        # Get tourist's emergency contact from Mongo users/enhanced profiles
        try:
            user = self._mdb.get_user_by_id(str(tourist_id))
        except Exception:
            user = None
        user_data: Dict[str, Any] = cast(Dict[str, Any], user or {})
        contact_val: Optional[Any] = user_data.get('emergency_contact')
        if not contact_val:
            return {'contacts_notified': [], 'total_contacts': 0}

        # Build emergency contact list
        emergency_contacts: List[str] = []
        if isinstance(contact_val, str):
            try:
                parsed = json.loads(contact_val)
                if isinstance(parsed, list):
                    for x in cast(List[Any], parsed):
                        emergency_contacts.append(str(x))
                else:
                    emergency_contacts.append(str(parsed))
            except Exception:
                emergency_contacts.append(contact_val)
        elif isinstance(contact_val, list):
            for x in cast(List[Any], contact_val):
                emergency_contacts.append(str(x))
        else:
            emergency_contacts.append(str(contact_val))

        # Send notifications to each contact
        for contact in emergency_contacts[: self.emergency_contact_settings['max_contacts']]:
            contact_type = 'phone' if contact.isdigit() or '+' in contact else 'email'

            for channel in self.emergency_contact_settings['notification_channels']:
                if (channel in ['sms', 'call'] and contact_type == 'phone') or (
                    channel == 'email' and contact_type == 'email'
                ):
                    response_id = f"CONTACT-{incident_id}-{uuid.uuid4().hex[:8]}"
                    # Create notification content
                    notification_content = self._create_emergency_contact_content(incident_data, tourist_id)
                    # Store notification record in Mongo
                    try:
                        self._mdb.record_emergency_contact_response({
                            'response_id': response_id,
                            'incident_id': incident_id,
                            'contact_id': contact,
                            'contact_type': contact_type,
                            'notification_channel': channel,
                            'contact_response': notification_content,
                            'response_status': 'sent'
                        })
                    except Exception:
                        pass
                    # Send notification (simulate for now)
                    status = await self._send_emergency_contact_notification(
                        channel, contact, notification_content
                    )
                    # Update status in Mongo
                    try:
                        db = getattr(self._mdb, '_db', None)
                        ecr = db['emergency_contact_responses'] if db is not None else None  # type: ignore[index]
                        if ecr is not None:
                            ecr.update_one({'response_id': response_id}, {'$set': {'response_status': status}})  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    # Log activity to blockchain
                    if self.blockchain_logger:
                        try:
                            self.blockchain_logger.log_response_activity(
                                incident_id,
                                'emergency_contact_notification',
                                {
                                    'contact_type': contact_type,
                                    'channel': channel,
                                    'status': status,
                                    'response_id': response_id,
                                },
                                f"contact_{contact}",
                                'emergency_contact',
                            )
                        except Exception as e:
                            self.logger.error(f"Blockchain contact logging failed: {str(e)}")
                    contacts_notified.append(
                        {
                            'response_id': response_id,
                            'contact': contact,
                            'channel': channel,
                            'status': status,
                        }
                    )

        return {'contacts_notified': contacts_notified, 'total_contacts': len(contacts_notified)}
    
    async def _setup_authority_verification(self, incident_id: str, required_services: List[str]) -> Dict[str, Any]:
        """Setup blockchain-based digital ID verification for authorities (Mongo-backed)."""
        if not blockchain_enabled:
            return {'verification_setup': False, 'reason': 'Blockchain not available'}

        verifications_created: List[Dict[str, Any]] = []
        try:
            db = getattr(self._mdb, '_db', None)
            emergency_services = db['emergency_services'] if db is not None else None  # type: ignore[index]
            if emergency_services is None:
                services_map: Dict[str, List[Dict[str, Any]]] = {}
            else:
                cur = list(emergency_services.find({'service_type': {'$in': required_services}, 'active': True}))  # type: ignore[attr-defined]
                services_map = {}
                for svc in cur:
                    services_map.setdefault(svc.get('service_type', ''), []).append(svc)
        except Exception:
            services_map = {}

        for service_type in required_services:
            for svc in services_map.get(service_type, []):
                service_id = svc.get('service_id')
                public_key = svc.get('verification_public_key')
                verification_id = f"VERIFY-{incident_id}-{service_id}-{uuid.uuid4().hex[:8]}"
                try:
                    # Create blockchain verification record hash
                    blockchain_hash = create_emergency_blockchain_record({
                        'incident_id': incident_id,
                        'authority_service': service_id,
                        'verification_id': verification_id,
                        'timestamp': datetime.now().isoformat(),
                        'public_key': public_key,
                    })
                    # Store verification record in Mongo
                    self._mdb.record_authority_verification({
                        'verification_id': verification_id,
                        'authority_id': service_id,
                        'authority_type': service_type,
                        'incident_id': incident_id,
                        'verification_status': 'pending',
                        'blockchain_hash': blockchain_hash,
                        'verification_data': {
                            'public_key': public_key,
                            'created_at': datetime.now().isoformat(),
                        },
                    })
                    verifications_created.append({
                        'verification_id': verification_id,
                        'service_id': service_id,
                        'blockchain_hash': blockchain_hash,
                    })
                except Exception as e:
                    self.logger.error(f"Failed to create blockchain verification for {service_id}: {str(e)}")

        return {
            'verification_setup': True,
            'verifications_created': verifications_created,
            'total_verifications': len(verifications_created),
        }
    
    async def _initialize_dispatch_tracking(self, incident_id: str, required_services: List[str], location: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize real-time dispatch tracking (Mongo-backed)."""
        dispatches_initialized: List[Dict[str, Any]] = []

        for service_type in required_services:
            dispatch_id = f"DISPATCH-{incident_id}-{service_type}-{uuid.uuid4().hex[:8]}"
            # Calculate estimated arrival time
            service_config = self.emergency_services.get(service_type, {})
            response_time = service_config.get('response_time_target', 600)
            estimated_arrival = datetime.now() + timedelta(seconds=response_time)
            # Initialize dispatch tracking in Mongo
            try:
                self._mdb.log_dispatch({
                    'dispatch_id': dispatch_id,
                    'incident_id': incident_id,
                    'service_type': service_type,
                    'dispatch_timestamp': datetime.now().isoformat(),
                    'estimated_arrival': estimated_arrival.isoformat(),
                    'response_status': 'dispatched',
                    'current_location_lat': (location or {}).get('latitude'),
                    'current_location_lng': (location or {}).get('longitude'),
                })
            except Exception:
                pass
            # Log dispatch to blockchain
            if self.blockchain_logger:
                try:
                    self.blockchain_logger.log_response_activity(
                        incident_id,
                        'service_dispatch_init',
                        {
                            'service_type': service_type,
                            'dispatch_id': dispatch_id,
                            'estimated_arrival': estimated_arrival.isoformat(),
                            'status': 'dispatched',
                        },
                        dispatch_id,
                        'emergency_service',
                    )
                except Exception as e:
                    self.logger.error(f"Blockchain dispatch logging failed: {str(e)}")
            dispatches_initialized.append(
                {
                    'dispatch_id': dispatch_id,
                    'service_type': service_type,
                    'estimated_arrival': estimated_arrival.isoformat(),
                }
            )

        return {
            'dispatch_tracking_initialized': True,
            'dispatches': dispatches_initialized,
            'total_dispatches': len(dispatches_initialized),
        }
    
    def _create_authority_alert_content(self, incident_data: Dict[str, Any], service_type: str) -> Dict[str, Any]:
        """Create alert content for emergency services"""
        return {
            'alert_type': 'EMERGENCY_INCIDENT',
            'incident_id': incident_data.get('incident_id'),
            'priority': self.emergency_services.get(service_type, {}).get('priority', 'medium'),
            'incident_type': incident_data.get('incident_type', 'general_emergency'),
            'severity': incident_data.get('severity', 'medium'),
            'location': incident_data.get('location', {}),
            'tourist_info': {
                'tourist_id': incident_data.get('tourist_id'),
                'identity_verified': incident_data.get('identity_verified', False)
            },
            'timestamp': datetime.now().isoformat(),
            'verification_required': self.emergency_services.get(service_type, {}).get('verification_required', False),
            'dispatch_instructions': f"Emergency response required for {service_type} service"
        }
    
    def _create_emergency_contact_content(self, incident_data: Dict[str, Any], tourist_id: int) -> Dict[str, Any]:
        """Create notification content for emergency contacts"""
        return {
            'notification_type': 'EMERGENCY_ALERT',
            'tourist_id': tourist_id,
            'incident_id': incident_data.get('incident_id'),
            'incident_type': incident_data.get('incident_type', 'Emergency Situation'),
            'severity': incident_data.get('severity', 'medium'),
            'location': incident_data.get('location', {}),
            'timestamp': datetime.now().isoformat(),
            'message': f"Emergency alert: Tourist {tourist_id} needs assistance. Emergency services have been notified.",
            'status_url': f"/api/incident/status/{incident_data.get('incident_id')}",
            'emergency_services_contacted': True
        }
    
    async def _send_authority_alert(self, channel: str, phone: Optional[str], email: Optional[str], radio: Optional[str], content: Dict[str, Any]) -> str:
        """Send alert to emergency service (simulated implementation)"""
        try:
            # Simulate sending alert based on channel
            if channel == 'sms' and phone:
                # SMS implementation would go here
                self.logger.info(f"📱 SMS alert sent to {phone}")
                return 'delivered'
            elif channel == 'email' and email:
                # Email implementation would go here
                self.logger.info(f"📧 Email alert sent to {email}")
                return 'delivered'
            elif channel == 'radio' and radio:
                # Radio dispatch implementation would go here
                self.logger.info(f"📻 Radio alert sent on {radio}")
                return 'delivered'
            elif channel == 'app':
                # Mobile app push notification would go here
                self.logger.info(f"📱 App notification sent")
                return 'delivered'
            else:
                return 'failed'
        except Exception as e:
            self.logger.error(f"Failed to send {channel} alert: {str(e)}")
            return 'failed'
    
    async def _send_emergency_contact_notification(self, channel: str, contact: str, content: Dict[str, Any]) -> str:
        """Send notification to emergency contact (simulated implementation)"""
        try:
            # Simulate sending notification
            if channel == 'sms':
                self.logger.info(f"📱 Emergency SMS sent to {contact}")
                return 'sent'
            elif channel == 'call':
                self.logger.info(f"📞 Emergency call initiated to {contact}")
                return 'sent'
            elif channel == 'email':
                self.logger.info(f"📧 Emergency email sent to {contact}")
                return 'sent'
            else:
                return 'failed'
        except Exception as e:
            self.logger.error(f"Failed to send {channel} notification: {str(e)}")
            return 'failed'
    
    def _calculate_response_times(self, required_services: List[str]) -> Dict[str, int]:
        """Calculate estimated response times for each service"""
        response_times: Dict[str, int] = {}
        for service in required_services:
            config = self.emergency_services.get(service, {})
            response_times[service] = config.get('response_time_target', 600)
        return response_times
    
    def get_incident_status(self, incident_id: str) -> Dict[str, Any]:
        """Get real-time incident response status"""
        # Assemble from Mongo
        alerts: List[Dict[str, Any]] = []
        try:
            for doc in self._mdb.list_incident_alerts(incident_id):
                alerts.append({
                    'type': doc.get('alert_type'),
                    'recipient': doc.get('recipient_type'),
                    'channel': doc.get('alert_channel'),
                    'status': doc.get('delivery_status'),
                    'sent_at': doc.get('sent_timestamp'),
                    'response_received': bool(doc.get('response_received', False))
                })
        except Exception:
            pass

        contact_responses: List[Dict[str, Any]] = []
        try:
            for doc in self._mdb.list_contact_responses(incident_id):
                contact_responses.append({
                    'contact': doc.get('contact_id'),
                    'channel': doc.get('notification_channel'),
                    'status': doc.get('response_status'),
                    'sent_at': doc.get('notification_timestamp'),
                    'acknowledged_at': doc.get('acknowledgment_timestamp') or doc.get('acknowledgement_timestamp')
                })
        except Exception:
            pass

        dispatch_status: List[Dict[str, Any]] = []
        try:
            for doc in self._mdb.list_dispatches(incident_id):
                loc = None
                lat = doc.get('current_location_lat')
                lng = doc.get('current_location_lng')
                if lat is not None and lng is not None:
                    loc = {'latitude': lat, 'longitude': lng}
                dispatch_status.append({
                    'service': doc.get('service_type'),
                    'status': doc.get('response_status'),
                    'estimated_arrival': doc.get('estimated_arrival'),
                    'actual_arrival': doc.get('actual_arrival'),
                    'current_location': loc
                })
        except Exception:
            pass

        verifications: List[Dict[str, Any]] = []
        try:
            for doc in self._mdb.list_authority_verifications(incident_id):
                verifications.append({
                    'authority': doc.get('authority_type') or doc.get('authority_id'),
                    'status': doc.get('verification_status'),
                    'blockchain_hash': doc.get('blockchain_hash'),
                    'verified_at': doc.get('verification_timestamp')
                })
        except Exception:
            pass
        
        return {
            'incident_id': incident_id,
            'alerts': alerts,
            'emergency_contacts': contact_responses,
            'dispatch_status': dispatch_status,
            'authority_verifications': verifications,
            'last_updated': datetime.now().isoformat()
        }
    
    async def verify_authority_access(self, authority_id: str, incident_id: str, digital_signature: str) -> Dict[str, Any]:
        """Verify authority access to incident using blockchain digital ID"""
        if not blockchain_enabled:
            return {
                'verified': False,
                'reason': 'Blockchain verification not available'
            }

        # Get verification record from Mongo
        av: Optional[Any] = None
        try:
            db = getattr(self._mdb, '_db', None)
            av = db['authority_verifications'] if db is not None else None  # type: ignore[index]
            result_doc: Optional[Dict[str, Any]] = av.find_one({'authority_id': authority_id, 'incident_id': incident_id}) if av is not None else None  # type: ignore[attr-defined]
        except Exception:
            result_doc = None
        if not result_doc:
            return {
                'verified': False,
                'reason': 'No verification record found'
            }

        verification_id: Optional[str] = cast(Optional[str], result_doc.get('verification_id'))
        blockchain_hash: Optional[str] = cast(Optional[str], result_doc.get('blockchain_hash'))

        try:
            # Verify digital signature using blockchain
            if not blockchain_hash:
                return {
                    'verified': False,
                    'reason': 'Missing blockchain hash for verification'
                }
            bh: str = blockchain_hash
            verification_result = verify_authority_identity(
                authority_id, digital_signature, bh
            )

            if verification_result.get('verified'):
                # Update verification status in Mongo
                try:
                    if av is not None:
                        update_filter: Dict[str, Any] = {'verification_id': verification_id} if verification_id else {'authority_id': authority_id, 'incident_id': incident_id}
                        av.update_one(update_filter, {'$set': {'verification_status': 'verified', 'verified_by': authority_id, 'verification_timestamp': datetime.now().isoformat()}})  # type: ignore[attr-defined]
                except Exception:
                    pass

                return {
                    'verified': True,
                    'verification_id': verification_id,
                    'authority_id': authority_id,
                    'verified_at': datetime.now().isoformat(),
                    'blockchain_hash': blockchain_hash
                }
            else:
                return {
                    'verified': False,
                    'reason': 'Digital signature verification failed'
                }

        except Exception as e:
            self.logger.error(f"Authority verification error: {str(e)}")
            return {
                'verified': False,
                'reason': f'Verification error: {str(e)}'
            }
        
    
    def update_dispatch_location(self, dispatch_id: str, location: Dict[str, Any]) -> bool:
        """Update real-time location of emergency service dispatch"""
        try:
            return self._mdb.update_dispatch(dispatch_id, {
                'current_location_lat': location.get('latitude'),
                'current_location_lng': location.get('longitude'),
                'last_update_timestamp': datetime.now().isoformat()
            })
        
        except Exception as e:
            self.logger.error(f"Failed to update dispatch location: {str(e)}")
            return False
    
    def mark_service_arrived(self, dispatch_id: str, arrival_location: Dict[str, Any]) -> bool:
        """Mark emergency service as arrived at incident location"""
        try:
            return self._mdb.mark_dispatch_arrived(dispatch_id, arrival_location)
        
        except Exception as e:
            self.logger.error(f"Failed to mark service arrival: {str(e)}")
            return False
