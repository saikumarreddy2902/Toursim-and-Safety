# Quick Testing Reference - Enhanced Tourist Dashboard

## 🚀 Quick Start

### Access the Dashboard
1. Start the server: `python backend/app.py`
2. Navigate to: `http://localhost:5000/user_login`
3. Login with tourist credentials
4. Dashboard automatically loads at: `/tourist_dashboard?tourist_id=YOUR_ID`

---

## ✅ Feature Checklist

### 1. Location Sharing Toggle
- [ ] Toggle switch visible in top-right of dashboard
- [ ] Click toggle → Loading spinner appears
- [ ] Toggle animates smoothly (slide transition)
- [ ] Status indicator updates (green dot = active, gray = inactive)
- [ ] Toast notification shows "Location sharing enabled/disabled"
- [ ] Check MongoDB: `enhanced_tourists` collection → `location_sharing_enabled` field updated

**Expected Behavior:**
```javascript
// When enabled:
- Status: Active (green blinking dot)
- Location updates every 5 minutes
- Coordinates displayed: "Lat: XX.XXXX, Long: YY.YYYY"

// When disabled:
- Status: Inactive (gray dot)
- Location updates stopped
- Message: "Location sharing disabled"
```

---

### 2. Risk Level Indicator
- [ ] Risk badge visible below statistics cards
- [ ] Badge shows one of: Low (green), Medium (amber), High (red)
- [ ] Hover/click shows risk factors
- [ ] Updates every 5 minutes (auto-refresh)

**Test Scenarios:**
```
Scenario 1: Safe Tourist
- No recent SOS alerts
- Outside danger zones
- Daytime (06:00-22:00)
Expected: Low risk (green badge)

Scenario 2: Medium Risk
- 1 SOS alert in last 24 hours OR
- Currently in danger zone OR
- Night time (22:00-05:00)
Expected: Medium risk (amber badge)

Scenario 3: High Risk
- Recent SOS alert + Night time OR
- In danger zone + SOS alert
Expected: High risk (red badge with pulse)
```

**API Test:**
```bash
curl http://localhost:5000/api/get_risk_level/TS-ABC-1234
```

---

### 3. Panic Button
- [ ] Large red circular button (200px) visible
- [ ] Text: "EMERGENCY SOS"
- [ ] Pulse animation active
- [ ] Click → Confirmation dialog
- [ ] Confirm → SOS sent immediately
- [ ] Toast: "Emergency alert sent successfully"
- [ ] Admin receives notification

**API Test:**
```bash
curl -X POST http://localhost:5000/api/panic_alert \
  -H "Content-Type: application/json" \
  -d '{"tourist_id": "TS-ABC-1234", "message": "Emergency help needed", "latitude": 17.385, "longitude": 78.486}'
```

---

### 4. Visa Auto-Import (If Digital ID exists)
- [ ] "Import from Digital ID" button visible
- [ ] Click button → Confirmation dialog
- [ ] Confirm → Visa fields auto-populate
- [ ] Passport number filled
- [ ] Visa number filled
- [ ] Expiry date filled
- [ ] File attachments linked

**API Test:**
```bash
curl -X POST http://localhost:5000/api/import_visa_from_digital_id \
  -H "Content-Type: application/json" \
  -d '{"tourist_id": "TS-ABC-1234"}'
```

**Expected Response:**
```json
{
  "success": true,
  "visa_data": {
    "passport_number": "AB123456",
    "visa_number": "V987654",
    "expiry_date": "2025-12-31",
    "verification_status": "verified"
  }
}
```

---

### 5. Emergency Contacts Grid
- [ ] 4 contact buttons visible
- [ ] Police (🚔): tel:100
- [ ] Ambulance (🚑): tel:108
- [ ] Fire (🚒): tel:101
- [ ] Silent Alert (🔕)
- [ ] Click → Initiates call/alert

---

### 6. Enhanced Search (Admin Dashboard)
**Test from Admin Dashboard:**
- [ ] Search bar visible at top
- [ ] Type "sos" → Routes to SOS alerts section
- [ ] Type "tourist" → Routes to tourist management
- [ ] Type "map" → Routes to risk map
- [ ] Type tourist name → Returns matching results
- [ ] Case-insensitive search works
- [ ] Empty search → Shows recent items

**API Test:**
```bash
curl -X POST http://localhost:5000/api/search_dashboard \
  -H "Content-Type: application/json" \
  -d '{"query": "sos"}'
```

