"""
Sample Data Generator for Tourist Safety System
Generates realistic demo data for testing and training purposes
"""
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime, timedelta
import random
import string
from typing import List, Dict, Any
import pymongo  # type: ignore
from bson import ObjectId  # type: ignore

# Sample data pools
FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Arjun", "Kavya",
    "John", "Sarah", "Michael", "Emma", "David", "Sophia", "James", "Olivia",
    "Liam", "Ava", "Noah", "Isabella", "Ethan", "Mia", "Mason", "Charlotte",
    "Ravi", "Deepika", "Suresh", "Meera", "Karthik", "Divya", "Arun", "Lakshmi"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Singh", "Patel", "Reddy", "Iyer", "Nair", "Chopra",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Gupta", "Verma", "Rao", "Krishnan", "Menon", "Pillai", "Desai", "Shah"
]

NATIONALITIES = [
    "Indian", "American", "British", "Canadian", "Australian", "German", "French",
    "Japanese", "Chinese", "Brazilian", "Mexican", "Italian", "Spanish", "Korean",
    "Russian", "Dutch", "Swedish", "Norwegian", "Danish", "Belgian"
]

INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
    "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana"
]

EMERGENCY_TYPES = [
    "MEDICAL_EMERGENCY", "ACCIDENT", "THEFT", "HARASSMENT", "LOST", "NATURAL_DISASTER",
    "FIRE", "VIOLENCE", "HEALTH_ISSUE", "PANIC_ATTACK", "ASSISTANCE_NEEDED"
]

INCIDENT_TYPES = [
    "Medical Emergency", "Traffic Accident", "Theft/Robbery", "Harassment",
    "Lost/Stranded", "Natural Disaster", "Health Issue", "Safety Concern"
]

# Location coordinates for major Indian tourist spots
TOURIST_LOCATIONS = [
    {"name": "Gateway of India, Mumbai", "lat": 18.9220, "lng": 72.8347},
    {"name": "Taj Mahal, Agra", "lat": 27.1751, "lng": 78.0421},
    {"name": "Red Fort, Delhi", "lat": 28.6562, "lng": 77.2410},
    {"name": "Hawa Mahal, Jaipur", "lat": 26.9239, "lng": 75.8267},
    {"name": "Golden Temple, Amritsar", "lat": 31.6200, "lng": 74.8765},
    {"name": "Qutub Minar, Delhi", "lat": 28.5244, "lng": 77.1855},
    {"name": "Mysore Palace", "lat": 12.3051, "lng": 76.6551},
    {"name": "Goa Beach", "lat": 15.2993, "lng": 74.1240},
    {"name": "Hampi Ruins", "lat": 15.3350, "lng": 76.4600},
    {"name": "Ajanta Caves", "lat": 20.5519, "lng": 75.7033}
]

def generate_tourist_id() -> str:
    """Generate random tourist ID"""
    return f"T{random.randint(10000, 99999)}"

def generate_phone() -> str:
    """Generate random Indian phone number"""
    return f"+91{random.randint(7000000000, 9999999999)}"

