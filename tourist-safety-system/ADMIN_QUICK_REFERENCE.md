# 🎯 Admin Dashboard - Quick Reference Card

## 🚀 Getting Started

### Access Dashboard
```
URL: http://your-server:5000/admin
Login: Use admin credentials
```

### Connection Status
Look for the **Live** badge (top-right corner):
- 🟢 **Live** = Real-time updates active (WebSocket)
- ⚪ **Offline** = Using 30-second refresh (Polling)

---

## 🚨 SOS Emergency Response

### Quick Actions
1. **View Alert** - Click SOS card to see details
2. **Respond** - Click "Respond" → Send template message
3. **Resolve** - Click "Resolve" → Mark as handled
4. **Create Incident** - Click "Create Incident" → Generate formal report

### Bulk Actions (NEW!)
1. Check boxes next to multiple alerts
2. Bulk action bar appears automatically
3. Click "Bulk Respond" or "Bulk Resolve"
4. Confirm action

### Keyboard Shortcuts
- `Ctrl + R` - Refresh SOS alerts
- `Esc` - Close modal dialogs
- `Space` - Toggle checkbox (when focused)

---

## 🤖 AI Monitoring

### Filter Alerts (NEW!)
**Priority Filter:** Critical / High / Medium / Low  
**Risk Filter:** High / Medium / Low  
**Time Filter:** 24h / 48h / Week / Month  

**How to Use:**
1. Select filters from dropdowns
2. Results update automatically
3. Click "Export" to download filtered CSV

### Understanding Alerts
- **Critical (Red):** Immediate action required
- **High (Orange):** Urgent attention needed
- **Medium (Yellow):** Monitor closely
- **Low (Blue):** Informational

---

## 📍 Tourist Location Map

### Map Controls
- **Zoom:** Mouse wheel or `+/-` buttons
- **Pan:** Click and drag
- **Marker Click:** View tourist/SOS details
- **Layer Toggle:** Show/hide tourist markers, SOS alerts, geofences

### Map Features
- 🔵 **Blue Markers** - Tourist locations
- 🔴 **Red Pulsing Markers** - Active SOS alerts
- 🟦 **Blue Polygons** - Geofence zones (restricted areas)

---

## 📊 Data Export

### Available Exports (NEW!)
| Section | Export Button Location | Filename Format |
|---------|------------------------|-----------------|
| Tourists | Top-right of tourist tab | `Tourists_YYYY-MM-DD.csv` |
| SOS Alerts | Top of SOS section | `SOS_Alerts_YYYY-MM-DD.csv` |
| Incident Reports | Post-Incident section | `Incident_Reports_YYYY-MM-DD.csv` |
| AI Alerts | AI Monitoring section | `AI_Alerts_YYYY-MM-DD_TimeRange.csv` |

### How to Export
1. (Optional) Apply filters
2. Click "Export" button
3. CSV downloads automatically
4. Open with Excel, Google Sheets, etc.

---

## 🔔 Real-Time Notifications

### Notification Types
- 🚨 **SOS Alert** - Red toast, alert sound
- 🤖 **AI Alert** - Yellow/orange toast
- 📋 **New Incident** - Blue toast
- 📍 **Tourist Update** - Silent map update
- ℹ️ **System Message** - Gray toast

### Sound Alerts
- **SOS:** Emergency siren (critical)
- **Success:** Chime (action completed)
- **Warning:** Beep (attention needed)

---

## 🎨 Dashboard Sections

### 1. SOS Emergency Alerts
- View active SOS alerts
- Respond to emergencies
- Bulk actions
- Export data

### 2. AI Monitoring System
- Real-time risk analysis
- Filter by priority/risk/time
- Statistics overview
- Export alerts

### 3. Post-Incident Reports
- View incident history
- Generate new reports
- Search and filter
- Export reports

### 4. Tourist Management
- Registered tourists list
- Location tracking
- Emergency contacts
- Export tourist data

### 5. Interactive Map
- Live location visualization
- SOS overlays
- Geofence zones
- Click for details

---

## 🔧 Common Tasks

### Task: Respond to SOS Alert
1. New SOS alert appears (red card)
2. Sound alert plays
3. Click "Respond" button
4. Select template or type custom message
5. Click "Send Response"
6. Alert marked as "Responded"

### Task: Create Incident from SOS
1. Find SOS alert card
2. Click red "Create Incident" button
3. Modal opens with pre-filled data
4. Select incident type (Medical, Security, etc.)
5. Add description
6. Choose severity level
7. Click "Submit Incident Report"
8. Incident created, SOS updated

### Task: Filter AI Alerts
1. Scroll to "AI Monitoring System"
2. Use dropdowns:
   - Priority: Select "Critical"
   - Risk: Select "High"
   - Time: Select "24h"
3. View filtered results (count shown)
4. Click "Export" to save filtered data

### Task: Export Tourist Data
1. Navigate to "Registered Tourists" tab
2. Click "Export" button (top-right)
3. Wait for CSV download
4. Open file with spreadsheet software

### Task: View Tourist on Map
1. Find tourist in table
2. Note location coordinates OR
3. Click tourist marker on map
4. Popup shows details

---

## ⚡ Performance Tips

