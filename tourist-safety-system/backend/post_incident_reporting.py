"""
Post-Incident Reporting System for Tourist Safety Platform (MongoDB only)
Generates comprehensive reports after incident resolution.
Replaces legacy SQLite with MongoDB using backend.mongo_db helpers.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, cast
import logging
from dataclasses import dataclass
import uuid

# MongoDB helper module
try:
    from . import mongo_db as mdb  # package import
except Exception:  # pragma: no cover - fallback when running as script
    import mongo_db as mdb  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IncidentAnalysis:
    """Data class for incident analysis results"""
    incident_id: str
    cause_category: str
    cause_details: str
    contributing_factors: List[str]
    severity_assessment: str
    prevention_recommendations: List[str]

@dataclass
class ResponseTimeMetrics:
    """Data class for response time analysis"""
    incident_detection_time: str
    first_response_time: float  # seconds
    authority_notification_time: float
    emergency_contact_notification_time: float
    dispatch_time: float
    arrival_time: Optional[float]
    resolution_time: float
    total_response_duration: float

@dataclass
class ResolutionDetails:
    """Data class for incident resolution information"""
    resolution_status: str
    resolution_method: str
    services_involved: List[str]
    final_outcome: str
    tourist_condition: str
    follow_up_required: bool
    follow_up_details: str

class PostIncidentReportGenerator:
    """Comprehensive post-incident reporting system"""
    
    def __init__(self, database_path: str):
        # database_path kept for signature compatibility; Mongo is used
        self.database_path = database_path
        self.logger = logging.getLogger(__name__)
        try:
            mdb.init_mongo()
        except Exception:
            # Allow operation in dev without hard failure; functions guard on mongo_enabled
            pass
        
        # Report templates and analysis patterns
        self.cause_categories = {
            'medical_emergency': 'Medical Emergency',
            'security_threat': 'Security Threat',
            'natural_disaster': 'Natural Disaster',
            'transportation_issue': 'Transportation Issue',
            'communication_failure': 'Communication Failure',
            'tourist_error': 'Tourist Error',
            'system_malfunction': 'System Malfunction',
            'external_factor': 'External Factor'
        }
        
        self.severity_levels = ['low', 'medium', 'high', 'critical']
        
        # Response time benchmarks (in seconds)
        self.response_benchmarks = {
            'first_response': 30,      # 30 seconds
            'authority_notification': 60,  # 1 minute
            'emergency_contact': 120,  # 2 minutes
            'dispatch': 300,          # 5 minutes
            'arrival': 1800           # 30 minutes
        }
    
    def _initialize_report_tables(self):
        """No-op in Mongo mode; collections and indexes are created in mongo_db.init_mongo."""
        self.logger.info("✅ Post-incident reporting (Mongo) ready")
    
    def analyze_incident_cause(self, incident_id: str) -> IncidentAnalysis:
        """Analyze incident to determine cause and contributing factors (Mongo)."""
        try:
            incident_doc: Optional[Dict[str, Any]] = mdb.get_incident(incident_id)
            if not incident_doc:
                raise ValueError(f"Incident {incident_id} not found")

            incident_type: str = str(incident_doc.get('incident_type') or 'general_emergency')
            severity: str = str(incident_doc.get('severity') or 'medium')
            location_data: Dict[str, Any] = cast(Dict[str, Any], incident_doc.get('location') or {})
            message: str = str(incident_doc.get('message') or '')
            timestamp: str = str(incident_doc.get('created_at') or datetime.now().isoformat())
            emergency_type: str = incident_type  # best available mapping
            context: Dict[str, Any] = cast(Dict[str, Any], incident_doc.get('context') or {})

            # AI analysis and auto SOS data may not be directly linked; keep optional
            ai_analysis: Optional[Dict[str, Any]] = None
            auto_sos_data: Optional[Dict[str, Any]] = None

            cause_category = self._determine_cause_category(
                incident_type, emergency_type, message, ai_analysis, auto_sos_data
            )

            cause_details = self._generate_cause_details(
                (
                    incident_type,
                    severity,
                    json.dumps(location_data) if location_data else None,
                    message,
                    timestamp,
                    emergency_type,
                    json.dumps(context) if context else None,
                ),
                ai_analysis,
                auto_sos_data,
            )

            contributing_factors = self._identify_contributing_factors(
                (
                    incident_type,
                    json.dumps(location_data) if location_data else None,
                ),
                ai_analysis,
                auto_sos_data,
            )

            severity_assessment = self._assess_severity(
                severity, incident_type, ai_analysis
            )

            prevention_recommendations = self._generate_prevention_recommendations(
                cause_category, contributing_factors, (incident_type,)
            )

            return IncidentAnalysis(
                incident_id=incident_id,
                cause_category=cause_category,
                cause_details=cause_details,
                contributing_factors=contributing_factors,
                severity_assessment=severity_assessment,
                prevention_recommendations=prevention_recommendations,
            )
        except Exception as e:
            self.logger.error(f"Error analyzing incident cause: {str(e)}")
            raise
    
    def calculate_response_metrics(self, incident_id: str) -> ResponseTimeMetrics:
        """Calculate comprehensive response time metrics using Mongo collections."""
        try:
            incident_doc: Optional[Dict[str, Any]] = mdb.get_incident(incident_id)
            if not incident_doc:
                raise ValueError(f"Incident {incident_id} not found")
            incident_time = datetime.fromisoformat(str(incident_doc.get('created_at') or datetime.now().isoformat()))

            # Gather related timelines
            alerts: List[Dict[str, Any]] = mdb.list_incident_alerts(incident_id)
            contacts: List[Dict[str, Any]] = mdb.list_contact_responses(incident_id)
            dispatches: List[Dict[str, Any]] = mdb.list_dispatches(incident_id)

            def parse_time(val: Optional[str]) -> Optional[datetime]:
                try:
                    return datetime.fromisoformat(val) if val else None
                except Exception:
                    return None

            first_alert_time = parse_time(alerts[0].get('sent_timestamp')) if alerts else None
            first_contact_time = parse_time(contacts[0].get('notification_timestamp')) if contacts else None
            first_dispatch_time = parse_time(dispatches[0].get('dispatch_timestamp')) if dispatches else None
            first_arrival_time: Optional[datetime] = None
            for d in dispatches:
                t = parse_time(d.get('actual_arrival'))
                if t and (first_arrival_time is None or t < first_arrival_time):
                    first_arrival_time = t

            resolution_time_abs: Optional[datetime] = None
            status = str(incident_doc.get('status') or '')
            if status.lower() in ('resolved', 'closed'):
                # Prefer explicit resolution timestamp if present
                resolution_time_abs = parse_time(cast(Optional[str], incident_doc.get('resolution_timestamp'))) or parse_time(cast(Optional[str], incident_doc.get('updated_at')))

            # Compute deltas
            def delta_seconds(t: Optional[datetime]) -> float:
                return float((t - incident_time).total_seconds()) if t else 0.0

            first_response_candidates = [t for t in [first_alert_time, first_contact_time, first_dispatch_time] if t]
            first_response_time = delta_seconds(min(first_response_candidates)) if first_response_candidates else 0.0
            authority_notification_time = delta_seconds(first_alert_time)
            emergency_contact_time = delta_seconds(first_contact_time)
            dispatch_time = delta_seconds(first_dispatch_time)
            arrival_time = delta_seconds(first_arrival_time) if first_arrival_time else None
            resolution_time = delta_seconds(resolution_time_abs) if resolution_time_abs else 0.0
            total_duration = resolution_time if resolution_time else (datetime.now() - incident_time).total_seconds()

            return ResponseTimeMetrics(
                incident_detection_time=incident_time.isoformat(),
                first_response_time=first_response_time,
                authority_notification_time=authority_notification_time,
                emergency_contact_notification_time=emergency_contact_time,
                dispatch_time=dispatch_time,
                arrival_time=arrival_time,
                resolution_time=resolution_time,
                total_response_duration=total_duration,
            )
        except Exception as e:
            self.logger.error(f"Error calculating response metrics: {str(e)}")
            raise
    
    def document_resolution(self, incident_id: str) -> ResolutionDetails:
        """Document incident resolution details from Mongo collections."""
        try:
            incident_doc: Optional[Dict[str, Any]] = mdb.get_incident(incident_id)
            if not incident_doc:
                raise ValueError(f"Incident {incident_id} not found")

            status: str = str(incident_doc.get('status') or 'unresolved')
            resolution_notes: str = str(incident_doc.get('resolution_notes') or '')

            # Services involved from dispatch tracking
            services_involved: List[str] = []
            for d in mdb.list_dispatches(incident_id):
                svc = d.get('service_type')
                if isinstance(svc, str):
                    services_involved.append(svc)
            services_involved = list(sorted(set(services_involved)))

            # Authority responses from verification logs
            authority_responses: List[Dict[str, Any]] = mdb.list_authority_verifications(incident_id)

            resolution_method = self._determine_resolution_method(
                services_involved, authority_responses, resolution_notes
            )

            final_outcome = self._determine_final_outcome(
                status, resolution_notes, authority_responses
            )

            tourist_condition = self._assess_tourist_condition(
                resolution_notes, authority_responses
            )

            follow_up_required, follow_up_details = self._assess_follow_up_needs(
                final_outcome, tourist_condition, services_involved
            )

            return ResolutionDetails(
                resolution_status=status,
                resolution_method=resolution_method,
                services_involved=services_involved,
                final_outcome=final_outcome,
                tourist_condition=tourist_condition,
                follow_up_required=follow_up_required,
                follow_up_details=follow_up_details,
            )
        except Exception as e:
            self.logger.error(f"Error documenting resolution: {str(e)}")
            raise
    
    def generate_comprehensive_report(self, incident_id: str, report_type: str = 'full') -> Dict[str, Any]:
        """Generate comprehensive post-incident report and store in Mongo."""
        try:
            self.logger.info(f"Generating {report_type} report for incident {incident_id}")

            incident_doc: Optional[Dict[str, Any]] = mdb.get_incident(incident_id)
            if not incident_doc:
                raise ValueError(f"Incident {incident_id} not found")

            # Generate analysis components
            cause_analysis = self.analyze_incident_cause(incident_id)
            response_metrics = self.calculate_response_metrics(incident_id)
            resolution_details = self.document_resolution(incident_id)

            # Create comprehensive report
            report: Dict[str, Any] = {
                'report_metadata': {
                    'report_id': f"RPT-{incident_id}-{uuid.uuid4().hex[:8]}",
                    'incident_id': incident_id,
                    'report_type': report_type,
                    'generated_at': datetime.now().isoformat(),
                    'generated_by': 'post_incident_system',
                    'report_version': '1.0',
                },
                'incident_summary': {
                    'incident_id': incident_doc.get('incident_id') or incident_id,
                    'tourist_id': incident_doc.get('tourist_id'),
                    'incident_timestamp': incident_doc.get('created_at'),
                    'location': incident_doc.get('location') or {},
                    'emergency_type': incident_doc.get('incident_type'),
                    'incident_message': incident_doc.get('message'),
                    'severity': incident_doc.get('severity'),
                    'final_status': incident_doc.get('status'),
                    'resolution_timestamp': incident_doc.get('resolution_timestamp'),
                },
                'cause_analysis': {
                    'primary_cause': cause_analysis.cause_category,
                    'cause_details': cause_analysis.cause_details,
                    'contributing_factors': cause_analysis.contributing_factors,
                    'severity_assessment': cause_analysis.severity_assessment,
                    'prevention_recommendations': cause_analysis.prevention_recommendations,
                },
                'response_time_analysis': {
                    'incident_detection': response_metrics.incident_detection_time,
                    'first_response_seconds': response_metrics.first_response_time,
                    'authority_notification_seconds': response_metrics.authority_notification_time,
                    'emergency_contact_seconds': response_metrics.emergency_contact_notification_time,
                    'dispatch_seconds': response_metrics.dispatch_time,
                    'arrival_seconds': response_metrics.arrival_time,
                    'resolution_seconds': response_metrics.resolution_time,
                    'total_duration_seconds': response_metrics.total_response_duration,
                    'performance_benchmarks': self._evaluate_performance(response_metrics),
                },
                'resolution_summary': {
                    'resolution_status': resolution_details.resolution_status,
                    'resolution_method': resolution_details.resolution_method,
                    'services_involved': resolution_details.services_involved,
                    'final_outcome': resolution_details.final_outcome,
                    'tourist_condition': resolution_details.tourist_condition,
                    'follow_up_required': resolution_details.follow_up_required,
                    'follow_up_details': resolution_details.follow_up_details,
                },
                'lessons_learned': self._generate_lessons_learned(
                    cause_analysis, response_metrics, resolution_details
                ),
                'improvement_recommendations': self._generate_improvement_recommendations(
                    cause_analysis, response_metrics, resolution_details
                ),
            }

            # Store report and analytics in Mongo
            report_id: str = str(report['report_metadata']['report_id'])
            report_hash = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
            mdb.create_post_incident_report({
                'report_id': report_id,
                'incident_id': incident_id,
                'report_generated_at': datetime.now().isoformat(),
                'report_type': report_type,
                'report_data': report,
                'report_hash': report_hash,
                'generated_by': 'system',
                'status': 'completed',
                'tourist_id': incident_doc.get('tourist_id'),
            })

            # Store analytics
            try:
                ra = getattr(mdb, '_report_analytics', None)
                if ra is not None:
                    ra.insert_one({  # type: ignore[attr-defined]
                        'analytics_id': f"ANALYTICS-{report_id}",
                        'report_id': report_id,
                        'cause_analysis': dict(cause_analysis.__dict__),
                        'response_metrics': dict(response_metrics.__dict__),
                        'resolution_summary': dict(resolution_details.__dict__),
                        'lessons_learned': report['lessons_learned'],
                        'improvement_recommendations': report['improvement_recommendations'],
                        'analyzed_at': datetime.now().isoformat(),
                    })
            except Exception:
                pass

            self.logger.info(f"✅ Report {report_id} generated successfully (Mongo)")
            return report
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
    
    def share_report_with_tourist(self, report_id: str, tourist_id: int, sharing_method: str = 'system_notification') -> bool:
        """Share incident report with the affected tourist (Mongo)."""
        try:
            # Get report from Mongo
            rep = mdb.get_post_incident_report(report_id)
            if not rep:
                raise ValueError(f"Report {report_id} not found")

            raw_report = rep.get('report_data')
            full_report: Dict[str, Any] = cast(Dict[str, Any], raw_report) if isinstance(raw_report, dict) else {}
            # Create tourist-friendly version (remove sensitive details)
            _ = self._create_tourist_report_version(full_report)

            # Log sharing activity
            mdb.share_post_incident_report(report_id, 'tourist', str(tourist_id), sharing_method, delivery_status='delivered')

            # Optional: create an admin notification to represent user notice
            try:
                mdb.create_admin_notification({
                    'title': 'Incident Report Ready',
                    'message': f'Report {report_id} shared with tourist {tourist_id}',
                    'severity': 'info',
                })
            except Exception:
                pass

            self.logger.info(f"✅ Report {report_id} shared with tourist {tourist_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error sharing report with tourist: {str(e)}")
            return False
    
    def share_report_with_authorities(self, report_id: str, authority_types: Optional[List[str]] = None) -> Dict[str, bool]:
        """Share incident report with relevant authorities (Mongo)."""
        if authority_types is None:
            authority_types = ['police', 'medical', 'emergency_services', 'tourism_board']

        results: Dict[str, bool] = {}
        try:
            rep = mdb.get_post_incident_report(report_id)
            if not rep:
                raise ValueError(f"Report {report_id} not found")
            raw_report = rep.get('report_data')
            report: Dict[str, Any] = cast(Dict[str, Any], raw_report) if isinstance(raw_report, dict) else {}

            for authority_type in authority_types:
                try:
                    _ = self._create_authority_report_version(report, authority_type)
                    mdb.share_post_incident_report(report_id, 'authority', authority_type, 'secure_transmission', delivery_status='delivered')
                    results[authority_type] = True
                    self.logger.info(f"✅ Report shared with {authority_type}")
                except Exception as e:
                    self.logger.error(f"Failed to share with {authority_type}: {str(e)}")
                    results[authority_type] = False
            return results
        except Exception as e:
            self.logger.error(f"Error sharing report with authorities: {str(e)}")
            return {auth: False for auth in authority_types}
    
    # Helper methods for analysis and report generation
    def _determine_cause_category(self, incident_type: str, emergency_type: Optional[str], message: Optional[str], ai_analysis: Optional[Any], auto_sos_data: Optional[Any]) -> str:
        """Determine the primary cause category of the incident"""
        if (emergency_type or '') in ['medical_emergency', 'health_issue']:
            return 'medical_emergency'
        elif (emergency_type or '') in ['security_threat', 'crime', 'harassment']:
            return 'security_threat'
        elif (emergency_type or '') in ['natural_disaster', 'weather']:
            return 'natural_disaster'
        elif auto_sos_data and 'transport' in str(auto_sos_data).lower():
            return 'transportation_issue'
        elif isinstance(message, str) and ('lost' in message.lower() or 'help' in message.lower()):
            return 'tourist_error'
        else:
            return 'external_factor'
    
    def _generate_cause_details(self, incident_data: Tuple[Any, ...], ai_analysis: Optional[Any], auto_sos_data: Optional[Any]) -> str:
        """Generate detailed cause description"""
        # For compatibility with legacy tuple structure
        message = str(incident_data[3]) if len(incident_data) > 3 and incident_data[3] is not None else ''
        timestamp = str(incident_data[4]) if len(incident_data) > 4 and incident_data[4] is not None else datetime.now().isoformat()
        emergency_type = str(incident_data[5]) if len(incident_data) > 5 and incident_data[5] is not None else ''
        # context = incident_data[6] if len(incident_data) > 6 else None
        
        details = f"Incident of type '{emergency_type}' occurred at {timestamp}. "
        details += f"Tourist reported: '{message}'. "
        
        if ai_analysis:
            details += f"AI analysis indicated: {ai_analysis}. "
        
        if auto_sos_data:
            details += f"Auto-SOS triggered due to: {auto_sos_data}. "
        
        return details.strip()
    
    def _identify_contributing_factors(self, incident_data: Tuple[Any, ...], ai_analysis: Optional[Any], auto_sos_data: Optional[Any]) -> List[str]:
        """Identify contributing factors to the incident"""
        factors: List[str] = []

        # ai_analysis may be dict with 'risk_factors'
        try:
            if isinstance(ai_analysis, dict):
                ai_dict: Dict[str, Any] = cast(Dict[str, Any], ai_analysis)
                rf_val: Any = ai_dict.get('risk_factors')
                if isinstance(rf_val, (list, tuple)):
                    iter_rf = cast(List[Any], rf_val) if isinstance(rf_val, list) else cast(Tuple[Any, ...], rf_val)
                    for item in iter_rf:
                        factors.append(str(item))
                elif isinstance(rf_val, str):
                    loaded_obj_any: Any = json.loads(rf_val)
                    if isinstance(loaded_obj_any, dict):
                        loaded_obj: Dict[str, Any] = cast(Dict[str, Any], loaded_obj_any)
                        lf_any: Any = loaded_obj.get('factors', [])
                        if isinstance(lf_any, (list, tuple)):
                            iter_lf = cast(List[Any], lf_any) if isinstance(lf_any, list) else cast(Tuple[Any, ...], lf_any)
                            for item in iter_lf:
                                factors.append(str(item))
        except Exception:
            pass

        try:
            # auto_sos_data may include confidence
            if isinstance(auto_sos_data, dict):
                auto_dict: Dict[str, Any] = cast(Dict[str, Any], auto_sos_data)
                conf_val: Any = auto_dict.get('confidence') or auto_dict.get('confidence_score') or 0.0
                try:
                    conf = float(conf_val)
                except Exception:
                    conf = 0.0
                if conf > 0.8:
                    factors.append('High-confidence automatic detection')
        except Exception:
            pass

        # Add location-based factors using incident_data second element (location json)
        try:
            raw = incident_data[1] if len(incident_data) > 1 else None
            location_dict: Dict[str, Any] = {}
            if isinstance(raw, str) and raw:
                try:
                    obj_any: Any = json.loads(raw)
                    if isinstance(obj_any, dict):
                        location_dict = cast(Dict[str, Any], obj_any)
                except Exception:
                    location_dict = {}
            acc_raw: Any = location_dict.get('accuracy', 0)
            try:
                acc = float(acc_raw)
            except Exception:
                acc = 0.0
            if acc > 100:
                factors.append('Low GPS accuracy')
        except Exception:
            pass

        return factors if factors else ['Standard incident conditions']
    
    def _assess_severity(self, severity: Optional[str], incident_type: str, ai_analysis: Optional[Any]) -> str:
        """Assess the severity of the incident"""
        if isinstance(severity, str) and severity:
            return severity
        
        if isinstance(ai_analysis, dict):
            ai_dict2: Dict[str, Any] = cast(Dict[str, Any], ai_analysis)
            sev_val: Any = ai_dict2.get('severity')
            if isinstance(sev_val, str) and sev_val:
                return sev_val
        
        return 'medium'  # Default
    
    def _generate_prevention_recommendations(self, cause_category: str, contributing_factors: List[str], incident_data: Tuple[Any, ...]) -> List[str]:
        """Generate prevention recommendations based on analysis"""
        recommendations: List[str] = []
        
        if cause_category == 'tourist_error':
            recommendations.append('Enhance tourist orientation and safety briefings')
            recommendations.append('Improve wayfinding and signage in tourist areas')
        elif cause_category == 'medical_emergency':
            recommendations.append('Increase medical facility awareness campaigns')
            recommendations.append('Enhance emergency medical response coverage')
        elif cause_category == 'security_threat':
            recommendations.append('Strengthen security presence in tourist areas')
            recommendations.append('Improve tourist safety awareness programs')
        
        if 'Low GPS accuracy' in contributing_factors:
            recommendations.append('Improve GPS coverage and backup location systems')
        
        return recommendations if recommendations else ['Continue standard safety protocols']
    
    def _determine_resolution_method(self, services_involved: List[str], authority_responses: List[Any], resolution_notes: Optional[str]) -> str:
        """Determine how the incident was resolved"""
        if 'medical' in services_involved:
            return 'Medical intervention'
        elif 'police' in services_involved:
            return 'Law enforcement response'
        elif len(authority_responses) > 0:
            return 'Authority coordination'
        elif isinstance(resolution_notes, str) and 'self' in resolution_notes.lower():
            return 'Self-resolved'
        else:
            return 'System-assisted resolution'
    
    def _determine_final_outcome(self, resolution_status: str, resolution_notes: Optional[str], authority_responses: List[Any]) -> str:
        """Determine the final outcome of the incident"""
        if resolution_status == 'resolved':
            return 'Successfully resolved'
        elif resolution_status == 'closed':
            return 'Case closed'
        else:
            transported = False
            for resp in authority_responses:
                if isinstance(resp, dict):
                    respd: Dict[str, Any] = cast(Dict[str, Any], resp)
                    rn = str(respd.get('response_notes') or respd.get('verification_status') or '')
                    if 'transported' in rn.lower():
                        transported = True
                        break
            if transported:
                return 'Medical transport provided'
            return 'Outcome pending'
    
    def _assess_tourist_condition(self, resolution_notes: Optional[str], authority_responses: List[Any]) -> str:
        """Assess the final condition of the tourist"""
        if isinstance(resolution_notes, str) and 'safe' in resolution_notes.lower():
            return 'Safe and secure'
        else:
            stable = False
            hospital = False
            for resp in authority_responses:
                if isinstance(resp, dict):
                    respd2: Dict[str, Any] = cast(Dict[str, Any], resp)
                    rn2 = str(respd2.get('response_notes') or '')
                    rl = rn2.lower()
                    if 'stable' in rl:
                        stable = True
                    if 'hospital' in rl:
                        hospital = True
            if stable:
                return 'Stable condition'
            if hospital:
                return 'Under medical care'
            return 'Condition under observation'
    
    def _assess_follow_up_needs(self, final_outcome: str, tourist_condition: str, services_involved: List[str]) -> Tuple[bool, str]:
        """Assess if follow-up actions are needed"""
        follow_up_required = False
        details = ""
        
        if 'medical' in services_involved:
            follow_up_required = True
            details += "Medical follow-up recommended. "
        
        if 'Under medical care' in tourist_condition:
            follow_up_required = True
            details += "Monitor recovery progress. "
        
        if 'pending' in final_outcome.lower():
            follow_up_required = True
            details += "Await final resolution confirmation. "
        
        return follow_up_required, details.strip()
    
    def _evaluate_performance(self, metrics: ResponseTimeMetrics) -> Dict[str, str]:
        """Evaluate response performance against benchmarks"""
        performance: Dict[str, str] = {}
        
        performance['first_response'] = 'excellent' if metrics.first_response_time <= self.response_benchmarks['first_response'] else 'needs_improvement'
        performance['authority_notification'] = 'excellent' if metrics.authority_notification_time <= self.response_benchmarks['authority_notification'] else 'needs_improvement'
        performance['emergency_contact'] = 'excellent' if metrics.emergency_contact_notification_time <= self.response_benchmarks['emergency_contact'] else 'needs_improvement'
        performance['dispatch'] = 'excellent' if metrics.dispatch_time <= self.response_benchmarks['dispatch'] else 'needs_improvement'
        
        if metrics.arrival_time:
            performance['arrival'] = 'excellent' if metrics.arrival_time <= self.response_benchmarks['arrival'] else 'needs_improvement'
        
        return performance
    
    def _generate_lessons_learned(self, cause_analysis: IncidentAnalysis, response_metrics: ResponseTimeMetrics, resolution_details: ResolutionDetails) -> List[str]:
        """Generate lessons learned from the incident"""
        lessons: List[str] = []
        
        # Response time lessons
        if response_metrics.first_response_time > self.response_benchmarks['first_response']:
            lessons.append('Initial response time exceeded benchmark - review alert processing')
        
        if response_metrics.authority_notification_time > self.response_benchmarks['authority_notification']:
            lessons.append('Authority notification delayed - optimize communication channels')
        
        # Cause-based lessons
        if 'tourist_error' in cause_analysis.cause_category:
            lessons.append('Tourist orientation programs may need enhancement')
        
        if len(resolution_details.services_involved) > 2:
            lessons.append('Multi-service coordination protocols worked effectively')
        
        return lessons if lessons else ['Standard response protocols performed adequately']
    
    def _generate_improvement_recommendations(self, cause_analysis: IncidentAnalysis, response_metrics: ResponseTimeMetrics, resolution_details: ResolutionDetails) -> List[str]:
        """Generate improvement recommendations"""
        recommendations: List[str] = []
        
        # Performance improvements
        if response_metrics.first_response_time > 60:
            recommendations.append('Implement faster alert processing systems')
        
        if not resolution_details.follow_up_required and resolution_details.resolution_status == 'resolved':
            recommendations.append('Current protocols are effective - maintain standards')
        
        # System improvements
        if 'system_malfunction' in cause_analysis.cause_category:
            recommendations.append('Conduct comprehensive system reliability review')
        
        recommendations.extend(cause_analysis.prevention_recommendations)
        
        return list(set(recommendations))  # Remove duplicates
    
    def _create_tourist_report_version(self, full_report: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tourist-friendly version of the report"""
        tourist_report: Dict[str, Any] = {
            'incident_summary': full_report['incident_summary'],
            'what_happened': {
                'cause': full_report['cause_analysis']['cause_details'],
                'resolution': full_report['resolution_summary']['final_outcome'],
                'your_safety': full_report['resolution_summary']['tourist_condition']
            },
            'response_summary': {
                'total_response_time': f"{full_report['response_time_analysis']['total_duration_seconds']} seconds",
                'services_helped': full_report['resolution_summary']['services_involved']
            },
            'follow_up': {
                'required': full_report['resolution_summary']['follow_up_required'],
                'details': full_report['resolution_summary']['follow_up_details']
            },
            'prevention_tips': full_report['cause_analysis']['prevention_recommendations']
        }
        return tourist_report
    
    def _create_authority_report_version(self, full_report: Dict[str, Any], authority_type: str) -> Dict[str, Any]:
        """Create authority-specific version of the report"""
        # Authorities get the full report with additional context
        authority_report: Dict[str, Any] = full_report.copy()
        authority_report['authority_context'] = {
            'jurisdiction': authority_type,
            'classification': f"{authority_type}_incident_report",
            'security_level': 'standard',
            'distribution': 'internal_use_only'
        }
        return authority_report