def generate_email(first_name: str, last_name: str) -> str:
    """Generate email address"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

def generate_passport() -> str:
    """Generate random passport number"""
    return f"{''.join(random.choices(string.ascii_uppercase, k=2))}{random.randint(1000000, 9999999)}"

def random_date_between(start_days_ago: int, end_days_ago: int) -> datetime:
    """Generate random datetime between two dates"""
    # Swap if start is greater than end
    if start_days_ago > end_days_ago:
        start_days_ago, end_days_ago = end_days_ago, start_days_ago
    
    start = datetime.now() - timedelta(days=end_days_ago)
    end = datetime.now() - timedelta(days=start_days_ago)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_tourists(count: int = 50) -> List[Dict[str, Any]]:
    """Generate sample tourist data"""
    tourists = []
    
    for _ in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        nationality = random.choice(NATIONALITIES)
        
        tourist = {
            "tourist_id": generate_tourist_id(),
            "full_name": f"{first_name} {last_name}",
            "name": f"{first_name} {last_name}",
            "nationality": nationality,
            "phone_number": generate_phone(),
            "email": generate_email(first_name, last_name),
            "passport_number": generate_passport(),
            "date_of_birth": random_date_between(18*365, 70*365).strftime("%Y-%m-%d"),
            "gender": random.choice(["Male", "Female", "Other"]),
            "address": f"{random.randint(1, 999)} {random.choice(INDIAN_CITIES)} Street, {nationality}",
            "emergency_contact": {
                "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                "phone": generate_phone(),
                "relationship": random.choice(["Spouse", "Parent", "Sibling", "Friend"])
            },
            "status": random.choice(["active", "active", "active", "inactive"]),  # 75% active
            "created_at": random_date_between(90, 1).isoformat(),
            "last_updated": datetime.now().isoformat(),
            "risk_level": random.choice(["low", "low", "low", "medium", "high"]),  # Mostly low
            "current_location": random.choice(TOURIST_LOCATIONS)
        }
        
        tourists.append(tourist)
    
    return tourists

def generate_sos_alerts(tourists: List[Dict[str, Any]], count: int = 20) -> List[Dict[str, Any]]:
    """Generate sample SOS alerts"""
    alerts = []
    
    for _ in range(count):
        tourist = random.choice(tourists)
        location = tourist["current_location"]
        
        # Add slight variation to location
        lat_offset = random.uniform(-0.01, 0.01)
        lng_offset = random.uniform(-0.01, 0.01)
        
        created_at = random_date_between(30, 0)
        status = random.choice(["ACTIVE", "ACTIVE", "RESPONDED", "RESOLVED", "RESOLVED"])
        
        alert = {
            "sos_id": f"SOS{random.randint(1000, 9999)}",
            "tourist_id": tourist["tourist_id"],
            "timestamp": created_at.isoformat(),
            "created_at": created_at.isoformat(),
            "emergency_type": random.choice(EMERGENCY_TYPES),
            "message": random.choice([
                "Emergency! Need immediate help!",
                "Medical assistance required urgently",
                "Lost and unable to find way back",
                "Feeling unsafe, need help",
                "Accident occurred, need ambulance",
                "Emergency SOS triggered"
            ]),
            "location_lat": location["lat"] + lat_offset,
            "location_lng": location["lng"] + lng_offset,
            "location_accuracy": random.randint(5, 50),
            "page": random.choice(["dashboard", "profile", "emergency"]),
            "language": random.choice(["en", "hi", "ta", "te"]),
            "status": status,
            "admin_notified": True,
            "battery_level": random.randint(10, 100)
        }
        
        if status in ["RESPONDED", "RESOLVED"]:
            alert["admin_response"] = random.choice([
                "Help is on the way! Emergency services notified.",
                "We have received your alert. Stay calm, assistance is coming.",
                "Authorities have been contacted. Please stay at your location."
            ])
            alert["responded_by"] = "admin"
            alert["updated_at"] = (created_at + timedelta(minutes=random.randint(5, 30))).isoformat()
        
        alerts.append(alert)
    
    return alerts

def generate_panic_alerts(tourists: List[Dict[str, Any]], count: int = 30) -> List[Dict[str, Any]]:
    """Generate sample panic alerts"""
    alerts = []
    
    for _ in range(count):
        tourist = random.choice(tourists)
        location = tourist["current_location"]
        created_at = random_date_between(60, 0)
        
        alert = {
            "alert_id": f"PA{random.randint(10000, 99999)}",
            "tourist_id": tourist["tourist_id"],
            "tourist_name": tourist["full_name"],
            "alert_type": "panic_button",
            "severity_level": random.choice(["high", "high", "medium", "critical"]),
            "latitude": location["lat"] + random.uniform(-0.02, 0.02),
            "longitude": location["lng"] + random.uniform(-0.02, 0.02),
            "location_accuracy": random.randint(5, 100),
            "address": location["name"],
            "status": random.choice(["active", "active", "acknowledged", "resolved"]),
            "timestamp": created_at.isoformat(),
            "admin_response_time": random.randint(2, 30) if random.random() > 0.3 else None,
            "resolution_notes": "Alert resolved successfully" if random.random() > 0.5 else None,
            "user_info": {
                "user_id": tourist["tourist_id"],
                "name": tourist["full_name"],
                "phone": tourist["phone_number"]
            },
            "tourist_info": {
                "tourist_id": tourist["tourist_id"],
                "name": tourist["full_name"],
                "nationality": tourist["nationality"]
            }
        }
        
        alerts.append(alert)
    
    return alerts

def generate_geofence_violations(tourists: List[Dict[str, Any]], count: int = 15) -> List[Dict[str, Any]]:
    """Generate sample geofence violations"""
    violations = []
    
    restricted_zones = [
        {"name": "Military Area - Red Fort", "lat": 28.6562, "lng": 77.2410, "radius": 500},
        {"name": "Restricted Zone - Border Area", "lat": 30.9010, "lng": 75.8573, "radius": 1000},
        {"name": "Conservation Area - Wildlife Sanctuary", "lat": 24.0854, "lng": 74.6292, "radius": 2000}
    ]
    
    for _ in range(count):
        tourist = random.choice(tourists)
        zone = random.choice(restricted_zones)
        
        violation = {
            "id": f"GV{random.randint(100, 999)}",
            "tourist_id": tourist["tourist_id"],
            "tourist_name": tourist["full_name"],
            "zone_name": zone["name"],
            "zone_type": "restricted",
            "latitude": zone["lat"] + random.uniform(-0.005, 0.005),
            "longitude": zone["lng"] + random.uniform(-0.005, 0.005),
            "timestamp": random_date_between(45, 0).isoformat(),
            "severity": random.choice(["low", "medium", "high"]),
            "notified": True
        }
        
        violations.append(violation)
    
    return violations

def generate_blockchain_records(tourists: List[Dict[str, Any]], count: int = 40) -> List[Dict[str, Any]]:
    """Generate sample blockchain records"""
    records = []
    
    for i in range(count):
        tourist = random.choice(tourists)
        timestamp = random_date_between(90, 0)
        
        record = {
            "block_index": i + 1,
            "timestamp": timestamp.isoformat(),
            "previous_hash": ''.join(random.choices(string.hexdigits.lower(), k=64)),
            "hash": ''.join(random.choices(string.hexdigits.lower(), k=64)),
            "data": {
                "tourist_id": tourist["tourist_id"],
                "action": random.choice(["registration", "alert_triggered", "location_update", "emergency_sos"]),
                "data_classification": "SENSITIVE_TOURIST_DATA"
            },
            "nonce": random.randint(100000, 999999),
            "verified": True
        }
        
        records.append(record)
    
    return records

def generate_incident_reports(tourists: List[Dict[str, Any]], alerts: List[Dict[str, Any]], count: int = 25) -> List[Dict[str, Any]]:
    """Generate sample incident reports"""
    reports = []
    
    for _ in range(count):
        tourist = random.choice(tourists)
        incident_time = random_date_between(60, 0)
        response_time = random.randint(5, 60)
        
        report = {
            "report_id": f"IR{random.randint(10000, 99999)}",
            "tourist_id": tourist["tourist_id"],
            "tourist_name": tourist["full_name"],
            "incident_type": random.choice(INCIDENT_TYPES),
            "incident_timestamp": incident_time.isoformat(),
            "generated_at": (incident_time + timedelta(hours=1)).isoformat(),
            "status": random.choice(["resolved", "resolved", "pending", "in_progress"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "description": f"Incident involving {tourist['full_name']} requiring assistance",
            "location": {
                "latitude": random.uniform(15.0, 30.0),
                "longitude": random.uniform(72.0, 85.0),
                "address": random.choice(TOURIST_LOCATIONS)["name"]
            },
            "response_time_minutes": response_time,
            "responders": [
                {
                    "name": f"Officer {random.choice(FIRST_NAMES)}",
                    "role": random.choice(["Police", "Medical", "Fire", "Security"]),
                    "contact": generate_phone()
                }
            ],
            "resolution_summary": "Incident resolved successfully with no major issues" if random.random() > 0.3 else None
        }
        
        reports.append(report)
    
    return reports

def generate_ai_monitoring_alerts(tourists: List[Dict[str, Any]], count: int = 35) -> List[Dict[str, Any]]:
    """Generate sample AI monitoring alerts"""
    alerts = []
    
    for _ in range(count):
        tourist = random.choice(tourists)
        alert_time = random_date_between(14, 0)  # Last 2 weeks
        
        alert = {
            "alert_id": f"AI{random.randint(10000, 99999)}",
            "tourist_id": tourist["tourist_id"],
            "alert_timestamp": alert_time.isoformat(),
            "risk_level": random.choice(["low", "low", "medium", "high"]),
            "priority": random.choice(["low", "medium", "medium", "high", "critical"]),
            "message": random.choice([
                "Unusual movement pattern detected",
                "Tourist entered restricted area",
                "Prolonged stay in high-risk zone",
                "Abnormal activity pattern identified",
                "Potential safety concern detected"
            ]),
            "location": {
                "latitude": random.uniform(15.0, 30.0),
                "longitude": random.uniform(72.0, 85.0)
            },
            "confidence_score": random.uniform(0.6, 0.99),
            "acknowledged": random.choice([True, False]),
            "resolved": random.choice([True, False, False]),
            "ai_analysis": {
                "risk_factors": random.sample([
                    "location_pattern",
                    "time_of_day",
                    "zone_violation",
                    "communication_loss"
                ], k=random.randint(1, 3))
            }
        }
        
        alerts.append(alert)
    
    return alerts

def insert_to_mongodb():
    """Insert sample data into MongoDB"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["tourist_safety"]
        
        print("🔄 Generating sample data...")
        
        # Generate all data
        tourists = generate_tourists(50)
        sos_alerts = generate_sos_alerts(tourists, 20)
        panic_alerts = generate_panic_alerts(tourists, 30)
        geofence_violations = generate_geofence_violations(tourists, 15)
        blockchain_records = generate_blockchain_records(tourists, 40)
        incident_reports = generate_incident_reports(tourists, sos_alerts, 25)
        ai_alerts = generate_ai_monitoring_alerts(tourists, 35)
        
        print("\n📥 Inserting data into MongoDB...\n")
        
        # Insert tourists
        if tourists:
            db.tourists.insert_many(tourists)
            print(f"✅ Inserted {len(tourists)} tourists")
        
        # Insert SOS alerts
        if sos_alerts:
            db.sos_alerts.insert_many(sos_alerts)
            print(f"✅ Inserted {len(sos_alerts)} SOS alerts")
        
        # Insert panic alerts
        if panic_alerts:
            db.panic_alerts.insert_many(panic_alerts)
            print(f"✅ Inserted {len(panic_alerts)} panic alerts")
        
        # Insert geofence violations
        if geofence_violations:
            db.geofence_violations.insert_many(geofence_violations)
            print(f"✅ Inserted {len(geofence_violations)} geofence violations")
        
        # Insert blockchain records
        if blockchain_records:
            db.blockchain.insert_many(blockchain_records)
            print(f"✅ Inserted {len(blockchain_records)} blockchain records")
        
        # Insert incident reports
        if incident_reports:
            db.incident_reports.insert_many(incident_reports)
            print(f"✅ Inserted {len(incident_reports)} incident reports")
        
        # Insert AI monitoring alerts
        if ai_alerts:
            db.ai_monitoring_alerts.insert_many(ai_alerts)
            print(f"✅ Inserted {len(ai_alerts)} AI monitoring alerts")
        
        print(f"\n🎉 Sample data generation complete!")
        print(f"\n📊 Summary:")
        print(f"   • {len(tourists)} tourists")
        print(f"   • {len(sos_alerts)} SOS alerts")
        print(f"   • {len(panic_alerts)} panic alerts")
        print(f"   • {len(geofence_violations)} geofence violations")
        print(f"   • {len(blockchain_records)} blockchain records")
        print(f"   • {len(incident_reports)} incident reports")
        print(f"   • {len(ai_alerts)} AI monitoring alerts")
        print(f"\n✨ Total: {sum([len(tourists), len(sos_alerts), len(panic_alerts), len(geofence_violations), len(blockchain_records), len(incident_reports), len(ai_alerts)])} records")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("  TOURIST SAFETY SYSTEM - SAMPLE DATA GENERATOR")
    print("=" * 60)
    print()
    
    insert_to_mongodb()
    
    print()
    print("=" * 60)
