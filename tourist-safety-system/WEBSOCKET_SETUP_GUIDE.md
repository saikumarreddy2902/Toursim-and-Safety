# WebSocket Real-Time Updates - Setup Guide

## 🚀 Overview

The admin dashboard now supports **WebSocket-based real-time updates** for instant notifications without polling. This provides:

- ⚡ **Instant SOS alerts** - No 30-second delay
- 🤖 **Live AI monitoring** - Real-time risk assessments
- 📍 **Tourist tracking** - Live location updates on map
- 📊 **Dashboard statistics** - Auto-updating counts and metrics
- 🔔 **System notifications** - Immediate admin alerts

## 📋 Installation

### 1. Install Python Dependencies

```bash
pip install flask-socketio python-socketio
```

### 2. Update Flask App

In your main Flask app file (e.g., `app.py` or `run_app.py`):

```python
from backend.websocket_server import init_websocket

# Initialize Flask app
app = Flask(__name__)

# Initialize WebSocket
socketio = init_websocket(app)

# Run with SocketIO instead of regular Flask
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

### 3. Integrate with Existing Routes

In your SOS alert route:

```python
from backend.websocket_server import broadcast_sos_alert

@app.route('/api/sos-alert', methods=['POST'])
def create_sos_alert():
    alert_data = request.get_json()
    
    # Save to database
    db.sos_alerts.insert_one(alert_data)
    
    # Broadcast to all connected admins
    broadcast_sos_alert(alert_data)
    
    return jsonify({'success': True})
```

Similarly for AI alerts:

```python
from backend.websocket_server import broadcast_ai_alert

@app.route('/api/ai/monitor/analyze', methods=['POST'])
def ai_analysis():
    # ... perform AI analysis ...
    
    if alert_generated:
        broadcast_ai_alert(alert_data)
    
    return jsonify({'success': True})
```

## 🎯 Features

### 1. Real-Time SOS Alerts

**What happens:**
- Tourist triggers SOS button
- Backend broadcasts alert via WebSocket
- All connected admin dashboards receive instant notification
- Alert badge updates automatically
- Sound alert plays
- Map marker appears immediately

**No polling delay!** Previously: 30-second delay. Now: Instant.

### 2. Live AI Monitoring

**What happens:**
- AI analysis detects risk
- WebSocket pushes alert to admins
- Dashboard updates risk charts
- Filtered alerts refresh
- Toast notification appears

### 3. Tourist Location Updates

**What happens:**
- Tourist location changes
- Backend broadcasts update
- Map markers move in real-time
- Tourist cache updates
- No table refresh needed

### 4. Incident Reports

**What happens:**
- New incident created
- WebSocket notifies admins
- Reports table updates
- Statistics refresh

## 🔧 Configuration

### Backend WebSocket Manager

The `WebSocketManager` class in `backend/websocket_server.py` provides:

```python
# Initialize
ws_manager = WebSocketManager(app)

# Broadcast methods
ws_manager.broadcast_sos_alert(alert_data)
ws_manager.broadcast_ai_alert(ai_alert)
ws_manager.broadcast_tourist_update(tourist_data, update_type='location')
ws_manager.broadcast_incident_report(report_data)
ws_manager.broadcast_stats_update(stats)

# Admin-specific notifications
ws_manager.notify_admin(admin_id, notification)

# System-wide messages
ws_manager.broadcast_system_message("System maintenance in 10 minutes", level='warning')
```

### Frontend WebSocket Client

The `WebSocketClient` class automatically:

1. **Connects** to WebSocket server on page load
2. **Subscribes** to event types: `['sos', 'ai_alerts', 'tourists', 'incidents']`
3. **Handles** incoming events with appropriate UI updates
4. **Reconnects** automatically (up to 5 attempts)
5. **Falls back** to polling if WebSocket unavailable

## 📡 Event Types

### Server → Client Events

| Event | Description | Payload |
|-------|-------------|---------|
| `new_sos_alert` | New SOS emergency alert | `{type, alert, timestamp, priority}` |
| `new_ai_alert` | AI monitoring alert | `{type, alert, timestamp, risk_level}` |
| `tourist_update` | Tourist location/status change | `{type, update_type, tourist, timestamp}` |
| `new_incident_report` | New incident report created | `{type, report, timestamp, severity}` |
| `stats_update` | Dashboard statistics update | `{type, stats, timestamp}` |
| `system_message` | System-wide announcement | `{type, message, level, timestamp}` |

### Client → Server Events

| Event | Description | Payload |
|-------|-------------|---------|
| `connect` | Client connection initiated | Auto |
| `disconnect` | Client disconnected | Auto |
| `join_admin` | Join admin-specific room | `{admin_id, subscriptions}` |
| `subscribe` | Subscribe to event types | `{event_types: ['sos', 'ai_alerts']}` |
| `unsubscribe` | Unsubscribe from events | `{event_types: ['tourists']}` |

## 🎨 UI Indicators

### Connection Status Badge

A live indicator appears in the top-right corner:

- 🟢 **Live** (green gradient) - WebSocket connected
- ⚪ **Offline** (gray) - Disconnected, using polling

### Visual Feedback

- **Toast notifications** for each real-time event
- **Badge animations** when counts update
- **Sound alerts** for critical events (SOS)
- **Map animations** for location updates

## 🔄 Fallback Mechanism

If WebSocket connection fails:

1. **Automatic retry** - Up to 5 attempts with 3-second delays
2. **Graceful fallback** - Reverts to 30-second polling
3. **User notification** - Toast message: "Using polling mode"
4. **No data loss** - All data still loads, just slower

## 🧪 Testing

### Test WebSocket Connection

Open browser console on admin dashboard:

```javascript
// Check WebSocket status
console.log(wsClient.connected); // Should be true

