"""
Test script for AI Monitoring System
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add backend directory to path for both runtime and static analysis
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Also try relative import path for Pylance
try:
    # Try absolute import first
    from ai_monitoring import AIMonitoringSystem, MovementAnalyzer, EnvironmentalMonitor, RiskClassificationEngine  # type: ignore
    print("✅ AI Monitoring modules imported successfully")
except ImportError:
    try:
        # Try relative import from backend
        from backend.ai_monitoring import AIMonitoringSystem, MovementAnalyzer, EnvironmentalMonitor, RiskClassificationEngine  # type: ignore
        print("✅ AI Monitoring modules imported successfully (backend prefix)")
    except ImportError as e:
        print(f"❌ Failed to import AI Monitoring modules: {e}")
        print(f"Backend path: {backend_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        sys.exit(1)

def test_movement_analyzer() -> bool:
    """Test the movement analyzer with sample data"""
    print("\n🧪 Testing Movement Analyzer...")
    
    analyzer = MovementAnalyzer()  # type: ignore
    
    # Sample location history (simulating tourist movement)
    location_history: List[Dict[str, Any]] = [
        {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'accuracy': 5.0,
            'speed': 15.0,
            'heading': 45
        },
        {
            'latitude': 28.6145,
            'longitude': 77.2095,
            'timestamp': (datetime.now() - timedelta(minutes=25)).isoformat(),
            'accuracy': 5.0,
            'speed': 20.0,
            'heading': 50
        },
        {
            'latitude': 28.6145,  # Sudden stop (same location)
            'longitude': 77.2095,
            'timestamp': (datetime.now() - timedelta(minutes=20)).isoformat(),
            'accuracy': 5.0,
            'speed': 0.0,
            'heading': 50
        },
        {
            'latitude': 28.6200,  # Rapid movement
            'longitude': 77.2150,
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'accuracy': 5.0,
            'speed': 80.0,
            'heading': 90
        },
        {
            'latitude': 28.6250,
            'longitude': 77.2200,
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'accuracy': 5.0,
            'speed': 25.0,
            'heading': 45
        }
    ]
    
    # Test sudden stops analysis
    sudden_stops = analyzer.analyze_sudden_stops(location_history)  # type: ignore
    print(f"   Sudden Stops Analysis: {sudden_stops['sudden_stops']} stops detected, Risk Score: {sudden_stops['risk_score']:.3f}")
    
    # Test rapid movements analysis
    rapid_movements = analyzer.analyze_rapid_movements(location_history)  # type: ignore
    print(f"   Rapid Movements Analysis: {rapid_movements['rapid_movements']} rapid movements, Risk Score: {rapid_movements['risk_score']:.3f}")
    
    # Test abnormal patterns analysis
    abnormal_patterns = analyzer.analyze_abnormal_patterns(location_history)  # type: ignore
    print(f"   Abnormal Patterns Analysis: {abnormal_patterns['abnormal_patterns']} patterns detected, Risk Score: {abnormal_patterns['risk_score']:.3f}")
    
    return True

def test_environmental_monitor() -> bool:
    """Test the environmental monitor"""
    print("\n🌍 Testing Environmental Monitor...")
    
    monitor = EnvironmentalMonitor()  # type: ignore
    
    # Test current location (New Delhi coordinates)
    current_location: Dict[str, float] = {
        'latitude': 28.6139,
        'longitude': 77.2090
    }
    
    # Test time risk analysis
    current_time = datetime.now().isoformat()
    time_analysis = monitor.analyze_time_risk(current_time, current_location)  # type: ignore
    print(f"   Time Risk Analysis: {time_analysis['time_period']}, Risk Score: {time_analysis['risk_score']:.3f}")
    
    # Test crowd density analysis
    crowd_analysis = monitor.analyze_crowd_density(current_location, nearby_tourists=15)  # type: ignore
    print(f"   Crowd Analysis: {crowd_analysis['density_level']} density, Risk Score: {crowd_analysis['risk_score']:.3f}")
    
    # Test environmental factors
    weather_data: Dict[str, Any] = {
        'temperature': 35,
        'condition': 'sunny',
        'humidity': 60
    }
    env_analysis = monitor.analyze_environmental_factors(current_location, weather_data)  # type: ignore
    print(f"   Environmental Analysis: {env_analysis['factor_count']} factors, Risk Score: {env_analysis['total_risk_score']:.3f}")
    
    return True

def test_risk_classifier() -> bool:
    """Test the risk classification engine"""
    print("\n⚖️ Testing Risk Classification Engine...")
    
    classifier = RiskClassificationEngine()  # type: ignore
    
    # Sample analysis results
    movement_analysis: Dict[str, Dict[str, Any]] = {
        'sudden_stops': {'risk_score': 0.3, 'sudden_stops': 1},
        'rapid_movements': {'risk_score': 0.6, 'rapid_movements': 2},
        'abnormal_patterns': {'risk_score': 0.4, 'abnormal_patterns': 1}
    }
    
    environmental_analysis: Dict[str, Any] = {
        'total_risk_score': 0.2,
        'risk_factors': [
            {'type': 'crowd_density', 'description': 'High crowd density', 'severity': 'medium'}
        ],
        'recommendations': ['Stay aware of surroundings']
    }
    
    time_analysis: Dict[str, Any] = {
        'risk_score': 0.1,
        'time_period': 'afternoon',
        'hour': 14
    }
    
    crowd_analysis: Dict[str, Any] = {
        'risk_score': 0.3,
        'density_level': 'medium'
    }
    
    # Classify risk
    risk_classification = classifier.classify_risk(  # type: ignore
        movement_analysis, environmental_analysis, time_analysis, crowd_analysis
    )
    
    print(f"   Risk Classification: {risk_classification['risk_level'].upper()}")  # type: ignore
    print(f"   Risk Score: {risk_classification['risk_score']:.3f}")
    print(f"   Confidence: {risk_classification['confidence']:.3f}")
    print(f"   Alert Priority: {risk_classification['alert_priority']}")
    print(f"   Risk Factors: {len(risk_classification['risk_factors'])}")  # type: ignore
    
    return True

def test_full_system() -> bool:
    """Test the complete AI monitoring system"""
    print("\n🤖 Testing Complete AI Monitoring System...")
    
    # Create a temporary database for testing
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        db_path = temp_db.name
    
    try:
        # Initialize AI monitoring system
        ai_system = AIMonitoringSystem(db_path)  # type: ignore
        print("   ✅ AI Monitoring System initialized")
        
        # Test analysis with sample data
        sample_location_history: List[Dict[str, Any]] = [
            {
                'latitude': 28.6139,
                'longitude': 77.2090,
                'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'accuracy': 5.0,
                'speed': 15.0,
                'heading': 45
            },
            {
                'latitude': 28.6200,
                'longitude': 77.2150,
                'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
                'accuracy': 5.0,
                'speed': 80.0,  # Rapid movement
                'heading': 90
            },
            {
                'latitude': 28.6250,
                'longitude': 77.2200,
                'timestamp': datetime.now().isoformat(),
                'accuracy': 5.0,
                'speed': 20.0,
                'heading': 45
            }
        ]
        
        current_location = sample_location_history[-1]
        weather_data: Dict[str, Any] = {'temperature': 32, 'condition': 'clear'}
        
        # Perform full analysis
        result = ai_system.analyze_tourist_movement(  # type: ignore
            tourist_id=12345,
            user_id=67890,
            location_history=sample_location_history,
            current_location=current_location,
            weather_data=weather_data,
            nearby_tourists=8
        )
        
        print(f"   Analysis Result:")
        print(f"   - Monitoring ID: {result['monitoring_id']}")
        print(f"   - Risk Level: {result['risk_level'].upper()}")  # type: ignore
        print(f"   - Risk Score: {result['risk_score']:.3f}")
        print(f"   - Confidence: {result['confidence']:.3f}")
        print(f"   - Alert Priority: {result['alert_priority']}")
        print(f"   - Location Data Points: {result['location_data_points']}")
        print(f"   - Alerts Generated: {len(result['alerts_generated'])}")  # type: ignore
        
        # Test dashboard data
        dashboard_data = ai_system.get_monitoring_dashboard_data(hours=1)  # type: ignore
        print(f"   Dashboard Data:")
        print(f"   - Total Analyses: {dashboard_data['statistics']['total_analyses']}")
        print(f"   - High Risk Count: {dashboard_data['statistics']['high_risk_count']}")
        print(f"   - Average Risk Score: {dashboard_data['statistics']['avg_risk_score']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Full system test failed: {e}")
        return False
    
    finally:
        # Clean up temporary database
        try:
            os.unlink(db_path)
        except:
            pass

def main() -> bool:
    """Run all tests"""
    print("🚀 Starting AI Monitoring System Tests...")
    
    tests: List[tuple[str, Any]] = [
        ("Movement Analyzer", test_movement_analyzer),
        ("Environmental Monitor", test_environmental_monitor),
        ("Risk Classifier", test_risk_classifier),
        ("Full System", test_full_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI Monitoring System tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)