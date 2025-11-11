# 🔧 Admin Dashboard Enhancement Implementation Plan

## Overview
Complete implementation guide for all 9 enhancement categories requested for the Admin Dashboard.

---

## 1. Data Visibility & Actionability

### A. Auto-Refresh with Loading Spinners

**Implementation:**
```javascript
// Add to admin_dashboard.html <script> section

let autoRefreshInterval = null;
let isRefreshing = false;

function showLoadingSpinner(tableId) {
    const table = document.getElementById(tableId);
    if (table) {
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 40px;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p style="margin-top: 15px; color: #6c757d;">Loading data...</p>
                </td>
            </tr>
        `;
    }
}

function showErrorMessage(tableId, errorMsg) {
    const table = document.getElementById(tableId);
    if (table) {
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 40px;">
                    <div style="color: #dc3545;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3em; margin-bottom: 15px;"></i>
                        <h4>Failed to Load Data</h4>
                        <p>${errorMsg}</p>
                        <button onclick="retryDataLoad('${tableId}')" class="btn btn-primary mt-3">
                            <i class="fas fa-sync-alt"></i> Retry
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }
}

function enableAutoRefresh(intervalMs = 30000) {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
    
    autoRefreshInterval = setInterval(() => {
        if (!isRefreshing) {
            refreshAllData();
        }
    }, intervalMs);
    
    showNotification('Auto-refresh enabled (30s intervals)', 'success');
}

function disableAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        showNotification('Auto-refresh disabled', 'info');
    }
}

async function refreshAllData() {
    isRefreshing = true;
    try {
        await Promise.all([
            loadTouristData(),
            loadPanicAlerts(),
            loadIncidentReports(),
            loadSystemStats()
        ]);
        updateLastRefreshTime();
    } catch (error) {
        console.error('Refresh error:', error);
    } finally {
        isRefreshing = false;
    }
}

