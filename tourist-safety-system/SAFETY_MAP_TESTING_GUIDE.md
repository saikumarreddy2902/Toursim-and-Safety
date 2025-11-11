# ✅ Safety Map Testing Guide

## 🚀 Quick Test Steps

### Prerequisites
- ✅ Server running: `http://127.0.0.1:5000`
- ✅ Logged in as tourist user
- ✅ Browser: Chrome, Firefox, Safari, or Edge
- ✅ Internet connection (for Leaflet.js CDN and map tiles)

---

## 📋 Test Checklist

### 1. Initial State Test
**What to check:**
- [ ] Safety Map widget visible below "Action Recommendations"
- [ ] Map is disabled by default (gray overlay)
- [ ] "Enable AI Tracking" button visible in header
- [ ] LIVE badge is hidden
- [ ] Statistics bar is hidden
- [ ] Quick action buttons are hidden
- [ ] Journey breadcrumb is hidden
- [ ] Map legend is hidden

**Expected appearance:**
```
🗺️ Safety Map            [Enable AI Tracking]
┌────────────────────────────────────────────┐
│                                            │
│         🗺️ Safety Map Disabled            │
│   Enable AI monitoring to activate         │
│   real-time location tracking              │
│                                            │
│            [🚀 Enable Now]                 │
│                                            │
└────────────────────────────────────────────┘
```

---

### 2. Enable Map Test
**Steps:**
1. Click "Enable AI Tracking" button in header
   OR
2. Click "🚀 Enable Now" button in center overlay

**What to check:**
- [ ] Gray overlay disappears
- [ ] Map becomes colorful and interactive
- [ ] LIVE badge appears with pulsing animation
- [ ] Button text changes to "Disable AI Tracking"
- [ ] Quick action buttons appear (top-right)
- [ ] Journey breadcrumb appears (top-left)
- [ ] Map legend appears (bottom-left)
- [ ] Statistics bar appears at bottom
- [ ] Achievement popup shows "Map Enabled!"
- [ ] Your location marker (📍) appears on map

**Console check:**
```javascript
// Open browser DevTools (F12)
// Console should show:
"Map initialized successfully"
// No errors
```

---

### 3. Map Interaction Test
**Steps:**
1. **Zoom Test:**
   - Use mouse wheel to zoom in/out
   - Click zoom buttons (bottom-right)
   - [ ] Map zooms smoothly

2. **Pan Test:**
   - Click and drag map
   - [ ] Map pans in all directions

3. **Marker Test:**
   - Click your location marker (📍)
   - [ ] Popup appears with location info
   - [ ] Popup shows current zone status
   - [ ] "Share This Location" button visible

4. **Zone Test:**
   - Click a green zone polygon
   - [ ] Popup shows "Safe Zone" info
   - Click a yellow zone polygon
   - [ ] Popup shows "Moderate Zone" info
   - Click a red zone polygon (if visible)
   - [ ] Popup shows "Restricted Zone" info

---

### 4. Quick Actions Test
**Test each button (top-right):**

**📍 Share Location:**
- Click button
- [ ] Function executes (check console)
- [ ] No JavaScript errors

**👥 Contacts:**
- Click button
- [ ] Opens emergency contacts section
- [ ] OR triggers contact modal