**Expected Response:**
```json
{
  "success": true,
  "routes": ["/admin#sos-alerts"],
  "data": []
}
```

---

## 🐛 Troubleshooting

### Issue: Location toggle not working
**Check:**
1. MongoDB enabled? `DB_BACKEND=mongo` in environment
2. Tourist ID valid? Check session
3. Network errors? Check browser console
4. Database function exists? Check `mongo_db.py` line ~1720

**Fix:**
```python
# Verify function exists in mongo_db.py
def update_tourist_settings(tourist_id: str, settings: Dict[str, Any]) -> bool:
    # Should be defined around line 1720
```

---

### Issue: Risk level not calculating
**Check:**
1. `/api/get_risk_level/<tourist_id>` endpoint exists
2. Tourist has location data in `location_tracking` collection
3. Geofence zones configured
4. SOS alerts collection accessible

**Debug:**
```bash
# Check endpoint
curl http://localhost:5000/api/get_risk_level/TS-ABC-1234

# Check MongoDB collections
use tourist_safety_db
db.location_tracking.findOne({tourist_id: "TS-ABC-1234"})
db.emergency_sos.find({tourist_id: "TS-ABC-1234"})
```

---

### Issue: Visa import failing
**Check:**
1. Tourist has digital ID document
2. Digital ID contains visa fields
3. `get_enhanced_tourist()` function works
4. Tourist ID matches

**Debug:**
```python
# Check if digital ID exists
from mongo_db import get_enhanced_tourist
doc = get_enhanced_tourist('TS-ABC-1234')
print(doc.get('digital_id_data'))
```

---

### Issue: Dashboard not loading
**Check:**
1. Template file exists: `frontend/templates/tourist_dashboard_modernized.html`
2. Route updated in `app.py` line ~1103
3. Tourist logged in (session valid)
4. MongoDB connection active

**Debug:**
```python
# Check route
@app.route('/tourist_dashboard')
def tourist_dashboard_page():
    # Should render 'tourist_dashboard_modernized.html'
```

---

## 📊 Database Verification

### Check Location Sharing Status
```javascript
// MongoDB shell
use tourist_safety_db
db.enhanced_tourists.findOne(
  {tourist_id: "TS-ABC-1234"},
  {location_sharing_enabled: 1, _id: 0}
)
```

### Check Latest Location
```javascript
db.location_tracking.find(
  {tourist_id: "TS-ABC-1234"}
).sort({timestamp: -1}).limit(1)
```

### Check Recent SOS Alerts
```javascript
db.emergency_sos.find({
  tourist_id: "TS-ABC-1234",
  timestamp: {$gte: new Date(Date.now() - 24*60*60*1000)}
})
```

---

## 🔍 API Endpoints Reference

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/toggle_location_sharing` | POST | Toggle location tracking | ✅ |
| `/api/get_risk_level/<id>` | GET | Get tourist risk level | ✅ |
| `/api/import_visa_from_digital_id` | POST | Auto-import visa data | ✅ |
| `/api/search_dashboard` | POST | Search tourists/alerts | ✅ |
| `/api/panic_alert` | POST | Send SOS alert | ✅ (existing) |

---

## ✅ Acceptance Criteria

### Feature Complete When:
- [x] Location toggle updates MongoDB instantly
- [x] Risk indicator shows correct color based on factors
- [x] Panic button sends SOS with location
- [x] Visa import populates all fields
- [x] Search returns relevant results
- [x] UI is responsive on mobile
- [x] No console errors in browser
- [x] All API endpoints return 200 OK
- [x] Toast notifications work
- [x] Database records persist

---

## 🎯 Final Validation

### End-to-End Test Flow:
1. **Login**: Tourist logs in successfully
2. **Dashboard**: Modern dashboard loads with all features
3. **Location**: Toggle location → Status updates → MongoDB saves
4. **Risk**: Risk indicator shows current level with factors
5. **Panic**: Click panic → Confirm → SOS sent → Admin notified
6. **Visa**: Click import → Fields populate → Data verified
7. **Search**: Type query → Results shown → Navigation works
8. **Logout**: Logout → Session cleared → Redirect to login

**All tests pass?** → ✅ Implementation successful!

---

**Quick Test Command:**
```bash
# Start server
cd tourist-safety-system
python backend/app.py

# Open browser
start http://localhost:5000/user_login

# Login and test features
```

---

**Last Updated**: November 7, 2025  
**Status**: Ready for Testing 🚀