// Manual disconnect/reconnect
wsClient.disconnect();
wsClient.connect();

// Send test subscription
wsClient.socket.emit('subscribe', { event_types: ['sos'] });
```

### Test Backend Broadcasting

From Python:

```python
from backend.websocket_server import broadcast_system_message

# Send test message
broadcast_system_message("Test broadcast at " + str(datetime.now()), level='info')
```

### Monitor WebSocket Traffic

1. Open browser DevTools → Network tab
2. Filter by "WS" (WebSocket)
3. Click on socket connection
4. View "Messages" tab to see real-time events

## 🚨 Troubleshooting

### WebSocket Not Connecting

**Problem:** Console shows "Socket.IO not available"

**Solution:**
- Check if Socket.IO CDN script loaded: View source → search for `socket.io.min.js`
- Check network connectivity
- Verify backend has `flask-socketio` installed

### Connection Drops Frequently

**Problem:** Status indicator keeps switching between Live/Offline

**Solution:**
- Check server logs for connection errors
- Increase `maxReconnectAttempts` in WebSocket client config
- Check firewall/proxy settings
- Use `socketio.run(app, allow_unsafe_werkzeug=True)` in development

### Events Not Received

**Problem:** Real-time updates not appearing

**Solution:**
- Verify subscription: `wsClient.subscriptions` should include event type
- Check backend is calling broadcast functions
- Verify event names match exactly (case-sensitive)
- Check browser console for errors

## 📊 Performance Impact

### Resource Usage

- **Network:** ~1-5 KB/min idle, ~10-50 KB/min active
- **CPU:** Minimal (event-driven)
- **Memory:** ~5-10 MB per connection
- **Battery:** More efficient than polling

### Scaling Considerations

For high-traffic deployments:

1. **Use Redis adapter** for multi-server setups:
   ```python
   from flask_socketio import SocketIO
   socketio = SocketIO(app, message_queue='redis://localhost:6379')
   ```

2. **Limit connections** per admin:
   ```python
   socketio = SocketIO(app, max_http_buffer_size=1e6)
   ```

3. **Monitor with stats**:
   ```python
   stats = ws_manager.get_stats()
   # {'connected_clients': 12, 'admin_sessions': 3}
   ```

## 🎯 Best Practices

1. **Always provide fallback** - Keep polling as backup
2. **Handle disconnections gracefully** - Show UI indicators
3. **Throttle updates** - Don't broadcast every millisecond
4. **Validate data** - Sanitize broadcast payloads
5. **Log events** - Track WebSocket activity for debugging
6. **Test thoroughly** - Simulate disconnections, high load
7. **Monitor performance** - Track connection counts, latency

## 📚 API Reference

### Backend Functions

```python
# Initialize
from backend.websocket_server import init_websocket
socketio = init_websocket(app)

# Broadcast functions
from backend.websocket_server import (
    broadcast_sos_alert,
    broadcast_ai_alert,
    broadcast_tourist_update,
    broadcast_incident_report,
    get_websocket_stats
)

# Usage
broadcast_sos_alert({
    'alert_id': '123',
    'tourist_id': 'T456',
    'location': {'latitude': 28.6139, 'longitude': 77.2090},
    'priority': 'critical'
})
```

### Frontend API

```javascript
// Access global WebSocket client
wsClient.connect();          // Connect
wsClient.disconnect();       // Disconnect
wsClient.connected;          // Check status
wsClient.subscriptions;      // View subscriptions

// Manual event handling
wsClient.socket.on('custom_event', (data) => {
    console.log('Custom event:', data);
});
```

## 🔐 Security Notes

- WebSocket connections inherit Flask session authentication
- Use HTTPS/WSS in production
- Validate all incoming data on backend
- Implement rate limiting for broadcast events
- Monitor for abnormal connection patterns

## 📝 Example Integration

**Complete SOS Alert Flow:**

```python
# Backend (routes.py)
from backend.websocket_server import broadcast_sos_alert

@app.route('/api/sos-alert', methods=['POST'])
def handle_sos_alert():
    alert = request.get_json()
    
    # Save to database
    result = db.sos_alerts.insert_one(alert)
    alert['_id'] = str(result.inserted_id)
    
    # Real-time broadcast
    broadcast_sos_alert(alert)
    
    # Send SMS/email (async)
    send_emergency_notifications(alert)
    
    return jsonify({'success': True, 'alert_id': alert['_id']})
```

**Frontend automatically:**
1. Receives WebSocket event
2. Plays alert sound
3. Shows toast notification
4. Updates badge count
5. Refreshes SOS alerts list
6. Adds map marker
7. Animates UI elements

---

**Status:** ✅ Fully implemented and ready to use  
**Fallback:** ✅ Automatic polling if WebSocket unavailable  
**Browser Support:** Chrome, Firefox, Safari, Edge (all modern browsers)

For questions or issues, check browser console logs and server logs.
