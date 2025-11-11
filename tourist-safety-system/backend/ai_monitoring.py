"""
AI-Powered Tourist Monitoring System
====================================

This module implements intelligent monitoring of tourist movements and environmental factors
to provide real-time risk assessment and anomaly detection.

Features:
- Movement Analysis: Sudden stops, rapid movements, abnormal patterns
- Environmental Monitoring: Time-based risk, crowd density, environmental factors
- Risk Classification: Low/Medium/High risk levels with intelligent scoring
- Real-time Alerts: Automatic notifications for high-risk situations
- Auto SOS Detection: AI-powered automatic emergency detection
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import math
import statistics
import uuid
import importlib.util
from mongo_db import (
    insert_ai_monitoring_result,
    insert_risk_alert,
    list_risk_alerts,
    get_ai_statistics,
    get_recent_locations as mongo_get_recent_locations,
)
# Import Auto SOS Detection system availability check
auto_sos_available = importlib.util.find_spec("auto_sos_detection") is not None
if not auto_sos_available:
    print("⚠️ Auto SOS Detection system not available")

class MovementAnalyzer:
    """Analyzes tourist movement patterns for anomaly detection"""
    
    def __init__(self):
        self.movement_threshold_stop = 5.0  # meters for sudden stop detection
        self.movement_threshold_rapid = 50.0  # meters/minute for rapid movement
        self.time_window_minutes = 10  # analysis window
        self.abnormal_pattern_threshold = 0.7  # confidence threshold
    
    def analyze_sudden_stops(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect sudden stops in movement patterns
        
        Args:
            location_history: List of location points with timestamps
            
        Returns:
            Dict with sudden stop analysis results
        """
        if len(location_history) < 3:
            return {'sudden_stops': 0, 'risk_score': 0.0, 'details': []}
        
        sudden_stops: List[Dict[str, Any]] = []
        risk_score: float = 0.0
        
        for i in range(1, len(location_history) - 1):
            prev_point = location_history[i-1]
            curr_point = location_history[i]
            next_point = location_history[i+1]
            
            # Calculate movement distances
            dist_before = self._calculate_distance(
                prev_point['latitude'], prev_point['longitude'],
                curr_point['latitude'], curr_point['longitude']
            )
            
            dist_after = self._calculate_distance(
                curr_point['latitude'], curr_point['longitude'],
                next_point['latitude'], next_point['longitude']
            )
            
            # Calculate time differences (in minutes)
            time_before = self._time_diff_minutes(prev_point['timestamp'], curr_point['timestamp'])
            time_after = self._time_diff_minutes(curr_point['timestamp'], next_point['timestamp'])
            
            if time_before > 0 and time_after > 0:
                speed_before = dist_before / time_before if time_before > 0 else 0
                speed_after = dist_after / time_after if time_after > 0 else 0
                
                # Detect sudden stop: significant speed drop
                if speed_before > 30 and speed_after < self.movement_threshold_stop:
                    stop_duration = time_after
                    sudden_stops.append({
                        'timestamp': curr_point['timestamp'],
                        'location': {
                            'latitude': curr_point['latitude'],
                            'longitude': curr_point['longitude']
                        },
                        'speed_before': speed_before,
                        'speed_after': speed_after,
                        'stop_duration': stop_duration,
                        'severity': self._classify_stop_severity(speed_before, stop_duration)
                    })
                    
                    # Increase risk score based on severity and duration
                    risk_score += min(0.3, stop_duration / 60.0 * 0.1)
        
        return {
            'sudden_stops': len(sudden_stops),
            'risk_score': min(1.0, risk_score),
            'details': sudden_stops,
            'analysis_window': self.time_window_minutes
        }
    
    def analyze_rapid_movements(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect rapid or erratic movements that might indicate distress
        
        Args:
            location_history: List of location points with timestamps
            
        Returns:
            Dict with rapid movement analysis results
        """
        if len(location_history) < 2:
            return {'rapid_movements': 0, 'risk_score': 0.0, 'details': []}
        
        rapid_movements: List[Dict[str, Any]] = []
        speeds: List[float] = []
        risk_score: float = 0.0
        
        for i in range(1, len(location_history)):
            prev_point = location_history[i-1]
            curr_point = location_history[i]
            
            distance = self._calculate_distance(
                prev_point['latitude'], prev_point['longitude'],
                curr_point['latitude'], curr_point['longitude']
            )
            
            time_diff = self._time_diff_minutes(prev_point['timestamp'], curr_point['timestamp'])
            
            if time_diff > 0:
                speed = distance / time_diff  # meters per minute
                speeds.append(speed)
                
                # Detect rapid movement
                if speed > self.movement_threshold_rapid:
                    rapid_movements.append({
                        'timestamp': curr_point['timestamp'],
                        'location': {
                            'latitude': curr_point['latitude'],
                            'longitude': curr_point['longitude']
                        },
                        'speed': speed,
                        'distance': distance,
                        'time_duration': time_diff,
                        'severity': self._classify_speed_severity(speed)
                    })
                    
                    # Increase risk score for very high speeds
                    if speed > 100:  # Very rapid movement
                        risk_score += 0.4
                    elif speed > 75:
                        risk_score += 0.2
                    else:
                        risk_score += 0.1
        
        # Calculate speed statistics
        avg_speed = statistics.mean(speeds) if speeds else 0
        max_speed = max(speeds) if speeds else 0
        speed_variance = statistics.variance(speeds) if len(speeds) > 1 else 0
        
        return {
            'rapid_movements': len(rapid_movements),
            'risk_score': min(1.0, risk_score),
            'details': rapid_movements,
            'speed_stats': {
                'average_speed': avg_speed,
                'max_speed': max_speed,
                'speed_variance': speed_variance
            }
        }
    
    def analyze_abnormal_patterns(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect abnormal movement patterns using statistical analysis
        
        Args:
            location_history: List of location points with timestamps
            
        Returns:
            Dict with abnormal pattern analysis results
        """
        if len(location_history) < 5:
            return {'abnormal_patterns': 0, 'risk_score': 0.0, 'details': []}
        
        patterns: Dict[str, Dict[str, Any]] = {
            'circular_movement': self._detect_circular_movement(location_history),
            'backtracking': self._detect_backtracking(location_history),
            'stationary_periods': self._detect_long_stationary_periods(location_history),
            'erratic_direction_changes': self._detect_erratic_direction_changes(location_history)
        }
        
        # Calculate overall abnormal pattern risk
        risk_score = 0.0
        abnormal_count = 0
        
        for _, pattern_data in patterns.items():
            if pattern_data['detected']:
                abnormal_count += 1
                risk_score += pattern_data['risk_contribution']
        
        return {
            'abnormal_patterns': abnormal_count,
            'risk_score': min(1.0, risk_score),
            'details': patterns,
            'confidence': self._calculate_pattern_confidence(patterns)
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in meters"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _time_diff_minutes(self, timestamp1: str, timestamp2: str) -> float:
        """Calculate time difference in minutes between two timestamps"""
        try:
            dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            return abs((dt2 - dt1).total_seconds() / 60.0)
        except:
            return 0.0
    
    def _classify_stop_severity(self, speed_before: float, stop_duration: float) -> str:
        """Classify severity of sudden stops"""
        if speed_before > 60 and stop_duration > 30:
            return 'high'
        elif speed_before > 40 and stop_duration > 15:
            return 'medium'
        else:
            return 'low'
    
    def _classify_speed_severity(self, speed: float) -> str:
        """Classify severity of rapid movements"""
        if speed > 120:
            return 'high'
        elif speed > 80:
            return 'medium'
        else:
            return 'low'
    
    def _detect_circular_movement(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect circular or repetitive movement patterns"""
        if len(location_history) < 4:
            return {'detected': False, 'risk_contribution': 0.0}
        
        # Check if tourist returns to similar locations multiple times
        position_clusters: List[Dict[str, Any]] = []
        cluster_threshold = 50  # meters
        
        for point in location_history:
            found_cluster = False
            for cluster in position_clusters:
                if self._calculate_distance(
                    point['latitude'], point['longitude'],
                    cluster.get('center_lat', 0), cluster.get('center_lng', 0)
                ) < cluster_threshold:
                    cluster['visits'] += 1
                    found_cluster = True
                    break
            
            if not found_cluster:
                position_clusters.append({
                    'center_lat': point['latitude'],
                    'center_lng': point['longitude'],
                    'visits': 1
                })
        
        # Look for clusters with multiple visits
        circular_detected = any(cluster['visits'] >= 3 for cluster in position_clusters)
        risk_contribution = 0.2 if circular_detected else 0.0
        
        return {
            'detected': circular_detected,
            'risk_contribution': risk_contribution,
            'clusters': position_clusters
        }
    
    def _detect_backtracking(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect backtracking patterns that might indicate confusion or distress"""
        if len(location_history) < 4:
            return {'detected': False, 'risk_contribution': 0.0}
        
        backtrack_count = 0
        total_segments = len(location_history) - 1
        
        for i in range(2, len(location_history)):
            current = location_history[i]
            prev = location_history[i-1]
            prev_prev = location_history[i-2]
            
            # Calculate if current position is closer to prev_prev than prev
            dist_to_prev_prev = self._calculate_distance(
                current['latitude'], current['longitude'],
                prev_prev['latitude'], prev_prev['longitude']
            )
            
            dist_to_prev = self._calculate_distance(
                current['latitude'], current['longitude'],
                prev['latitude'], prev['longitude']
            )
            
            if dist_to_prev_prev < dist_to_prev and dist_to_prev_prev < 30:
                backtrack_count += 1
        
        backtrack_ratio = backtrack_count / total_segments if total_segments > 0 else 0
        detected = backtrack_ratio > 0.3
        risk_contribution = min(0.3, backtrack_ratio)
        
        return {
            'detected': detected,
            'risk_contribution': risk_contribution,
            'backtrack_ratio': backtrack_ratio,
            'backtrack_count': backtrack_count
        }
    
    def _detect_long_stationary_periods(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect unusually long stationary periods"""
        if len(location_history) < 2:
            return {'detected': False, 'risk_contribution': 0.0}
        
        stationary_periods: List[Dict[str, Any]] = []
        current_stationary_start = None
        stationary_threshold = 20  # meters
        
        for i in range(1, len(location_history)):
            distance = self._calculate_distance(
                location_history[i-1]['latitude'], location_history[i-1]['longitude'],
                location_history[i]['latitude'], location_history[i]['longitude']
            )
            
            if distance < stationary_threshold:
                if current_stationary_start is None:
                    current_stationary_start = location_history[i-1]['timestamp']
            else:
                if current_stationary_start is not None:
                    duration = self._time_diff_minutes(current_stationary_start, location_history[i-1]['timestamp'])
                    if duration > 60:  # More than 1 hour stationary
                        stationary_periods.append({
                            'start_time': current_stationary_start,
                            'end_time': location_history[i-1]['timestamp'],
                            'duration_minutes': duration,
                            'location': {
                                'latitude': location_history[i-1]['latitude'],
                                'longitude': location_history[i-1]['longitude']
                            }
                        })
                    current_stationary_start = None
        
        # Check final period
        if current_stationary_start is not None:
            duration = self._time_diff_minutes(current_stationary_start, location_history[-1]['timestamp'])
            if duration > 60:
                stationary_periods.append({
                    'start_time': current_stationary_start,
                    'end_time': location_history[-1]['timestamp'],
                    'duration_minutes': duration,
                    'location': {
                        'latitude': location_history[-1]['latitude'],
                        'longitude': location_history[-1]['longitude']
                    }
                })
        
        detected = len(stationary_periods) > 0
        risk_contribution = min(0.2, len(stationary_periods) * 0.1)
        
        return {
            'detected': detected,
            'risk_contribution': risk_contribution,
            'stationary_periods': stationary_periods
        }
    
    def _detect_erratic_direction_changes(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect erratic direction changes that might indicate panic or confusion"""
        if len(location_history) < 3:
            return {'detected': False, 'risk_contribution': 0.0}
        
        direction_changes: List[Dict[str, Any]] = []
        
        for i in range(2, len(location_history)):
            # Calculate bearings
            bearing1 = self._calculate_bearing(
                location_history[i-2]['latitude'], location_history[i-2]['longitude'],
                location_history[i-1]['latitude'], location_history[i-1]['longitude']
            )
            
            bearing2 = self._calculate_bearing(
                location_history[i-1]['latitude'], location_history[i-1]['longitude'],
                location_history[i]['latitude'], location_history[i]['longitude']
            )
            
            # Calculate angle change
            angle_change = abs(bearing2 - bearing1)
            if angle_change > 180:
                angle_change = 360 - angle_change
            
            if angle_change > 90:  # Sharp direction change
                direction_changes.append({
                    'timestamp': location_history[i]['timestamp'],
                    'location': {
                        'latitude': location_history[i]['latitude'],
                        'longitude': location_history[i]['longitude']
                    },
                    'angle_change': angle_change
                })
        
        # Consider erratic if too many sharp turns
        erratic_threshold = len(location_history) * 0.4
        detected = len(direction_changes) > erratic_threshold
        risk_contribution = min(0.25, len(direction_changes) / len(location_history))
        
        return {
            'detected': detected,
            'risk_contribution': risk_contribution,
            'direction_changes': direction_changes,
            'sharp_turn_ratio': len(direction_changes) / len(location_history)
        }
    
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing between two GPS coordinates"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon_rad = math.radians(lon2 - lon1)
        
        y = math.sin(delta_lon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad))
        
        bearing = math.atan2(y, x)
        return (math.degrees(bearing) + 360) % 360
    
    def _calculate_pattern_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence level for pattern detection"""
        detected_patterns = sum(1 for p in patterns.values() if p['detected'])
        total_patterns = len(patterns)
        
        if total_patterns == 0:
            return 0.0
        
        base_confidence = detected_patterns / total_patterns
        
        # Adjust confidence based on risk contributions
        risk_sum = sum(p['risk_contribution'] for p in patterns.values())
        risk_factor = min(1.0, risk_sum / 0.5)  # Normalize to 0-1
        
        return min(1.0, (base_confidence + risk_factor) / 2)


class EnvironmentalMonitor:
    """Monitors environmental factors that affect tourist safety"""
    
    def __init__(self):
        self.time_risk_factors = {
            'very_early': (0, 5),      # 12 AM - 5 AM (high risk)
            'early_morning': (5, 8),   # 5 AM - 8 AM (medium risk)
            'morning': (8, 12),        # 8 AM - 12 PM (low risk)
            'afternoon': (12, 17),     # 12 PM - 5 PM (low risk)
            'evening': (17, 20),       # 5 PM - 8 PM (medium risk)
            'night': (20, 24)         # 8 PM - 12 AM (high risk)
        }
        
        self.crowd_density_thresholds = {
            'low': 10,      # people per 100m²
            'medium': 25,   # people per 100m²
            'high': 50,     # people per 100m²
            'very_high': 100 # people per 100m²
        }
    
    def analyze_time_risk(self, timestamp: str, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze time-based risk factors
        
        Args:
            timestamp: Current timestamp
            location: Current location coordinates
            
        Returns:
            Dict with time-based risk analysis
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            
            # Determine time period
            time_period = 'unknown'
            for period, (start, end) in self.time_risk_factors.items():
                if start <= hour < end:
                    time_period = period
                    break
            
            # Calculate risk based on time
            risk_score = self._calculate_time_risk_score(hour)
            
            # Additional factors
            is_weekend = dt.weekday() >= 5
            is_holiday = self._check_holiday(dt)
            
            # Adjust risk for weekends and holidays
            if is_weekend:
                risk_score *= 1.1
            if is_holiday:
                risk_score *= 1.2
            
            return {
                'time_period': time_period,
                'hour': hour,
                'risk_score': min(1.0, risk_score),
                'is_weekend': is_weekend,
                'is_holiday': is_holiday,
                'recommendations': self._get_time_recommendations(time_period, risk_score)
            }
            
        except Exception as e:
            return {
                'time_period': 'unknown',
                'hour': 12,
                'risk_score': 0.3,
                'is_weekend': False,
                'is_holiday': False,
                'recommendations': ['Unable to analyze time factors'],
                'error': str(e)
            }
    
    def analyze_crowd_density(self, location: Dict[str, Any], nearby_tourists: int = 0) -> Dict[str, Any]:
        """
        Analyze crowd density and its safety implications
        
        Args:
            location: Current location coordinates
            nearby_tourists: Number of tourists in vicinity
            
        Returns:
            Dict with crowd density analysis
        """
        # Estimate crowd density (this would be enhanced with real data sources)
        estimated_density = self._estimate_crowd_density(location, nearby_tourists)
        
        # Classify density level
        density_level = 'low'
        for level, threshold in self.crowd_density_thresholds.items():
            if estimated_density >= threshold:
                density_level = level
        
        # Calculate risk score based on density
        risk_score = self._calculate_crowd_risk_score(estimated_density, density_level)
        
        return {
            'density_level': density_level,
            'estimated_density': estimated_density,
            'nearby_tourists': nearby_tourists,
            'risk_score': risk_score,
            'safety_factors': self._get_crowd_safety_factors(density_level),
            'recommendations': self._get_crowd_recommendations(density_level, risk_score)
        }
    
    def analyze_environmental_factors(self, location: Dict[str, float], weather_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze various environmental risk factors
        
        Args:
            location: Current location coordinates
            weather_data: Optional weather information
            
        Returns:
            Dict with environmental risk analysis
        """
        risk_factors: List[Dict[str, Any]] = []
        total_risk_score: float = 0.0
        
        # Location-based risks
        location_risks = self._analyze_location_risks(location)
        risk_factors.extend(location_risks['factors'])
        total_risk_score += location_risks['risk_score']
        
        # Weather-based risks
        if weather_data:
            weather_risks = self._analyze_weather_risks(weather_data)
            risk_factors.extend(weather_risks['factors'])
            total_risk_score += weather_risks['risk_score']
        
        # Infrastructure risks
        infrastructure_risks = self._analyze_infrastructure_risks(location)
        risk_factors.extend(infrastructure_risks['factors'])
        total_risk_score += infrastructure_risks['risk_score']
        
        return {
            'risk_factors': risk_factors,
            'total_risk_score': min(1.0, total_risk_score),
            'factor_count': len(risk_factors),
            'high_risk_factors': [f for f in risk_factors if f.get('severity') == 'high'],
            'recommendations': self._get_environmental_recommendations(risk_factors)
        }
    
    def _calculate_time_risk_score(self, hour: int) -> float:
        """Calculate risk score based on time of day"""
        if 0 <= hour < 5:  # Very early morning
            return 0.8
        elif 5 <= hour < 8:  # Early morning
            return 0.4
        elif 8 <= hour < 12:  # Morning
            return 0.2
        elif 12 <= hour < 17:  # Afternoon
            return 0.1
        elif 17 <= hour < 20:  # Evening
            return 0.3
        else:  # Night
            return 0.7
    
    def _check_holiday(self, dt: datetime) -> bool:
        """Check if date is a holiday (simplified implementation)"""
        # This would be enhanced with a proper holiday database
        holiday_dates = [
            (1, 1),   # New Year
            (1, 26),  # Republic Day
            (8, 15),  # Independence Day
            (10, 2),  # Gandhi Jayanti
            (12, 25), # Christmas
        ]
        return (dt.month, dt.day) in holiday_dates
    
    def _get_time_recommendations(self, time_period: str, risk_score: float) -> List[str]:
        """Get safety recommendations based on time"""
        recommendations: List[str] = []
        
        if time_period in ['very_early', 'night']:
            recommendations.extend([
                'Avoid isolated areas',
                'Stay in well-lit public spaces',
                'Consider using transportation instead of walking',
                'Keep emergency contacts readily available'
            ])
        elif time_period == 'evening':
            recommendations.extend([
                'Be extra cautious in unfamiliar areas',
                'Avoid displaying valuables',
                'Stay aware of surroundings'
            ])
        
        if risk_score > 0.6:
            recommendations.append('Consider postponing non-essential activities')
        
        return recommendations
    
    def _estimate_crowd_density(self, location: Dict[str, Any], nearby_tourists: int) -> float:
        """Estimate crowd density based on available data"""
        # Base estimation on nearby tourists
        base_density = nearby_tourists
        
        # Enhance estimation based on location type (would use real POI data)
        lat, lng = location.get('latitude', 0), location.get('longitude', 0)
        
        # Simple heuristic based on coordinates (would be replaced with real data)
        if self._is_tourist_hotspot(lat, lng):
            base_density *= 3
        elif self._is_commercial_area(lat, lng):
            base_density *= 2
        
        return base_density
    
    def _calculate_crowd_risk_score(self, density: float, density_level: str) -> float:
        """Calculate risk score based on crowd density"""
        if density_level == 'low':
            return 0.2
        elif density_level == 'medium':
            return 0.3
        elif density_level == 'high':
            return 0.5
        else:  # very_high
            return 0.8
    
    def _get_crowd_safety_factors(self, density_level: str) -> List[str]:
        """Get safety factors based on crowd density"""
        if density_level == 'low':
            return ['Increased personal security awareness needed', 'Less immediate help available']
        elif density_level == 'medium':
            return ['Balanced safety environment', 'Moderate help availability']
        elif density_level == 'high':
            return ['Higher security presence likely', 'More witnesses present', 'Potential for pickpocketing']
        else:  # very_high
            return ['Overcrowding risks', 'Difficult emergency evacuation', 'Higher crime opportunity']
    
    def _get_crowd_recommendations(self, density_level: str, risk_score: float) -> List[str]:
        """Get recommendations based on crowd density"""
        recommendations: List[str] = []
        
        if density_level == 'low':
            recommendations.extend([
                'Stay alert in isolated areas',
                'Keep emergency contacts accessible',
                'Avoid displaying valuables'
            ])
        elif density_level in ['high', 'very_high']:
            recommendations.extend([
                'Keep belongings secure',
                'Stay aware of pickpockets',
                'Know evacuation routes',
                'Avoid pushing through crowds'
            ])
        
        return recommendations
    
    def _analyze_location_risks(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risks based on location characteristics"""
        lat, lng = location.get('latitude', 0), location.get('longitude', 0)
        factors: List[Dict[str, Any]] = []
        risk_score = 0.0
        
        # Check for high-risk areas (would use real crime data)
        if self._is_high_crime_area(lat, lng):
            factors.append({
                'type': 'crime_risk',
                'description': 'High crime area',
                'severity': 'high',
                'risk_contribution': 0.4
            })
            risk_score += 0.4
        
        # Check for tourist scam areas
        if self._is_tourist_scam_area(lat, lng):
            factors.append({
                'type': 'scam_risk',
                'description': 'Known tourist scam area',
                'severity': 'medium',
                'risk_contribution': 0.2
            })
            risk_score += 0.2
        
        return {'factors': factors, 'risk_score': risk_score}
    
    def _analyze_weather_risks(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather-related risks"""
        factors: List[Dict[str, Any]] = []
        risk_score: float = 0.0
        
        # Temperature risks
        temp = weather_data.get('temperature', 25)
        if temp > 40:
            factors.append({
                'type': 'extreme_heat',
                'description': f'Extreme heat: {temp}°C',
                'severity': 'high',
                'risk_contribution': 0.3
            })
            risk_score += 0.3
        elif temp < 5:
            factors.append({
                'type': 'extreme_cold',
                'description': f'Extreme cold: {temp}°C',
                'severity': 'medium',
                'risk_contribution': 0.2
            })
            risk_score += 0.2
        
        # Weather condition risks
        condition = weather_data.get('condition', '').lower()
        if any(term in condition for term in ['storm', 'heavy rain', 'snow']):
            factors.append({
                'type': 'severe_weather',
                'description': f'Severe weather: {condition}',
                'severity': 'high',
                'risk_contribution': 0.4
            })
            risk_score += 0.4
        
        return {'factors': factors, 'risk_score': risk_score}
    
    def _analyze_infrastructure_risks(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze infrastructure-related risks"""
        lat, lng = location.get('latitude', 0), location.get('longitude', 0)
        factors: List[Dict[str, Any]] = []
        risk_score: float = 0.0
        
        # Check for poor infrastructure areas
        if self._is_poor_infrastructure_area(lat, lng):
            factors.append({
                'type': 'infrastructure',
                'description': 'Poor infrastructure area',
                'severity': 'medium',
                'risk_contribution': 0.2
            })
            risk_score += 0.2
        
        return {'factors': factors, 'risk_score': risk_score}
    
    def _get_environmental_recommendations(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Get recommendations based on environmental factors"""
        recommendations: List[str] = []
        
        for factor in risk_factors:
            if factor['type'] == 'extreme_heat':
                recommendations.extend([
                    'Stay hydrated',
                    'Seek shade frequently',
                    'Avoid prolonged outdoor exposure'
                ])
            elif factor['type'] == 'severe_weather':
                recommendations.extend([
                    'Seek indoor shelter',
                    'Avoid outdoor activities',
                    'Monitor weather updates'
                ])
            elif factor['type'] == 'crime_risk':
                recommendations.extend([
                    'Avoid isolated areas',
                    'Travel in groups',
                    'Keep valuables secure'
                ])
        
        return list(set(recommendations))  # Remove duplicates
    
    # Placeholder methods for location analysis (would use real data sources)
    def _is_tourist_hotspot(self, lat: float, lng: float) -> bool:
        """Check if location is a tourist hotspot"""
        # Placeholder implementation
        return False
    
    def _is_commercial_area(self, lat: float, lng: float) -> bool:
        """Check if location is a commercial area"""
        # Placeholder implementation
        return False
    
    def _is_high_crime_area(self, lat: float, lng: float) -> bool:
        """Check if location is a high crime area"""
        # Placeholder implementation
        return False
    
    def _is_tourist_scam_area(self, lat: float, lng: float) -> bool:
        """Check if location is known for tourist scams"""
        # Placeholder implementation
        return False
    
    def _is_poor_infrastructure_area(self, lat: float, lng: float) -> bool:
        """Check if location has poor infrastructure"""
        # Placeholder implementation
        return False


class RiskClassificationEngine:
    """Classifies overall risk level based on movement and environmental analysis"""
    
    def __init__(self):
        self.risk_weights = {
            'movement_analysis': 0.4,
            'environmental_factors': 0.3,
            'time_factors': 0.2,
            'crowd_factors': 0.1
        }
        
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 1.0
        }
    
    def classify_risk(
        self,
        movement_analysis: Dict[str, Any],
        environmental_analysis: Dict[str, Any],
        time_analysis: Dict[str, Any],
        crowd_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify overall risk level based on all analysis factors
        
        Args:
            movement_analysis: Results from movement analysis
            environmental_analysis: Results from environmental analysis
            time_analysis: Results from time analysis
            crowd_analysis: Results from crowd analysis
            
        Returns:
            Dict with risk classification and detailed breakdown
        """
        
        # Calculate weighted risk score
        movement_score = self._extract_movement_risk_score(movement_analysis)
        environmental_score = environmental_analysis.get('total_risk_score', 0.0)
        time_score = time_analysis.get('risk_score', 0.0)
        crowd_score = crowd_analysis.get('risk_score', 0.0)
        
        weighted_score = (
            movement_score * self.risk_weights['movement_analysis'] +
            environmental_score * self.risk_weights['environmental_factors'] +
            time_score * self.risk_weights['time_factors'] +
            crowd_score * self.risk_weights['crowd_factors']
        )
        
        # Classify risk level
        risk_level = self._classify_risk_level(weighted_score)
        
        # Generate risk factors and recommendations
        risk_factors = self._compile_risk_factors(
            movement_analysis, environmental_analysis, time_analysis, crowd_analysis
        )
        
        recommendations = self._generate_recommendations(
            risk_level, risk_factors, movement_analysis, environmental_analysis
        )
        
        # Calculate confidence level
        confidence = self._calculate_confidence(
            movement_analysis, environmental_analysis, time_analysis, crowd_analysis
        )
        
        return {
            'risk_level': risk_level,
            'risk_score': weighted_score,
            'confidence': confidence,
            'breakdown': {
                'movement_score': movement_score,
                'environmental_score': environmental_score,
                'time_score': time_score,
                'crowd_score': crowd_score
            },
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'alert_priority': self._determine_alert_priority(risk_level, weighted_score),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _extract_movement_risk_score(self, movement_analysis: Dict[str, Any]) -> float:
        """Extract overall risk score from movement analysis"""
        sudden_stops_score = movement_analysis.get('sudden_stops', {}).get('risk_score', 0.0)
        rapid_movements_score = movement_analysis.get('rapid_movements', {}).get('risk_score', 0.0)
        abnormal_patterns_score = movement_analysis.get('abnormal_patterns', {}).get('risk_score', 0.0)
        
        # Take the maximum score with some combination
        max_score = max(sudden_stops_score, rapid_movements_score, abnormal_patterns_score)
        avg_score = (sudden_stops_score + rapid_movements_score + abnormal_patterns_score) / 3
        
        return (max_score * 0.7 + avg_score * 0.3)
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify risk level based on score"""
        if risk_score <= self.risk_thresholds['low']:
            return 'low'
        elif risk_score <= self.risk_thresholds['medium']:
            return 'medium'
        else:
            return 'high'
    
    def _compile_risk_factors(
        self,
        movement_analysis: Dict[str, Any],
        environmental_analysis: Dict[str, Any],
        time_analysis: Dict[str, Any],
        crowd_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compile all risk factors into a unified list"""
        risk_factors: List[Dict[str, Any]] = []
        
        # Movement-based risk factors
        if movement_analysis.get('sudden_stops', {}).get('sudden_stops', 0) > 0:
            risk_factors.append({
                'category': 'movement',
                'type': 'sudden_stops',
                'description': f"Detected {movement_analysis['sudden_stops']['sudden_stops']} sudden stops",
                'severity': 'medium' if movement_analysis['sudden_stops']['sudden_stops'] > 2 else 'low'
            })
        
        if movement_analysis.get('rapid_movements', {}).get('rapid_movements', 0) > 0:
            risk_factors.append({
                'category': 'movement',
                'type': 'rapid_movements',
                'description': f"Detected {movement_analysis['rapid_movements']['rapid_movements']} rapid movements",
                'severity': 'high' if movement_analysis['rapid_movements']['rapid_movements'] > 3 else 'medium'
            })
        
        if movement_analysis.get('abnormal_patterns', {}).get('abnormal_patterns', 0) > 0:
            risk_factors.append({
                'category': 'movement',
                'type': 'abnormal_patterns',
                'description': f"Detected {movement_analysis['abnormal_patterns']['abnormal_patterns']} abnormal patterns",
                'severity': 'medium'
            })
        
        # Environmental risk factors
        env_factors = environmental_analysis.get('risk_factors', [])
        for factor in env_factors:
            risk_factors.append({
                'category': 'environmental',
                'type': factor['type'],
                'description': factor['description'],
                'severity': factor['severity']
            })
        
        # Time-based risk factors
        if time_analysis.get('risk_score', 0) > 0.5:
            risk_factors.append({
                'category': 'temporal',
                'type': 'time_risk',
                'description': f"High-risk time period: {time_analysis.get('time_period', 'unknown')}",
                'severity': 'medium' if time_analysis['risk_score'] > 0.7 else 'low'
            })
        
        # Crowd-based risk factors
        crowd_level = crowd_analysis.get('density_level', 'low')
        if crowd_level in ['high', 'very_high']:
            risk_factors.append({
                'category': 'crowd',
                'type': 'crowd_density',
                'description': f"High crowd density: {crowd_level}",
                'severity': 'medium' if crowd_level == 'very_high' else 'low'
            })
        
        return risk_factors
    
    def _generate_recommendations(
        self,
        risk_level: str,
        risk_factors: List[Dict[str, Any]],
        movement_analysis: Dict[str, Any],
        environmental_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate safety recommendations based on risk analysis"""
        recommendations: List[str] = []
        
        # Risk level based recommendations
        if risk_level == 'high':
            recommendations.extend([
                'Consider moving to a safer location immediately',
                'Contact emergency services if in immediate danger',
                'Alert travel companions of your situation',
                'Stay in well-populated, well-lit areas'
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                'Exercise increased caution',
                'Stay aware of your surroundings',
                'Consider changing your route or activity',
                'Keep emergency contacts readily available'
            ])
        else:  # low risk
            recommendations.extend([
                'Continue normal activities with standard precautions',
                'Stay aware of changing conditions'
            ])
        
        # Factor-specific recommendations
        for factor in risk_factors:
            if factor['type'] == 'sudden_stops':
                recommendations.append('If experiencing sudden stops, ensure you are in a safe location')
            elif factor['type'] == 'rapid_movements':
                recommendations.append('If moving rapidly, slow down and assess your situation')
            elif factor['type'] == 'crime_risk':
                recommendations.append('Avoid displaying valuables and stay in groups')
        
        # Environmental recommendations
        env_recommendations = environmental_analysis.get('recommendations', [])
        recommendations.extend(env_recommendations)
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_confidence(
        self,
        movement_analysis: Dict[str, Any],
        environmental_analysis: Dict[str, Any],
        time_analysis: Dict[str, Any],
        crowd_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence level for the risk assessment"""
        confidence_factors: List[float] = []
        
        # Movement analysis confidence
        movement_confidence = movement_analysis.get('abnormal_patterns', {}).get('confidence', 0.5)
        confidence_factors.append(movement_confidence)
        
        # Data availability confidence
        data_availability = 0.8  # Base confidence
        if environmental_analysis.get('risk_factors'):
            data_availability += 0.1
        if time_analysis.get('hour') is not None:
            data_availability += 0.1
        
        confidence_factors.append(min(1.0, data_availability))
        
        return statistics.mean(confidence_factors) if confidence_factors else 0.5
    
    def _determine_alert_priority(self, risk_level: str, risk_score: float) -> str:
        """Determine alert priority for notifications"""
        if risk_level == 'high' and risk_score > 0.8:
            return 'critical'
        elif risk_level == 'high':
            return 'high'
        elif risk_level == 'medium' and risk_score > 0.5:
            return 'medium'
        else:
            return 'low'


class AIMonitoringSystem:
    """Main AI monitoring system that coordinates all analysis components"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.movement_analyzer = MovementAnalyzer()
        self.environmental_monitor = EnvironmentalMonitor()
        self.risk_classifier = RiskClassificationEngine()
        
        # Initialize Auto SOS Detection if available
        if auto_sos_available:
            from auto_sos_detection import AutoSOSDetector, IncidentPackager
            self.auto_sos_detector = AutoSOSDetector(database_path=database_path)
            self.incident_packager = IncidentPackager(database_path=database_path)
        else:
            self.auto_sos_detector = None
            self.incident_packager = None
        
        # Initialize monitoring domain (Mongo-only; no tables to create)
        self._initialize_monitoring_tables()
    
    def _initialize_monitoring_tables(self):
        """Mongo-only: no table initialization required."""
        return
    
    def analyze_tourist_movement(
        self,
        tourist_id: int,
        user_id: Optional[int] = None,
        location_history: Optional[List[Dict[str, Any]]] = None,
        current_location: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        nearby_tourists: int = 0
    ) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis of tourist movement and environment
        
        Args:
            tourist_id: ID of the tourist being monitored
            user_id: ID of the user (if authenticated)
            location_history: List of recent location points
            current_location: Current location coordinates
            weather_data: Optional weather information
            nearby_tourists: Number of nearby tourists
            
        Returns:
            Dict with comprehensive risk analysis and recommendations
        """
        
        # If no location history provided, get from database (Mongo)
        if location_history is None:
            # Approximate last 2 hours by fetching recent points
            fetched = mongo_get_recent_locations(str(tourist_id), limit=200)
            # Reverse to ascending order as previous code expected
            location_history = [
                {
                    'latitude': it.get('latitude'),
                    'longitude': it.get('longitude'),
                    'timestamp': it.get('timestamp'),
                    'accuracy': it.get('accuracy', 0),
                    'speed': it.get('speed', 0),
                    'heading': it.get('heading', 0),
                }
                for it in reversed(fetched)
            ]
        
        if not location_history and not current_location:
            return {
                'error': 'No location data available for analysis',
                'risk_level': 'unknown',
                'risk_score': 0.0
            }
        
        # Ensure current location is in history
        if current_location and current_location not in location_history:
            location_history.append(current_location)
        
        # Perform movement analysis
        movement_analysis = {
            'sudden_stops': self.movement_analyzer.analyze_sudden_stops(location_history),
            'rapid_movements': self.movement_analyzer.analyze_rapid_movements(location_history),
            'abnormal_patterns': self.movement_analyzer.analyze_abnormal_patterns(location_history)
        }
        
        # Perform environmental analysis
        current_time = datetime.now().isoformat()
        time_analysis = self.environmental_monitor.analyze_time_risk(current_time, current_location or {})
        crowd_analysis = self.environmental_monitor.analyze_crowd_density(current_location or {}, nearby_tourists)
        environmental_analysis = self.environmental_monitor.analyze_environmental_factors(current_location or {}, weather_data)
        
        # Classify overall risk
        risk_classification = self.risk_classifier.classify_risk(
            movement_analysis, environmental_analysis, time_analysis, crowd_analysis
        )
        
        # Check for Auto SOS trigger
        auto_sos_triggered = False
        auto_sos_result = None
        incident_package = None
        
        if self.auto_sos_detector and risk_classification['risk_score'] > 0.7:
            # Prepare analysis data for Auto SOS evaluation
            ai_analysis_data: Dict[str, Any] = {
                'tourist_id': tourist_id,
                'user_id': user_id,
                'risk_score': risk_classification['risk_score'],
                'risk_level': risk_classification['risk_level'],
                'confidence': risk_classification['confidence'],
                'movement_analysis': movement_analysis,
                'environmental_analysis': environmental_analysis,
                'time_analysis': time_analysis,
                'crowd_analysis': crowd_analysis,
                'current_location': current_location or {},
                'analysis_timestamp': risk_classification['analysis_timestamp']
            }
            
            # Evaluate for Auto SOS trigger
            if self.auto_sos_detector:
                auto_sos_result = self.auto_sos_detector.evaluate_auto_sos_trigger(ai_analysis_data)
                
                if auto_sos_result and self.incident_packager:
                    auto_sos_triggered = True
                    incident_id = str(uuid.uuid4())
                    
                    # Create incident package
                    incident_package = self.incident_packager.create_incident_package(
                        incident_type='auto_sos',
                        tourist_id=tourist_id,
                        incident_id=incident_id,
                        location=current_location or {},
                        ai_analysis=ai_analysis_data,
                        auto_sos_event=auto_sos_result
                    )
        
        # Store results in database
        monitoring_id = self._store_monitoring_results(
            tourist_id, user_id, movement_analysis, environmental_analysis,
            time_analysis, crowd_analysis, risk_classification, 
            auto_sos_triggered, incident_package
        )
        
        # Generate alerts if necessary
        alerts = self._generate_alerts(monitoring_id, tourist_id, user_id, risk_classification, current_location)
        
        # Compile final result
        result: Dict[str, Any] = {
            'monitoring_id': monitoring_id,
            'tourist_id': tourist_id,
            'analysis_timestamp': risk_classification['analysis_timestamp'],
            'risk_level': risk_classification['risk_level'],
            'risk_score': risk_classification['risk_score'],
            'confidence': risk_classification['confidence'],
            'alert_priority': risk_classification['alert_priority'],
            'movement_analysis': movement_analysis,
            'environmental_analysis': environmental_analysis,
            'time_analysis': time_analysis,
            'crowd_analysis': crowd_analysis,
            'risk_factors': risk_classification['risk_factors'],
            'recommendations': risk_classification['recommendations'],
            'alerts_generated': alerts,
            'auto_sos_triggered': auto_sos_triggered,
            'auto_sos_result': auto_sos_result,
            'incident_package': incident_package,
            'location_data_points': len(location_history)
        }
        
        return result
    
    def _store_monitoring_results(
        self,
        tourist_id: int,
        user_id: Optional[int],
        movement_analysis: Dict[str, Any],
        environmental_analysis: Dict[str, Any],
        time_analysis: Dict[str, Any],
        crowd_analysis: Dict[str, Any],
        risk_classification: Dict[str, Any],
        auto_sos_triggered: bool = False,
        incident_package: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store monitoring results in database"""
        
        # Generate monitoring ID and store in Mongo
        monitoring_id = f"MONITOR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{tourist_id}-{hash(str(movement_analysis)) % 10000}"
        doc: Dict[str, Any] = {
            'monitoring_id': monitoring_id,
            'tourist_id': str(tourist_id),
            'user_id': user_id,
            'risk_level': risk_classification['risk_level'],
            'risk_score': risk_classification['risk_score'],
            'confidence': risk_classification['confidence'],
            'movement_analysis': movement_analysis,
            'environmental_analysis': environmental_analysis,
            'time_analysis': time_analysis,
            'crowd_analysis': crowd_analysis,
            'risk_factors': risk_classification['risk_factors'],
            'recommendations': risk_classification['recommendations'],
            'alert_priority': risk_classification['alert_priority'],
            'auto_sos_triggered': auto_sos_triggered,
            'auto_sos_timestamp': datetime.now().isoformat() if auto_sos_triggered else None,
            'incident_package_id': incident_package.get('incident_id') if incident_package else None,
            'analysis_timestamp': risk_classification['analysis_timestamp'],
        }
        insert_ai_monitoring_result(doc)
        return monitoring_id
    
    def _generate_alerts(
        self,
        monitoring_id: str,
        tourist_id: int,
        user_id: Optional[int],
        risk_classification: Dict[str, Any],
        current_location: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate alerts based on risk analysis"""
        
        alerts: List[Dict[str, Any]] = []
        
        # Generate alert if risk level is medium or high
        if risk_classification['risk_level'] in ['medium', 'high']:
            alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{tourist_id}"
            message = self._create_alert_message(risk_classification)
            insert_risk_alert({
                'alert_id': alert_id,
                'monitoring_id': monitoring_id,
                'tourist_id': str(tourist_id),
                'user_id': user_id,
                'alert_type': 'ai_risk_assessment',
                'priority': risk_classification['alert_priority'],
                'risk_level': risk_classification['risk_level'],
                'latitude': current_location.get('latitude') if current_location else None,
                'longitude': current_location.get('longitude') if current_location else None,
                'message': message,
                'sent_to_admin': True,
                'sent_to_tourist': risk_classification['risk_level'] == 'high'
            })
            alerts.append({
                'alert_id': alert_id,
                'type': 'ai_risk_assessment',
                'priority': risk_classification['alert_priority'],
                'message': message,
                'sent_to_admin': True,
                'sent_to_tourist': risk_classification['risk_level'] == 'high'
            })
        
        return alerts
    
    def _create_alert_message(self, risk_classification: Dict[str, Any]) -> str:
        """Create human-readable alert message"""
        risk_level = risk_classification['risk_level']
        risk_score = risk_classification['risk_score']
        risk_factors = risk_classification['risk_factors']
        
        # Base message
        if risk_level == 'high':
            message = f"🚨 HIGH RISK ALERT: Tourist safety risk detected (Score: {risk_score:.2f})"
        elif risk_level == 'medium':
            message = f"⚠️ MEDIUM RISK: Increased safety monitoring required (Score: {risk_score:.2f})"
        else:
            message = f"ℹ️ LOW RISK: Standard monitoring (Score: {risk_score:.2f})"
        
        # Add risk factors
        if risk_factors:
            factor_descriptions = [f['description'] for f in risk_factors[:3]]  # Top 3 factors
            message += f"\n\nRisk Factors: {', '.join(factor_descriptions)}"
        
        return message
    
    def get_monitoring_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get monitoring data for admin dashboard"""
        # Use Mongo-backed statistics and alerts
        stats = get_ai_statistics(hours)
        alerts_docs = list_risk_alerts(hours=hours, priority='high', limit=20)
        # include 'critical' as well
        alerts_docs += list_risk_alerts(hours=hours, priority='critical', limit=20)
        # Sort and cap 20
        alerts_docs.sort(key=lambda a: a.get('alert_timestamp', ''), reverse=True)
        alerts_docs = alerts_docs[:20]
        high_risk_alerts: List[Dict[str, Any]] = []
        for a in alerts_docs:
            high_risk_alerts.append({
                'alert_id': a.get('alert_id'),
                'tourist_id': a.get('tourist_id'),
                'risk_level': a.get('risk_level'),
                'message': a.get('message'),
                'timestamp': a.get('alert_timestamp'),
                'location': {
                    'latitude': a.get('latitude'),
                    'longitude': a.get('longitude')
                } if a.get('latitude') and a.get('longitude') else None
            })
        anomalies: List[Dict[str, Any]] = []
        return {
            'statistics': {
                'total_analyses': stats.get('analyses_count', 0),
                'high_risk_count': stats.get('risk_distribution', {}).get('high', 0),
                'medium_risk_count': stats.get('risk_distribution', {}).get('medium', 0),
                'low_risk_count': stats.get('risk_distribution', {}).get('low', 0),
                'avg_risk_score': stats.get('avg_risk_score', 0.0),
                'avg_confidence': stats.get('avg_confidence', 0.0),
            },
            'high_risk_alerts': high_risk_alerts,
            'movement_anomalies': anomalies,
            'analysis_period_hours': hours
        }