function updateLastRefreshTime() {
    const timeElement = document.getElementById('lastRefreshTime');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = `Last updated: ${now.toLocaleTimeString()}`;
    }
}
```

### B. Fix Tourist Name Display in Panic Alerts

**Backend Fix (backend/app.py):**
```python
@app.route('/api/admin/panic-alerts', methods=['GET'])
def get_panic_alerts():
    try:
        if not mongo_enabled():
            return jsonify({'success': False, 'alerts': []}), 200
        
        init_mongo()
        from mongo_db import mongo_db
        
        # Get panic alerts with tourist info
        alerts_collection = mongo_db['panic_alerts']
        tourists_collection = mongo_db['_enhanced_tourists']
        
        alerts = list(alerts_collection.find().sort('timestamp', -1).limit(50))
        
        # Enrich alerts with tourist data
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
            tourist_id = alert.get('tourist_id')
            
            if tourist_id:
                tourist = tourists_collection.find_one({'tourist_id': tourist_id})
                if tourist:
                    alert['tourist_name'] = tourist.get('username', 'Unknown')
                    alert['tourist_email'] = tourist.get('email', '')
                    alert['tourist_phone'] = tourist.get('phone', '')
                else:
                    alert['tourist_name'] = f'Tourist #{tourist_id}'
            else:
                alert['tourist_name'] = 'Anonymous'
        
        return jsonify({'success': True, 'alerts': alerts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Frontend Update:**
```javascript
function loadPanicAlerts() {
    showLoadingSpinner('panicAlertsTable');
    
    fetch('/api/admin/panic-alerts')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPanicAlerts(data.alerts);
            } else {
                showErrorMessage('panicAlertsTable', data.error || 'Unknown error');
            }
        })
        .catch(error => {
            showErrorMessage('panicAlertsTable', `Network error: ${error.message}`);
        });
}

function displayPanicAlerts(alerts) {
    const tbody = document.querySelector('#panicAlertsTable tbody');
    
    if (alerts.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #6c757d;">
                    <i class="fas fa-check-circle" style="font-size: 3em; color: #28a745; margin-bottom: 15px;"></i>
                    <h4>No Active Panic Alerts</h4>
                    <p>All tourists are safe. System monitoring active.</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = alerts.map(alert => `
        <tr onclick="viewAlertDetails('${alert._id}')" style="cursor: pointer;">
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="/static/default-avatar.png" 
                         style="width: 40px; height: 40px; border-radius: 50%;" 
                         alt="Tourist">
                    <div>
                        <strong>${alert.tourist_name || 'Unknown'}</strong>
                        <br>
                        <small style="color: #6c757d;">${alert.tourist_id || 'N/A'}</small>
                    </div>
                </div>
            </td>
            <td>${alert.alert_type || 'Panic Alert'}</td>
            <td>
                <span class="badge bg-danger">
                    <i class="fas fa-map-marker-alt"></i>
                    ${alert.latitude?.toFixed(4) || 'N/A'}, ${alert.longitude?.toFixed(4) || 'N/A'}
                </span>
            </td>
            <td>${new Date(alert.timestamp).toLocaleString()}</td>
            <td>
                <span class="badge ${alert.status === 'resolved' ? 'bg-success' : 'bg-warning'}">
                    ${alert.status || 'Pending'}
                </span>
            </td>
            <td>
                <button onclick="event.stopPropagation(); resolveAlert('${alert._id}')" 
                        class="btn btn-sm btn-success">
                    <i class="fas fa-check"></i> Resolve
                </button>
                <button onclick="event.stopPropagation(); contactTourist('${alert.tourist_id}')" 
                        class="btn btn-sm btn-primary">
                    <i class="fas fa-phone"></i> Contact
                </button>
            </td>
        </tr>
    `).join('');
}
```

---

## 2. Analytics & Summaries

### A. Real-Time Summary Widgets

**Add to HTML (after existing stat cards):**
```html
<!-- Enhanced Summary Dashboard -->
<div class="row mb-4">
    <div class="col-md-12">
        <h3 class="mb-3">
            <i class="fas fa-chart-line"></i> Real-Time Analytics
            <small class="text-muted" id="lastRefreshTime">Last updated: Never</small>
        </h3>
    </div>
</div>

<div class="dashboard-grid">
    <!-- Active Alerts Widget -->
    <div class="stat-card alerts clickable" onclick="showSection('alerts')">
        <div class="stat-header">
            <div class="stat-icon" style="color: #dc3545;">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <span class="trend-indicator" id="alertsTrend">
                <i class="fas fa-arrow-up"></i> +3
            </span>
        </div>
        <div class="stat-number" id="activeAlertsCount">0</div>
        <div class="stat-label">Active Alerts</div>
        <div class="stat-footer">
            <small>Last hour: <span id="alertsLastHour">0</span></small>
        </div>
    </div>

    <!-- Resolved Incidents Widget -->
    <div class="stat-card blockchain clickable" onclick="showSection('incidents')">
        <div class="stat-header">
            <div class="stat-icon" style="color: #28a745;">
                <i class="fas fa-check-circle"></i>
            </div>
            <span class="trend-indicator positive">
                <i class="fas fa-arrow-up"></i> +12
            </span>
        </div>
        <div class="stat-number" id="resolvedIncidentsCount">0</div>
        <div class="stat-label">Resolved Today</div>
        <div class="stat-footer">
            <small>Resolution Rate: <span id="resolutionRate">0%</span></small>
        </div>
    </div>

    <!-- Tourists Onboard Widget -->
    <div class="stat-card tourists clickable" onclick="showSection('tourists')">
        <div class="stat-header">
            <div class="stat-icon" style="color: #007bff;">
                <i class="fas fa-users"></i>
            </div>
            <span class="trend-indicator positive">
                <i class="fas fa-arrow-up"></i> +5
            </span>
        </div>
        <div class="stat-number" id="touristsOnboardCount">0</div>
        <div class="stat-label">Tourists Onboard</div>
        <div class="stat-footer">
            <small>New today: <span id="newTouristsToday">0</span></small>
        </div>
    </div>

    <!-- Geofence Violations Widget -->
    <div class="stat-card files clickable" onclick="showSection('geofence')">
        <div class="stat-header">
            <div class="stat-icon" style="color: #ffc107;">
                <i class="fas fa-map-marked-alt"></i>
            </div>
            <span class="trend-indicator">
                <i class="fas fa-minus"></i> 0
            </span>
        </div>
        <div class="stat-number" id="geofenceViolationsCount">0</div>
        <div class="stat-label">Geofence Violations</div>
        <div class="stat-footer">
            <small>Last 24h: <span id="violationsLast24h">0</span></small>
        </div>
    </div>

    <!-- System Health Widget -->
    <div class="stat-card" style="border-left-color: #17a2b8;" onclick="showSystemHealthModal()">
        <div class="stat-header">
            <div class="stat-icon" style="color: #17a2b8;">
                <i class="fas fa-heartbeat"></i>
            </div>
            <span class="status-indicator" id="systemHealthStatus">
                <i class="fas fa-circle" style="color: #28a745;"></i> Healthy
            </span>
        </div>
        <div class="stat-number" id="systemUptime">99.9%</div>
        <div class="stat-label">System Uptime</div>
        <div class="stat-footer">
            <small>Response Time: <span id="avgResponseTime">120ms</span></small>
        </div>
    </div>

    <!-- Average Response Time Widget -->
    <div class="stat-card" style="border-left-color: #6610f2;">
        <div class="stat-header">
            <div class="stat-icon" style="color: #6610f2;">
                <i class="fas fa-clock"></i>
            </div>
            <span class="trend-indicator positive">
                <i class="fas fa-arrow-down"></i> -15s
            </span>
        </div>
        <div class="stat-number" id="avgIncidentResponseTime">4.2m</div>
        <div class="stat-label">Avg Response Time</div>
        <div class="stat-footer">
            <small>Target: &lt;5 minutes</small>
        </div>
    </div>
</div>

<style>
.clickable {
    cursor: pointer;
    transition: all 0.3s ease;
}

.clickable:hover {
    transform: scale(1.05);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
}

.trend-indicator {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
}

.trend-indicator.positive {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
}

.stat-footer {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e9ecef;
    color: #6c757d;
    font-size: 0.9em;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9em;
}
</style>
```

### B. Trend Charts with Chart.js

**Add Chart.js CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**Add Charts Section:**
```html
<!-- Trend Charts Section -->
<div class="row mb-4">
    <div class="col-md-6">
        <div class="chart-card">
            <h4><i class="fas fa-chart-area"></i> Emergency Calls Trend (7 Days)</h4>
            <canvas id="emergencyCallsChart"></canvas>
        </div>
    </div>
    <div class="col-md-6">
        <div class="chart-card">
            <h4><i class="fas fa-chart-bar"></i> Geofence Violations (7 Days)</h4>
            <canvas id="geofenceViolationsChart"></canvas>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-6">
        <div class="chart-card">
            <h4><i class="fas fa-chart-line"></i> Average Response Time (7 Days)</h4>
            <canvas id="responseTimeChart"></canvas>
        </div>
    </div>
    <div class="col-md-6">
        <div class="chart-card">
            <h4><i class="fas fa-chart-pie"></i> Incident Resolution Rate</h4>
            <canvas id="resolutionRateChart"></canvas>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-12">
        <div class="chart-card">
            <h4><i class="fas fa-user-plus"></i> Tourist Registration Growth (30 Days)</h4>
            <canvas id="registrationGrowthChart"></canvas>
        </div>
    </div>
</div>

<style>
.chart-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    margin-bottom: 25px;
}

.chart-card h4 {
    margin-bottom: 20px;
    color: #495057;
    display: flex;
    align-items: center;
    gap: 10px;
}

.chart-card canvas {
    max-height: 300px;
}
</style>

<script>
// Initialize Charts
let charts = {};

function initializeCharts() {
    // Emergency Calls Trend
    const ctx1 = document.getElementById('emergencyCallsChart');
    if (ctx1) {
        charts.emergencyCalls = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: getLast7Days(),
                datasets: [{
                    label: 'Emergency Calls',
                    data: [12, 19, 15, 25, 22, 30, 28],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Geofence Violations
    const ctx2 = document.getElementById('geofenceViolationsChart');
    if (ctx2) {
        charts.geofenceViolations = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: getLast7Days(),
                datasets: [{
                    label: 'Violations',
                    data: [5, 8, 3, 12, 7, 15, 10],
                    backgroundColor: '#ffc107',
                    borderColor: '#ff9800',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Response Time
    const ctx3 = document.getElementById('responseTimeChart');
    if (ctx3) {
        charts.responseTime = new Chart(ctx3, {
            type: 'line',
            data: {
                labels: getLast7Days(),
                datasets: [{
                    label: 'Avg Response (minutes)',
                    data: [5.2, 4.8, 5.5, 4.2, 3.9, 4.5, 4.2],
                    borderColor: '#6610f2',
                    backgroundColor: 'rgba(102, 16, 242, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Resolution Rate (Pie)
    const ctx4 = document.getElementById('resolutionRateChart');
    if (ctx4) {
        charts.resolutionRate = new Chart(ctx4, {
            type: 'doughnut',
            data: {
                labels: ['Resolved', 'Pending', 'Escalated'],
                datasets: [{
                    data: [85, 10, 5],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Registration Growth
    const ctx5 = document.getElementById('registrationGrowthChart');
    if (ctx5) {
        charts.registrationGrowth = new Chart(ctx5, {
            type: 'line',
            data: {
                labels: getLast30Days(),
                datasets: [{
                    label: 'New Registrations',
                    data: generateRandomData(30, 5, 25),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

function getLast7Days() {
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return days;
}

function getLast30Days() {
    const days = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return days;
}

function generateRandomData(count, min, max) {
    return Array.from({ length: count }, () => 
        Math.floor(Math.random() * (max - min + 1)) + min
    );
}

// Update charts with real data
function updateChartData(chartName, newData) {
    if (charts[chartName]) {
        charts[chartName].data.datasets[0].data = newData;
        charts[chartName].update();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeCharts, 1000);
});
</script>
```

---

## 3. AI Monitoring & Alert System

### A. Advanced Alert Filtering

**Add Filter Controls:**
```html
<!-- Alert Filters Section -->
<div class="filter-section mb-4">
    <div class="row">
        <div class="col-md-3">
            <label>Location</label>
            <select id="filterLocation" class="form-control" onchange="applyFilters()">
                <option value="">All Locations</option>
                <option value="delhi">Delhi</option>
                <option value="mumbai">Mumbai</option>
                <option value="bangalore">Bangalore</option>
            </select>
        </div>
        <div class="col-md-3">
            <label>Incident Type</label>
            <select id="filterIncidentType" class="form-control" onchange="applyFilters()">
                <option value="">All Types</option>
                <option value="panic">Panic Alert</option>
                <option value="geofence">Geofence Violation</option>
                <option value="medical">Medical Emergency</option>
                <option value="safety">Safety Concern</option>
            </select>
        </div>
        <div class="col-md-3">
            <label>Priority</label>
            <select id="filterPriority" class="form-control" onchange="applyFilters()">
                <option value="">All Priorities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
        </div>
        <div class="col-md-3">
            <label>Tourist ID</label>
            <input type="text" id="filterTouristId" class="form-control" 
                   placeholder="Search by ID" onkeyup="applyFilters()">
        </div>
    </div>
    <div class="row mt-3">
        <div class="col-md-12">
            <button onclick="clearFilters()" class="btn btn-secondary">
                <i class="fas fa-times"></i> Clear Filters
            </button>
            <button onclick="selectAllAlerts()" class="btn btn-primary">
                <i class="fas fa-check-square"></i> Select All
            </button>
            <button onclick="deselectAllAlerts()" class="btn btn-outline-primary">
                <i class="far fa-square"></i> Deselect All
            </button>
            <button onclick="bulkResolveAlerts()" class="btn btn-success">
                <i class="fas fa-check-double"></i> Resolve Selected
            </button>
            <button onclick="bulkExportAlerts()" class="btn btn-info">
                <i class="fas fa-download"></i> Export Selected
            </button>
        </div>
    </div>
</div>

<style>
.filter-section {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.filter-section label {
    font-weight: 600;
    color: #495057;
    margin-bottom: 8px;
    display: block;
}

.filter-section .form-control {
    border-radius: 8px;
    border: 1px solid #dee2e6;
    padding: 10px 15px;
}

.filter-section .form-control:focus {
    border-color: #6f42c1;
    box-shadow: 0 0 0 0.2rem rgba(111, 66, 193, 0.25);
}
</style>

<script>
let selectedAlerts = new Set();
let allAlerts = [];

function applyFilters() {
    const location = document.getElementById('filterLocation').value;
    const incidentType = document.getElementById('filterIncidentType').value;
    const priority = document.getElementById('filterPriority').value;
    const touristId = document.getElementById('filterTouristId').value.toLowerCase();
    
    let filtered = allAlerts.filter(alert => {
        if (location && alert.location !== location) return false;
        if (incidentType && alert.type !== incidentType) return false;
        if (priority && alert.priority !== priority) return false;
        if (touristId && !alert.tourist_id.toLowerCase().includes(touristId)) return false;
        return true;
    });
    
    displayPanicAlerts(filtered);
    updateFilterStats(filtered.length, allAlerts.length);
}

function clearFilters() {
    document.getElementById('filterLocation').value = '';
    document.getElementById('filterIncidentType').value = '';
    document.getElementById('filterPriority').value = '';
    document.getElementById('filterTouristId').value = '';
    applyFilters();
}

function selectAllAlerts() {
    document.querySelectorAll('.alert-checkbox').forEach(cb => {
        cb.checked = true;
        selectedAlerts.add(cb.value);
    });
    updateSelectionCount();
}

function deselectAllAlerts() {
    document.querySelectorAll('.alert-checkbox').forEach(cb => {
        cb.checked = false;
    });
    selectedAlerts.clear();
    updateSelectionCount();
}

function bulkResolveAlerts() {
    if (selectedAlerts.size === 0) {
        showNotification('Please select alerts to resolve', 'warning');
        return;
    }
    
    if (confirm(`Resolve ${selectedAlerts.size} selected alerts?`)) {
        const alertIds = Array.from(selectedAlerts);
        
        fetch('/api/admin/alerts/bulk-resolve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ alert_ids: alertIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`${alertIds.length} alerts resolved successfully`, 'success');
                selectedAlerts.clear();
                refreshAllData();
            } else {
                showNotification('Failed to resolve alerts', 'error');
            }
        })
        .catch(error => {
            showNotification('Network error', 'error');
        });
    }
}

function updateSelectionCount() {
    const count = selectedAlerts.size;
    const countElement = document.getElementById('selectionCount');
    if (countElement) {
        countElement.textContent = count > 0 ? `(${count} selected)` : '';
    }
}

function updateFilterStats(filtered, total) {
    const statsElement = document.getElementById('filterStats');
    if (statsElement) {
        statsElement.textContent = `Showing ${filtered} of ${total} alerts`;
    }
}
</script>
```

### B. Priority Notifications with Color Coding

**Add Priority Styles:**
```html
<style>
.priority-badge {
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.85em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.priority-critical {
    background: #dc3545;
    color: white;
    animation: pulse-critical 2s infinite;
}

.priority-high {
    background: #fd7e14;
    color: white;
}

.priority-medium {
    background: #ffc107;
    color: #000;
}

.priority-low {
    background: #28a745;
    color: white;
}

@keyframes pulse-critical {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.alert-row-critical {
    background: rgba(220, 53, 69, 0.05);
    border-left: 4px solid #dc3545;
}

.alert-row-high {
    background: rgba(253, 126, 20, 0.05);
    border-left: 4px solid #fd7e14;
}
</style>

<script>
// Push Notification Support
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showNotification('Push notifications enabled', 'success');
            }
        });
    }
}

function sendPushNotification(title, message, priority = 'medium') {
    if ('Notification' in window && Notification.permission === 'granted') {
        const icon = priority === 'critical' ? '/static/icon-critical.png' : '/static/icon-alert.png';
        
        new Notification(title, {
            body: message,
            icon: icon,
            badge: '/static/badge.png',
            tag: `alert-${Date.now()}`,
            requireInteraction: priority === 'critical'
        });
    }
}

// Monitor for new critical alerts
function monitorCriticalAlerts() {
    setInterval(() => {
        fetch('/api/admin/alerts/critical')
            .then(response => response.json())
            .then(data => {
                if (data.new_alerts && data.new_alerts.length > 0) {
                    data.new_alerts.forEach(alert => {
                        sendPushNotification(
                            `🚨 Critical Alert!`,
                            `${alert.tourist_name} needs immediate assistance`,
                            'critical'
                        );
                        playAlertSound();
                    });
                }
            });
    }, 10000); // Check every 10 seconds
}

function playAlertSound() {
    const audio = new Audio('/static/alert-sound.mp3');
    audio.play().catch(e => console.log('Audio play failed:', e));
}
</script>
```

---

## 4. Interactive Maps

### A. Live Tourist Tracking with Google Maps

**Add Google Maps API:**
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization"></script>

<!-- Map Section -->
<div class="row mb-4">
    <div class="col-md-12">
        <div class="map-card">
            <div class="map-header">
                <h4><i class="fas fa-map-marked-alt"></i> Live Tourist Tracking</h4>
                <div class="map-controls">
                    <button onclick="toggleHeatmap()" class="btn btn-sm btn-info">
                        <i class="fas fa-fire"></i> Heatmap
                    </button>
                    <button onclick="toggleClusters()" class="btn btn-sm btn-primary">
                        <i class="fas fa-layer-group"></i> Clusters
                    </button>
                    <button onclick="refreshMapData()" class="btn btn-sm btn-success">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
            </div>
            <div id="touristMap" style="height: 600px; border-radius: 10px;"></div>
            <div class="map-legend">
                <span><i class="fas fa-circle" style="color: #28a745;"></i> Safe</span>
                <span><i class="fas fa-circle" style="color: #ffc107;"></i> Caution</span>
                <span><i class="fas fa-circle" style="color: #dc3545;"></i> Alert</span>
            </div>
        </div>
    </div>
</div>

<style>
.map-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.map-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.map-controls {
    display: flex;
    gap: 10px;
}

.map-legend {
    display: flex;
    gap: 20px;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #dee2e6;
}

.map-legend span {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
}
</style>

<script>
let touristMap;
let touristMarkers = {};
let heatmapLayer;
let markerCluster;
let showHeatmap = false;
let showClusters = false;

function initializeTouristMap() {
    touristMap = new google.maps.Map(document.getElementById('touristMap'), {
        center: { lat: 28.6139, lng: 77.2090 }, // Delhi
        zoom: 12,
        styles: [
            {
                featureType: 'poi',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
    
    loadTouristLocations();
}

function loadTouristLocations() {
    fetch('/api/admin/tourist-locations')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTouristMarkers(data.tourists);
                if (showHeatmap) updateHeatmap(data.tourists);
            }
        });
}

function updateTouristMarkers(tourists) {
    // Clear existing markers
    Object.values(touristMarkers).forEach(marker => marker.setMap(null));
    touristMarkers = {};
    
    tourists.forEach(tourist => {
        const position = { lat: tourist.latitude, lng: tourist.longitude };
        const status = tourist.status || 'safe';
        
        const marker = new google.maps.Marker({
            position: position,
            map: touristMap,
            title: tourist.name,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: getStatusColor(status),
                fillOpacity: 0.8,
                strokeColor: '#fff',
                strokeWeight: 2
            }
        });
        
        // Info window
        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="padding: 10px;">
                    <h5>${tourist.name}</h5>
                    <p><strong>ID:</strong> ${tourist.tourist_id}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${status === 'safe' ? 'success' : 'danger'}">${status}</span></p>
                    <p><strong>Last Update:</strong> ${new Date(tourist.last_update).toLocaleString()}</p>
                    <div style="margin-top: 10px;">
                        <button onclick="viewTouristProfile('${tourist.tourist_id}')" class="btn btn-sm btn-primary">
                            View Profile
                        </button>
                        <button onclick="contactTourist('${tourist.tourist_id}')" class="btn btn-sm btn-success">
                            Contact
                        </button>
                    </div>
                </div>
            `
        });
        
        marker.addListener('click', () => {
            infoWindow.open(touristMap, marker);
        });
        
        touristMarkers[tourist.tourist_id] = marker;
    });
}

function getStatusColor(status) {
    switch (status) {
        case 'safe': return '#28a745';
        case 'caution': return '#ffc107';
        case 'alert': return '#dc3545';
        default: return '#007bff';
    }
}

function toggleHeatmap() {
    showHeatmap = !showHeatmap;
    
    if (showHeatmap) {
        fetch('/api/admin/tourist-locations')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const heatmapData = data.tourists.map(t => ({
                        location: new google.maps.LatLng(t.latitude, t.longitude),
                        weight: t.status === 'alert' ? 3 : 1
                    }));
                    
                    heatmapLayer = new google.maps.visualization.HeatmapLayer({
                        data: heatmapData,
                        map: touristMap
                    });
                }
            });
    } else {
        if (heatmapLayer) heatmapLayer.setMap(null);
    }
}

function refreshMapData() {
    loadTouristLocations();
    showNotification('Map data refreshed', 'success');
}

// Initialize map on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('touristMap')) {
        initializeTouristMap();
        setInterval(loadTouristLocations, 30000); // Refresh every 30s
    }
});
</script>
```

---

## 5. Post-Incident Reporting

### A. Export & Filter Reports

**Add Export Section:**
```html
<!-- Report Export Section -->
<div class="export-section mb-4">
    <div class="row">
        <div class="col-md-12">
            <h4><i class="fas fa-file-export"></i> Export Incident Reports</h4>
        </div>
    </div>
    <div class="row mt-3">
        <div class="col-md-3">
            <label>Date Range</label>
            <input type="date" id="exportStartDate" class="form-control">
        </div>
        <div class="col-md-3">
            <label>&nbsp;</label>
            <input type="date" id="exportEndDate" class="form-control">
        </div>
        <div class="col-md-3">
            <label>Status</label>
            <select id="exportStatus" class="form-control">
                <option value="">All Statuses</option>
                <option value="resolved">Resolved</option>
                <option value="pending">Pending</option>
                <option value="escalated">Escalated</option>
            </select>
        </div>
        <div class="col-md-3">
            <label>Format</label>
            <div class="btn-group w-100" role="group">
                <button onclick="exportReports('pdf')" class="btn btn-danger">
                    <i class="fas fa-file-pdf"></i> PDF
                </button>
                <button onclick="exportReports('csv')" class="btn btn-success">
                    <i class="fas fa-file-csv"></i> CSV
                </button>
                <button onclick="exportReports('excel')" class="btn btn-primary">
                    <i class="fas fa-file-excel"></i> Excel
                </button>
            </div>
        </div>
    </div>
</div>

<script>
function exportReports(format) {
    const startDate = document.getElementById('exportStartDate').value;
    const endDate = document.getElementById('exportEndDate').value;
    const status = document.getElementById('exportStatus').value;
    
    if (!startDate || !endDate) {
        showNotification('Please select date range', 'warning');
        return;
    }
    
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        status: status,
        format: format
    });
    
    showNotification(`Generating ${format.toUpperCase()} report...`, 'info');
    
    window.open(`/api/admin/reports/export?${params.toString()}`, '_blank');
}
</script>
```

---

This is Part 1 of the implementation. Would you like me to continue with:
- Part 2: System Health & Logging
- Part 3: Usability Enhancements  
- Part 4: Backend API implementations

Or would you prefer I implement these features directly into the admin dashboard HTML file?
