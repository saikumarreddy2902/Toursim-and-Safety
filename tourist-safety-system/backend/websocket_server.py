"""
WebSocket Server for Real-Time Admin Dashboard Updates
Provides instant push notifications for SOS alerts, AI monitoring, and tourist updates
"""

from datetime import datetime
from typing import Set, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room  # type: ignore
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False  # type: ignore
    logger.warning("flask-socketio not installed. Install with: pip install flask-socketio python-socketio")

class WebSocketManager:
    """Manages WebSocket connections and real-time updates"""
    
    def __init__(self, app=None):  # type: ignore
        self.socketio = None
        self.connected_clients: Set[str] = set()
        self.admin_sessions: Dict[str, Any] = {}
        
        if app and SOCKETIO_AVAILABLE:
            self.init_app(app)  # type: ignore
    
    def init_app(self, app):  # type: ignore
        """Initialize SocketIO with Flask app"""
        if not SOCKETIO_AVAILABLE:
            logger.error("Cannot initialize WebSocket: flask-socketio not installed")
            return
        
        self.socketio = SocketIO(  # type: ignore
            app,  # type: ignore
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=False
        )
        
        # Register event handlers
        self._register_handlers()
        logger.info("WebSocket server initialized successfully")
    
    def _register_handlers(self):
        """Register SocketIO event handlers"""
        
        @self.socketio.on('connect')  # type: ignore
        def handle_connect():  # type: ignore
            """Handle new client connection"""
            client_id = str(id(self))
            self.connected_clients.add(client_id)
            logger.info(f"Client connected: {client_id}. Total clients: {len(self.connected_clients)}")
            emit('connection_established', {  # type: ignore
                'status': 'connected',
                'timestamp': datetime.now().isoformat(),
                'message': 'Real-time updates enabled'
            })
        
        @self.socketio.on('disconnect')  # type: ignore
        def handle_disconnect():  # type: ignore
            """Handle client disconnection"""
            client_id = str(id(self))
            if client_id in self.connected_clients:
                self.connected_clients.remove(client_id)
            logger.info(f"Client disconnected: {client_id}. Total clients: {len(self.connected_clients)}")
        
        @self.socketio.on('join_admin')  # type: ignore
        def handle_join_admin(data):  # type: ignore
            """Admin joins their dedicated room"""
            admin_id = data.get('admin_id', 'default_admin')  # type: ignore
            join_room(f'admin_{admin_id}')  # type: ignore
            self.admin_sessions[admin_id] = {  # type: ignore
                'joined_at': datetime.now(),
                'subscriptions': data.get('subscriptions', ['sos', 'ai_alerts', 'tourists'])  # type: ignore
            }
            logger.info(f"Admin {admin_id} joined room with subscriptions: {self.admin_sessions[admin_id]['subscriptions']}")
            emit('joined_admin_room', {  # type: ignore
                'admin_id': admin_id,
                'subscriptions': self.admin_sessions[admin_id]['subscriptions']
            })
        
        @self.socketio.on('subscribe')  # type: ignore
        def handle_subscribe(data):  # type: ignore
            """Subscribe to specific event types"""
            event_types = data.get('event_types', [])  # type: ignore
            for event_type in event_types:  # type: ignore
                join_room(event_type)  # type: ignore
            logger.info(f"Client subscribed to: {event_types}")
            emit('subscribed', {'event_types': event_types})  # type: ignore
        
        @self.socketio.on('unsubscribe')  # type: ignore
        def handle_unsubscribe(data):  # type: ignore
            """Unsubscribe from event types"""
            event_types = data.get('event_types', [])  # type: ignore
            for event_type in event_types:  # type: ignore
                leave_room(event_type)  # type: ignore
            logger.info(f"Client unsubscribed from: {event_types}")
            emit('unsubscribed', {'event_types': event_types})  # type: ignore
    
    # ========== Broadcasting Methods ==========
    
    def broadcast_sos_alert(self, alert_data: Dict[str, Any]):
        """Broadcast new SOS alert to all connected admins"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'sos_alert',
            'alert': alert_data,
            'timestamp': datetime.now().isoformat(),
            'priority': alert_data.get('priority', 'high')
        }
        
        self.socketio.emit('new_sos_alert', payload, room='sos')  # type: ignore
        logger.info(f"Broadcasted SOS alert: {alert_data.get('alert_id', 'unknown')}")
    
    def broadcast_ai_alert(self, ai_alert: Dict[str, Any]):
        """Broadcast new AI monitoring alert"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'ai_alert',
            'alert': ai_alert,
            'timestamp': datetime.now().isoformat(),
            'risk_level': ai_alert.get('risk_level', 'medium')
        }
        
        self.socketio.emit('new_ai_alert', payload, room='ai_alerts')  # type: ignore
        logger.info(f"Broadcasted AI alert: {ai_alert.get('alert_type', 'unknown')}")
    
    def broadcast_tourist_update(self, tourist_data: Dict[str, Any], update_type: str = 'location'):
        """Broadcast tourist location/status update"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'tourist_update',
            'update_type': update_type,
            'tourist': tourist_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('tourist_update', payload, room='tourists')  # type: ignore
        logger.info(f"Broadcasted tourist update: {tourist_data.get('tourist_id', 'unknown')}")
    
    def broadcast_incident_report(self, report_data: Dict[str, Any]):
        """Broadcast new incident report"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'incident_report',
            'report': report_data,
            'timestamp': datetime.now().isoformat(),
            'severity': report_data.get('severity', 'medium')
        }
        
        self.socketio.emit('new_incident_report', payload, room='incidents')  # type: ignore
        logger.info(f"Broadcasted incident report: {report_data.get('report_id', 'unknown')}")
    
    def broadcast_stats_update(self, stats: Dict[str, Any]):
        """Broadcast updated dashboard statistics"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'stats_update',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('stats_update', payload, broadcast=True)  # type: ignore
        logger.info("Broadcasted stats update to all clients")
    
    def notify_admin(self, admin_id: str, notification: Dict[str, Any]):
        """Send notification to specific admin"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'admin_notification',
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('admin_notification', payload, room=f'admin_{admin_id}')  # type: ignore
        logger.info(f"Sent notification to admin {admin_id}: {notification.get('message', '')}")
    
    def broadcast_system_message(self, message: str, level: str = 'info'):
        """Broadcast system-wide message"""
        if not self.socketio:
            return
        
        payload: Dict[str, Any] = {  # type: ignore
            'type': 'system_message',
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('system_message', payload, broadcast=True)  # type: ignore
        logger.info(f"Broadcasted system message ({level}): {message}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current WebSocket server statistics"""
        return {
            'connected_clients': len(self.connected_clients),
            'admin_sessions': len(self.admin_sessions),
            'socketio_available': SOCKETIO_AVAILABLE,
            'status': 'running' if self.socketio else 'not_initialized'
        }


# Global WebSocket manager instance
ws_manager = WebSocketManager()


# Helper functions for easy integration
def init_websocket(app):  # type: ignore
    """Initialize WebSocket with Flask app"""
    ws_manager.init_app(app)  # type: ignore
    return ws_manager


def broadcast_sos_alert(alert_data: Dict[str, Any]):
    """Broadcast SOS alert - convenience function"""
    ws_manager.broadcast_sos_alert(alert_data)


def broadcast_ai_alert(ai_alert: Dict[str, Any]):
    """Broadcast AI alert - convenience function"""
    ws_manager.broadcast_ai_alert(ai_alert)


def broadcast_tourist_update(tourist_data: Dict[str, Any], update_type: str = 'location'):
    """Broadcast tourist update - convenience function"""
    ws_manager.broadcast_tourist_update(tourist_data, update_type)


def broadcast_incident_report(report_data: Dict[str, Any]):
    """Broadcast incident report - convenience function"""
    ws_manager.broadcast_incident_report(report_data)


def get_websocket_stats() -> Dict[str, Any]:
    """Get WebSocket statistics - convenience function"""
    return ws_manager.get_stats()


# Example usage in Flask route:
"""
from backend.websocket_server import broadcast_sos_alert, init_websocket

# In app initialization:
socketio = init_websocket(app)

# In SOS alert route:
@app.route('/api/sos-alert', methods=['POST'])
def create_sos_alert():
    alert_data = request.get_json()
    # ... save to database ...
    
    # Broadcast to all connected admins
    broadcast_sos_alert(alert_data)
    
    return jsonify({'success': True})
"""
