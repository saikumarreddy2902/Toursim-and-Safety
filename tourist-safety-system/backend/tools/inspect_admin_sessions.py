import os
import sys

def main():
    # Ensure backend is on path
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from mongo_db import init_mongo, mongo_enabled, list_admin_sessions_mongo  # type: ignore

    if not mongo_enabled():
        print("MongoDB not enabled. Please set DB_BACKEND='mongo' and MONGO_URI in environment.")
        return
    init_mongo()
    sessions = list_admin_sessions_mongo(limit=20)
    print(f"Admin sessions (latest {len(sessions)}):")
    for s in sessions:
        print("-", {
            'session_id': s.get('session_id'),
            'admin_user_id': s.get('user_id'),
            'login_timestamp': s.get('login_timestamp'),
            'logout_timestamp': s.get('logout_timestamp'),
            'ip_address': s.get('ip_address'),
            'user_agent': s.get('user_agent'),
            'device_info': s.get('device_info'),
            'session_status': s.get('session_status'),
        })

if __name__ == '__main__':
    main()