### For Best Performance
- ✅ Use modern browser (Chrome, Firefox, Edge)
- ✅ Keep WebSocket connected (check "Live" badge)
- ✅ Apply filters before exporting large datasets
- ✅ Clear browser cache weekly
- ✅ Close unused tabs

### If Dashboard is Slow
1. Check "Live" badge - if offline, refresh page
2. Reduce time filter range (24h instead of Month)
3. Export data in smaller batches
4. Clear browser cache: `Ctrl + Shift + Delete`

---

## 🚑 Emergency Protocols

### Critical SOS Alert Received
1. **Immediate:** Check location on map
2. **Contact:** Call tourist via emergency contact
3. **Dispatch:** Contact local emergency services
4. **Respond:** Send reassurance message via dashboard
5. **Create Incident:** Click "Create Incident" button
6. **Monitor:** Watch for tourist updates
7. **Resolve:** Mark SOS as resolved when safe

### High-Risk AI Alert
1. **Review:** Read alert message and risk factors
2. **Verify:** Check tourist location on map
3. **Assess:** Determine if intervention needed
4. **Contact:** Reach out to tourist if necessary
5. **Acknowledge:** Click "Acknowledge" button
6. **Monitor:** Track situation development
7. **Resolve:** Click "Resolve" when addressed

---

## 🔒 Security Best Practices

### Do's ✅
- ✅ Log out when leaving workstation
- ✅ Use strong admin password
- ✅ Verify tourist identity before sharing data
- ✅ Export data only when necessary
- ✅ Keep browser updated
- ✅ Report suspicious activity

### Don'ts ❌
- ❌ Share admin credentials
- ❌ Leave dashboard open unattended
- ❌ Export sensitive data to public folders
- ❌ Ignore system messages
- ❌ Disable security warnings

---

## 🆘 Troubleshooting

### Problem: WebSocket Not Connected
**Symptom:** Badge shows "Offline"  
**Solution:**
1. Refresh browser page (`F5`)
2. Check internet connection
3. Contact IT if persists

### Problem: Export Not Working
**Symptom:** CSV doesn't download  
**Solution:**
1. Check browser pop-up blocker
2. Verify data exists (table not empty)
3. Try different browser

### Problem: Map Not Loading
**Symptom:** Gray box instead of map  
**Solution:**
1. Check internet connection (Leaflet uses CDN)
2. Refresh page
3. Disable browser extensions

### Problem: SOS Alert Not Appearing
**Symptom:** Tourist triggered SOS but not visible  
**Solution:**
1. Click "Refresh" button
2. Check filters (no filters hiding it)
3. Scroll down (might be below visible area)

---

## 📚 Help Resources

### Documentation
- **WebSocket Setup:** `WEBSOCKET_SETUP_GUIDE.md`
- **Complete Features:** `ADMIN_DASHBOARD_COMPLETION.md`
- **Sample Data:** `SAMPLE_DATA_GENERATOR.md`

### Browser Console (Advanced)
Press `F12` to open developer tools:
- **Console Tab:** View error messages
- **Network Tab:** Check API calls
- **Application Tab:** View cached data

### Test Commands (Console)
```javascript
// Check WebSocket status
wsClient.connected

// Manually refresh SOS alerts
refreshSOSAlerts()

// Export tourists
exportTourists()

// View tourist cache
touristCache
```

---

## 📊 Status Indicators

### Badge Colors
| Color | Meaning |
|-------|---------|
| 🔴 Red | Critical/Active SOS |
| 🟠 Orange | High priority/risk |
| 🟡 Yellow | Medium priority |
| 🔵 Blue | Low priority/info |
| 🟢 Green | Success/resolved |
| ⚪ Gray | Inactive/offline |

### Alert Priorities
- **Critical:** Life-threatening, respond within 1 minute
- **High:** Urgent, respond within 5 minutes
- **Medium:** Important, respond within 15 minutes
- **Low:** Informational, review when possible

---

## 🎓 Training Checklist

### New Admin Onboarding
- [ ] Access dashboard with credentials
- [ ] Understand WebSocket connection status
- [ ] Practice responding to SOS alert (test data)
- [ ] Create incident from SOS (test data)
- [ ] Filter AI alerts by priority
- [ ] Export tourists to CSV
- [ ] Locate tourist on map
- [ ] Use bulk SOS actions
- [ ] Review emergency protocols
- [ ] Know who to contact for IT support

---

## 🔢 Key Metrics to Monitor

### Daily
- Active SOS alerts count
- High-risk AI alerts (last 24h)
- Average SOS response time
- Tourist registration count

### Weekly
- Total incidents created
- SOS resolution rate
- AI alert accuracy (false positives)
- Peak activity times

### Monthly
- Export compliance reports
- Review emergency protocols
- Update tourist database
- Security audit

---

## 📞 Emergency Contacts

### Technical Support
- **IT Helpdesk:** [Insert number]
- **System Administrator:** [Insert email]
- **On-Call Engineer:** [Insert number]

### Emergency Services
- **Police:** [Insert local number]
- **Medical:** [Insert local number]
- **Fire:** [Insert local number]
- **Tourist Assistance:** [Insert number]

---

**Quick Tip:** Bookmark this page for instant access!

**Last Updated:** January 2024  
**Version:** 2.0.0