**🚨 Emergency:**
- Click button
- [ ] Emergency SOS function triggers
- [ ] Confirmation dialog appears
- [ ] (Don't confirm unless testing emergency flow)

**🏥 Services:**
- Click button
- [ ] 3 service markers appear on map:
  - 🏥 Hospital
  - 🚔 Police Station
  - 🏛️ Embassy
- Click each marker
- [ ] Popup shows service details
- [ ] "Get Directions" button visible
- [ ] Achievement popup shows "Services Found!"

---

### 5. Journey Tracking Test
**Steps:**
1. Enable map
2. Wait 10 seconds (auto-update interval)
3. [ ] Location updates (marker moves slightly)
4. [ ] Blue dashed polyline appears (journey path)
5. Check journey breadcrumb (top-left):
   - [ ] Shows "📍 Current" location
   - [ ] Shows timestamp (e.g., "Just now")
   - [ ] Shows coordinates
6. Wait another 10 seconds
7. [ ] New breadcrumb entry added
8. [ ] Older entries move down
9. [ ] Maximum 5 entries shown

**Note:** If browser geolocation permission denied:
- Map uses simulated location updates
- Movement will be small random changes

---

### 6. Statistics Bar Test
**Check bottom statistics bar:**

**Current Zone:**
- [ ] Shows zone name (e.g., "Safe ✅")
- [ ] Color matches zone type:
  - Green for Safe
  - Yellow for Moderate
  - Red for Restricted
- [ ] Updates when you move between zones

**Distance Today:**
- [ ] Shows "0 km" initially
- [ ] Increases as you move
- [ ] Format: "2.5 km" (decimal)

**Locations Tracked:**
- [ ] Shows count (e.g., "47")
- [ ] Increases with each update
- [ ] Maximum 50

**Safety Alerts:**
- [ ] Shows "0" initially
- [ ] Increases when entering restricted zone

---

### 7. Geofence Alert Test
**Steps:**
1. Enable map
2. Pan map to view red (restricted) zone
3. Drag your marker into the red zone
   OR
4. Wait for simulated location to enter red zone

**What to check:**
- [ ] Alert popup appears in center
- [ ] Shows "⚠️ Geofence Alert!" title
- [ ] Icon shakes continuously
- [ ] Shows zone name
- [ ] "Understood" button visible
- [ ] Auto-dismisses after 5 seconds
- [ ] Safety Alerts count increases by 1

**Visual check:**
```
┌─────────────────────────────┐
│          ⚠️ (shaking)       │
│      Geofence Alert!        │
│                             │
│ You've entered a restricted │
│ zone: Restricted Zone       │
│                             │
│       [Understood]          │
└─────────────────────────────┘
```

---

### 8. Map Legend Test
**Check legend (bottom-left):**
- [ ] Shows "🛡️ Safety Zones" title
- [ ] Green box + "Safe Zone" text
- [ ] Yellow box + "Moderate Zone" text
- [ ] Red box + "Restricted Zone" text
- [ ] Colors match map overlays

---

### 9. Disable Map Test
**Steps:**
1. Click "Disable AI Tracking" button

**What to check:**
- [ ] Map becomes grayscale
- [ ] Gray overlay reappears
- [ ] LIVE badge disappears
- [ ] Button text changes to "Enable AI Tracking"
- [ ] Quick action buttons disappear
- [ ] Journey breadcrumb disappears
- [ ] Map legend disappears
- [ ] Statistics bar disappears
- [ ] Auto-updates stop

---

### 10. Mobile Responsive Test
**Steps:**
1. Open browser DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select mobile device (e.g., iPhone 12)

**What to check:**
- [ ] Map height reduced to 350px
- [ ] Quick action buttons smaller
- [ ] Journey breadcrumb width reduced
- [ ] Legend font smaller
- [ ] Statistics bar shows 2x2 grid (2 columns)
- [ ] All elements still visible
- [ ] No horizontal scrolling
- [ ] Touch gestures work (pinch to zoom)

**Test on real devices (if available):**
- [ ] iPhone/iOS Safari
- [ ] Android Chrome
- [ ] Tablet (iPad/Android)

---

### 11. Browser Permission Test
**First-time users:**
1. Enable map
2. Browser shows: "Allow location access?"
3. **Test Case A:** Click "Allow"
   - [ ] Map uses real GPS location
   - [ ] Marker updates to actual position
   
4. **Test Case B:** Click "Block"
   - [ ] Map uses simulated location
   - [ ] Marker still updates (random movement)
   - [ ] No errors in console

---

### 12. Performance Test
**What to check:**
- [ ] Map loads within 2 seconds
- [ ] No lag when dragging map
- [ ] Smooth animations (60fps)
- [ ] Location updates don't freeze UI
- [ ] No memory leaks (check DevTools Memory tab)
- [ ] CPU usage reasonable (<50%)

**Browser Console Check:**
```javascript
// Check for errors
console.log("Should show no errors");

// Check map instance
console.log(safetyMapInstance); // Should be Leaflet map object

// Check location history
console.log(locationHistory); // Should be array of locations
```

---

### 13. Cross-Browser Test
**Test in each browser:**

**Chrome:**
- [ ] All features work
- [ ] No console errors
- [ ] Animations smooth

**Firefox:**
- [ ] All features work
- [ ] CSS Grid layout correct
- [ ] No console errors

**Safari:**
- [ ] All features work
- [ ] Smooth scrolling works
- [ ] No console errors

**Edge:**
- [ ] All features work
- [ ] Identical to Chrome
- [ ] No console errors

---

### 14. Integration Test
**Test sync with other features:**

**AI Monitoring:**
- [ ] Disable AI monitoring elsewhere
- [ ] Map should also disable
- [ ] Enable AI monitoring
- [ ] Map should enable

**Emergency SOS:**
- [ ] Trigger from map quick action
- [ ] Same as clicking main SOS button
- [ ] Location sent correctly

**Location Sharing:**
- [ ] Share from map
- [ ] Location matches map marker
- [ ] Contacts receive correct coordinates

---

## 🐛 Common Issues & Fixes

### Issue 1: Map Not Loading (Blank White)
**Symptoms:** Nothing appears, just white space

**Checks:**
1. Open DevTools Console
2. Look for errors like:
   - "Leaflet is not defined"
   - "Failed to load resource"

**Fixes:**
- Check internet connection
- Verify Leaflet CDN URL:
  ```html
  https://unpkg.com/leaflet@1.9.4/dist/leaflet.js
  https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
  ```
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

---

### Issue 2: Location Marker Not Appearing
**Symptoms:** Map loads but no 📍 marker

**Checks:**
```javascript
// Console:
console.log(userMarker); // Should be Leaflet Marker object
console.log(safetyMapInstance); // Should be Leaflet Map object
```

**Fixes:**
- Grant browser location permission
- Check if `initializeSafetyMap()` was called
- Verify no JavaScript errors before map init

---

### Issue 3: Zones Not Showing
**Symptoms:** No colored overlays

**Checks:**
- Zoom out to see wider area
- Check if zones exist for your region

**Fixes:**
```javascript
// Console:
console.log(sampleSafetyZones); // Should show array of 3 zones
console.log(safetyZones); // Should show array of Leaflet polygons
```

---

### Issue 4: Updates Not Working
**Symptoms:** Marker doesn't move, stats don't change

**Checks:**
```javascript
// Console:
console.log(isMapEnabled); // Should be true
console.log(mapUpdateInterval); // Should be interval ID (number)
```

**Fixes:**
- Disable and re-enable map
- Check browser console for errors
- Verify 10-second interval is running

---

### Issue 5: Mobile Layout Broken
**Symptoms:** Elements overlap, text tiny

**Checks:**
- Viewport meta tag in HTML:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ```

**Fixes:**
- Use DevTools responsive mode
- Test actual device
- Check media query breakpoint (768px)

---

## 📊 Expected Test Results

### ✅ Pass Criteria
- All 14 test categories complete
- No critical JavaScript errors
- Map initializes within 2 seconds
- All buttons functional
- Mobile responsive works
- At least 3 browsers tested

### ❌ Fail Criteria
- JavaScript errors preventing map load
- Map doesn't initialize
- Quick actions don't respond
- Mobile layout completely broken
- Crashes browser

---

## 🎯 Automated Testing (Future)

### Unit Tests (Future)
```javascript
// Example Jest tests
describe('Safety Map', () => {
  test('should initialize map on enable', () => {
    toggleSafetyMap();
    expect(safetyMapInstance).toBeDefined();
  });

  test('should add marker to map', () => {
    expect(userMarker).toBeDefined();
    expect(userMarker.getLatLng()).toEqual([28.6139, 77.2090]);
  });

  test('should draw 3 safety zones', () => {
    expect(safetyZones.length).toBe(3);
  });
});
```

---

## 📝 Test Report Template

```markdown
# Safety Map Test Report

**Tester:** [Your Name]
**Date:** [Test Date]
**Browser:** [Chrome/Firefox/Safari/Edge]
**Device:** [Desktop/Mobile/Tablet]
**OS:** [Windows/Mac/iOS/Android]

## Test Results

### Functional Tests
- [ ] Initial state: PASS/FAIL
- [ ] Enable map: PASS/FAIL
- [ ] Map interaction: PASS/FAIL
- [ ] Quick actions: PASS/FAIL
- [ ] Journey tracking: PASS/FAIL
- [ ] Statistics bar: PASS/FAIL
- [ ] Geofence alerts: PASS/FAIL
- [ ] Map legend: PASS/FAIL
- [ ] Disable map: PASS/FAIL

### Responsive Tests
- [ ] Desktop (>768px): PASS/FAIL
- [ ] Mobile (<768px): PASS/FAIL

### Performance
- Load time: [X] seconds
- CPU usage: [X]%
- Memory usage: [X] MB

### Issues Found
1. [Issue description]
2. [Issue description]

### Screenshots
[Attach screenshots]

### Notes
[Additional comments]

**Overall Status:** ✅ PASS / ❌ FAIL
```

---

## 🏁 Final Verification

**Before considering testing complete:**
1. [ ] All 14 test sections completed
2. [ ] Tested in at least 2 browsers
3. [ ] Tested on mobile (real device or emulator)
4. [ ] No critical errors in console
5. [ ] All features working as expected
6. [ ] Test report filled out
7. [ ] Screenshots/videos captured
8. [ ] Issues documented (if any)

---

**Test Status:** ⏳ Pending  
**Start Testing:** Visit `http://127.0.0.1:5000` → Login → Enable Safety Map  

---

*Complete this testing guide to ensure the Safety Map is production-ready! 🗺️✅*
