# 🚀 Part 3: JavaScript Functions for Modern Admin Dashboard

## Complete JavaScript Implementation

Add this complete JavaScript section before the closing `</body>` tag:

```javascript
<script>
/* ============================================
   GLOBAL STATE & CONFIGURATION
   ============================================ */

const AppState = {
    theme: localStorage.getItem('admin-theme') || 'light',
    language: localStorage.getItem('admin-language') || 'en',
    notifications: [],
    refreshInterval: 30000, // 30 seconds
    charts: {}
};

/* ============================================
   THEME TOGGLE (DARK MODE)
   ============================================ */

function initTheme() {
    document.documentElement.setAttribute('data-theme', AppState.theme);
    const themeIcon = document.querySelector('.theme-toggle i');
    if (themeIcon) {
        themeIcon.className = AppState.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function toggleTheme() {
    AppState.theme = AppState.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('admin-theme', AppState.theme);
    initTheme();
    
    showToast(
        'success',
        'Theme Changed',
        `Switched to ${AppState.theme} mode`
    );
}

/* ============================================
   TOAST NOTIFICATION SYSTEM
   ============================================ */

function showToast(type, title, message, duration = 5000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} animate__animated animate__fadeInRight`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${icons[type]}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="removeToast(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Play sound alert for critical notifications
    if (type === 'error' || type === 'warning') {
        playAlertSound(type);
    }
    
    // Auto remove after duration
    setTimeout(() => {
        toast.classList.add('animate__fadeOutRight');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function removeToast(button) {
    const toast = button.closest('.toast');
    toast.classList.add('animate__fadeOutRight');
    setTimeout(() => toast.remove(), 300);
}

/* ============================================
   SOUND ALERTS
   ============================================ */

const Sounds = {
    success: new Howl({ src: ['data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUI'], volume: 0.5 }),
    error: new Howl({ src: ['data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fZJmwrJBhNjRfodDbq2EcBj+a2/PDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUIGWi77eefTRALUKfj77dmHAU4ktfyzHksBSR2x/DdkEAKFF606eulVRQKRp/g8r5sIQUrgc7y2Yk1CBloue3nn00QDFCn4++3ZhwFOJLX8sx5LAUkdsfw3ZBAChRetOnrqFUUCkaf4PK+bCEFK4HO8tmJNQ'], volume: 0.7 }),
    warning: new Howl({ src: ['data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fZJmwrJBhNjRfodDbq2EcBj+a2/PDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUIGWi77eefTRAMUKfj8LZjHAY4kdfyzHksBSR3x/DdkEAKFF606eulVRQKRp/g8r5sIQUrgc7y2Yk1CBloue3nn00QDFCn4/C2YxwGOJHX8sx5LAUkd8fw3ZBAChRetOnrqFU'], volume: 0.6 })
};

function playAlertSound(type) {
    if (Sounds[type]) {
        try {
            Sounds[type].play();
        } catch (e) {
            console.log('Sound playback not available');
        }
    }
}

/* ============================================
   GLOBAL SEARCH FUNCTIONALITY
   ============================================ */

let searchTimeout;

function handleGlobalSearch(input) {
    clearTimeout(searchTimeout);
    
    const query = input.value.trim();
    
    if (query.length < 2) {
        hideSearchResults();
        return;
    }
    
    // Show loading
    showSearchResults('<div class="loading-container"><div class="spinner"></div><div class="loading-text">Searching...</div></div>');
    
    // Debounce search
    searchTimeout = setTimeout(() => {
        performSearch(query);
    }, 300);
}

async function performSearch(query) {
    try {
        const response = await fetch(`/api/admin/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        if (results.length === 0) {
            showSearchResults(`
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h3>No results found</h3>
                    <p>Try different keywords</p>
                </div>
            `);
        } else {
            displaySearchResults(results);
        }
    } catch (error) {
        showSearchResults(`
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Search Error</h3>
                <p>Unable to perform search</p>
            </div>
        `);
    }
}

function displaySearchResults(results) {
    const html = results.map(result => `
        <div class="search-result-item" onclick="navigateToResult('${result.type}', '${result.id}')">
            <div class="search-result-icon">
                <i class="fas ${getResultIcon(result.type)}"></i>
            </div>
            <div class="search-result-content">
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-meta">${result.meta}</div>
            </div>
        </div>
    `).join('');
    
    showSearchResults(html);
}

function getResultIcon(type) {
    const icons = {
        tourist: 'fa-user',
        alert: 'fa-exclamation-triangle',
        incident: 'fa-shield-alt',
        document: 'fa-file-alt'
    };
    return icons[type] || 'fa-circle';
}

function showSearchResults(html) {
    let resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'search-results';
        resultsContainer.className = 'search-results';
        document.querySelector('.global-search').appendChild(resultsContainer);
    }
    resultsContainer.innerHTML = html;
    resultsContainer.classList.add('show');
}

function hideSearchResults() {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.classList.remove('show');
    }
}

function navigateToResult(type, id) {
    // Implement navigation based on result type
    console.log(`Navigate to ${type}: ${id}`);
    hideSearchResults();
}

/* ============================================
   CHART.JS INITIALIZATION
   ============================================ */

function initCharts() {
    // Risk Distribution Pie Chart
    createRiskDistributionChart();
    
    // Tourist Activity Line Chart
    createActivityTrendChart();
    
    // Alert Priority Bar Chart
    createAlertPriorityChart();
}

function createRiskDistributionChart() {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx) return;
    
    AppState.charts.riskDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [45, 35, 20],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function createActivityTrendChart() {
    const ctx = document.getElementById('activityTrendChart');
    if (!ctx) return;
    
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const data = [65, 59, 80, 81, 56, 55, 40];
    
    AppState.charts.activityTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Active Tourists',
                data: data,
                fill: true,
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderColor: 'rgb(99, 102, 241)',
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createAlertPriorityChart() {
    const ctx = document.getElementById('alertPriorityChart');
    if (!ctx) return;
    
    AppState.charts.alertPriority = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                label: 'Number of Alerts',
                data: [12, 19, 15, 8],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)'
                ],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/* ============================================
   INTERACTIVE MAP INITIALIZATION
   ============================================ */

let touristMap;
let touristMarkers = [];

function initTouristMap() {
    const mapContainer = document.getElementById('touristMap');
    if (!mapContainer) return;
    
    // Initialize Leaflet map
    touristMap = L.map('touristMap').setView([20.5937, 78.9629], 5); // India center
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(touristMap);
    
    // Load tourist locations
    loadTouristLocations();
    
    // Refresh every 30 seconds
    setInterval(loadTouristLocations, 30000);
}

async function loadTouristLocations() {
    try {
        const response = await fetch('/api/admin/tourist-locations');
        const locations = await response.json();
        
        // Clear existing markers
        touristMarkers.forEach(marker => marker.remove());
        touristMarkers = [];
        
        // Add new markers
        locations.forEach(location => {
            const markerColor = getRiskColorForMarker(location.risk_level);
            
            const marker = L.circleMarker([location.lat, location.lng], {
                radius: 8,
                fillColor: markerColor,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(touristMap);
            
            marker.bindPopup(`
                <div style="min-width: 200px;">
                    <strong>${location.name}</strong><br>
                    <span class="badge badge-${location.risk_level}">${location.risk_level} Risk</span><br>
                    <small>Last update: ${new Date(location.timestamp).toLocaleString()}</small>
                </div>
            `);
            
            touristMarkers.push(marker);
        });
        
        showToast('success', 'Map Updated', `Loaded ${locations.length} tourist locations`);
    } catch (error) {
        console.error('Error loading tourist locations:', error);
        showToast('error', 'Map Error', 'Failed to load tourist locations');
    }
}

function getRiskColorForMarker(riskLevel) {
    const colors = {
        low: '#10b981',
        medium: '#f59e0b',
        high: '#ef4444'
    };
    return colors[riskLevel] || '#6366f1';
}

/* ============================================
   AUTO-REFRESH FUNCTIONALITY
   ============================================ */

let refreshIntervals = {};

function startAutoRefresh(sectionId, callback, interval = 30000) {
    // Clear existing interval
    if (refreshIntervals[sectionId]) {
        clearInterval(refreshIntervals[sectionId]);
    }
    
    // Set new interval
    refreshIntervals[sectionId] = setInterval(callback, interval);
    
    // Show indicator
    const section = document.getElementById(sectionId);
    if (section) {
        const indicator = document.createElement('div');
        indicator.className = 'auto-refresh-indicator';
        indicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Auto-refreshing...';
        section.querySelector('.section-header')?.appendChild(indicator);
    }
}

function stopAutoRefresh(sectionId) {
    if (refreshIntervals[sectionId]) {
        clearInterval(refreshIntervals[sectionId]);
        delete refreshIntervals[sectionId];
    }
}

/* ============================================
   DATA LOADING WITH SKELETON
   ============================================ */

function showSkeletonLoader(containerId, count = 5) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const skeletons = Array(count).fill(0).map(() => `
        <div class="skeleton-row" style="display: flex; align-items: center; gap: 1rem; padding: 1rem; margin-bottom: 0.5rem;">
            <div class="skeleton skeleton-avatar"></div>
            <div style="flex: 1;">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = skeletons;
}

function hideSkeletonLoader(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
    }
}

/* ============================================
   BULK ACTIONS
   ============================================ */

let selectedItems = new Set();

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedItems.add(cb.value);
        } else {
            selectedItems.delete(cb.value);
        }
    });
    updateBulkActionBar();
}

function toggleSelect(checkbox) {
    if (checkbox.checked) {
        selectedItems.add(checkbox.value);
    } else {
        selectedItems.delete(checkbox.value);
    }
    updateBulkActionBar();
}

function updateBulkActionBar() {
    const bar = document.getElementById('bulk-action-bar');
    const count = document.getElementById('selected-count');
    
    if (selectedItems.size > 0) {
        bar.classList.add('show');
        count.textContent = selectedItems.size;
    } else {
        bar.classList.remove('show');
    }
}

async function bulkAction(action) {
    if (selectedItems.size === 0) {
        showToast('warning', 'No Selection', 'Please select items first');
        return;
    }
    
    const confirmed = confirm(`Are you sure you want to ${action} ${selectedItems.size} items?`);
    if (!confirmed) return;
    
    try {
        const response = await fetch('/api/admin/bulk-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: action,
                items: Array.from(selectedItems)
            })
        });
        
        if (response.ok) {
            showToast('success', 'Success', `${action} completed for ${selectedItems.size} items`);
            selectedItems.clear();
            updateBulkActionBar();
            // Refresh data
            location.reload();
        } else {
            throw new Error('Bulk action failed');
        }
    } catch (error) {
        showToast('error', 'Error', 'Failed to perform bulk action');
    }
}

/* ============================================
   EXPORT FUNCTIONALITY
   ============================================ */

async function exportData(format, dataType) {
    showToast('info', 'Exporting...', `Preparing ${format.toUpperCase()} export`);
    
    try {
        const response = await fetch(`/api/admin/export/${dataType}?format=${format}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${dataType}_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
        showToast('success', 'Export Complete', `${format.toUpperCase()} file downloaded`);
    } catch (error) {
        showToast('error', 'Export Failed', 'Unable to export data');
    }
}

/* ============================================
   LANGUAGE SWITCHING
   ============================================ */

async function switchLanguage(lang) {
    AppState.language = lang;
    localStorage.setItem('admin-language', lang);
    
    try {
        const response = await fetch(`/api/translate/admin?lang=${lang}`);
        const translations = await response.json();
        
        // Apply translations
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (translations[key]) {
                element.textContent = translations[key];
            }
        });
        
        showToast('success', 'Language Changed', `Switched to ${lang.toUpperCase()}`);
    } catch (error) {
        showToast('error', 'Translation Error', 'Failed to load translations');
    }
}

/* ============================================
   NOTIFICATION POLLING
   ============================================ */

async function pollNotifications() {
    try {
        const response = await fetch('/api/admin/notifications/unread');
        const notifications = await response.json();
        
        updateNotificationBadge(notifications.length);
        
        // Show toast for new critical notifications
        notifications.forEach(notif => {
            if (notif.priority === 'critical' && !AppState.notifications.includes(notif.id)) {
                showToast('error', 'Critical Alert', notif.message, 10000);
                playAlertSound('error');
                AppState.notifications.push(notif.id);
            }
        });
    } catch (error) {
        console.error('Error polling notifications:', error);
    }
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

/* ============================================
   INITIALIZATION
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initTheme();
    
    // Initialize charts
    initCharts();
    
    // Initialize map
    initTouristMap();
    
    // Start auto-refresh for critical sections
    startAutoRefresh('sos-alerts', refreshSOSAlerts, 15000);
    startAutoRefresh('ai-monitoring', refreshAIMonitoring, 30000);
    
    // Poll notifications every 10 seconds
    setInterval(pollNotifications, 10000);
    pollNotifications();
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.global-search')) {
            hideSearchResults();
        }
    });
    
    // Show welcome message
    setTimeout(() => {
        showToast('success', 'Welcome Back!', 'Admin dashboard loaded successfully');
    }, 500);
});

/* ============================================
   EXISTING FUNCTIONS (Keep these)
   ============================================ */

// Add your existing functions here (refreshSOSAlerts, refreshAIMonitoring, etc.)
// These should remain as they were in the original file

</script>
```

---

## 📋 Part 4: Enhanced HTML Structure Examples

### Modern Header Structure:
```html
<header class="admin-header">
    <div class="container">
        <div class="header-wrapper">
            <!-- Logo -->
            <a href="#" class="admin-logo">
                <div class="logo-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <div class="logo-text">
                    <span data-translate="admin_dashboard">Admin Dashboard</span>
                    <span class="logo-subtitle">Tourist Safety System</span>
                </div>
            </a>
            
            <!-- Global Search -->
            <div class="global-search">
                <div class="search-wrapper">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" 
                           class="search-input" 
                           placeholder="Search tourists, alerts, incidents..." 
                           oninput="handleGlobalSearch(this)"
                           autocomplete="off">
                </div>
            </div>
            
            <!-- Header Actions -->
            <div class="header-actions">
                <!-- Dark Mode Toggle -->
                <button class="header-btn theme-toggle" onclick="toggleTheme()" title="Toggle Dark Mode">
                    <i class="fas fa-moon"></i>
                </button>
                
                <!-- Notifications -->
                <button class="header-btn notification-btn" onclick="toggleNotifications()" title="Notifications">
                    <i class="fas fa-bell"></i>
                    <span class="notification-badge">5</span>
                </button>
                
                <!-- Language Selector -->
                <select class="language-selector" onchange="switchLanguage(this.value)" title="Change Language">
                    <option value="en">🇬🇧 EN</option>
                    <option value="hi">🇮🇳 HI</option>
                    <option value="ta">தமிழ்</option>
                    <option value="te">తెలుగు</option>
                </select>
                
                <!-- Admin Profile -->
                <div class="admin-profile">
                    <div class="admin-avatar">
                        A
                        <span class="status-indicator"></span>
                    </div>
                    <div class="admin-info">
                        <div class="admin-name">Admin User</div>
                        <div class="admin-role">Super Admin</div>
                    </div>
                </div>
                
                <!-- Logout -->
                <a href="/" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>Logout</span>
                </a>
            </div>
        </div>
    </div>
</header>
```

### Modern Stats Cards:
```html
<div class="stats-grid">
    <!-- Primary Card -->
    <div class="stat-card primary" style="animation-delay: 0.1s">
        <div class="stat-card-header">
            <div class="stat-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-trend up">
                <i class="fas fa-arrow-up"></i>
                +12%
            </div>
        </div>
        <div class="stat-value">1,245</div>
        <div class="stat-label">Active Tourists</div>
        <div class="stat-footer">
            <span class="stat-footer-item">
                <i class="fas fa-clock"></i>
                Updated now
            </span>
            <a href="#" class="stat-footer-item clickable">
                View all →
            </a>
        </div>
    </div>
    
    <!-- Success Card -->
    <div class="stat-card success" style="animation-delay: 0.2s">
        <div class="stat-card-header">
            <div class="stat-icon">
                <i class="fas fa-link"></i>
            </div>
            <div class="stat-trend up">
                <i class="fas fa-check"></i>
                98.5%
            </div>
        </div>
        <div class="stat-value">23,456</div>
        <div class="stat-label">Blockchain Records</div>
        <div class="stat-footer">
            <span class="stat-footer-item">
                <i class="fas fa-shield-alt"></i>
                All secure
            </span>
        </div>
    </div>
    
    <!-- Warning Card -->
    <div class="stat-card warning" style="animation-delay: 0.3s">
        <div class="stat-card-header">
            <div class="stat-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="stat-trend up">
                <i class="fas fa-arrow-up"></i>
                +8
            </div>
        </div>
        <div class="stat-value">89</div>
        <div class="stat-label">Pending Documents</div>
        <div class="stat-footer">
            <span class="stat-footer-item">
                <i class="fas fa-hourglass-half"></i>
                Review needed
            </span>
        </div>
    </div>
    
    <!-- Danger Card -->
    <div class="stat-card danger" style="animation-delay: 0.4s">
        <div class="stat-card-header">
            <div class="stat-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="stat-trend down">
                <i class="fas fa-arrow-down"></i>
                -15%
            </div>
        </div>
        <div class="stat-value">7</div>
        <div class="stat-label">Active SOS Alerts</div>
        <div class="stat-footer">
            <span class="stat-footer-item">
                <i class="fas fa-clock"></i>
                3 critical
            </span>
        </div>
    </div>
</div>
```

### Modern Data Table:
```html
<div class="dashboard-section">
    <div class="section-header">
        <h2 class="section-title">
            <i class="fas fa-users"></i>
            Recent Tourists
        </h2>
        <div class="section-actions">
            <button class="btn btn-outline" onclick="exportData('csv', 'tourists')">
                <i class="fas fa-download"></i>
                Export CSV
            </button>
            <button class="btn btn-primary">
                <i class="fas fa-plus"></i>
                Add Tourist
            </button>
        </div>
    </div>
    
    <div class="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th><input type="checkbox" onchange="toggleSelectAll(this)"></th>
                    <th>Tourist</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Risk Level</th>
                    <th>Last Active</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><input type="checkbox" class="item-checkbox" value="1" onchange="toggleSelect(this)"></td>
                    <td>
                        <div class="user-cell">
                            <div class="user-avatar">JD</div>
                            <div class="user-info">
                                <div class="user-name">John Doe</div>
                                <div class="user-meta">john@example.com</div>
                            </div>
                        </div>
                    </td>
                    <td>New Delhi, India</td>
                    <td><span class="badge badge-success"><i class="fas fa-check"></i> Active</span></td>
                    <td><span class="badge badge-success">Low</span></td>
                    <td>2 minutes ago</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="action-btn action-btn-edit" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn action-btn-delete" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

---

## 🎯 Implementation Checklist

- [ ] Replace `<head>` section with modern fonts & libraries
- [ ] Replace `<style>` section with complete CSS system
- [ ] Add JavaScript before `</body>` tag
- [ ] Update header HTML structure
- [ ] Modernize stat cards layout
- [ ] Update data tables with new classes
- [ ] Add toast container to body
- [ ] Test dark mode toggle
- [ ] Test global search
- [ ] Verify chart rendering
- [ ] Test responsive design on mobile

---

**Ready to apply?** I can now apply all these changes directly to your `admin_dashboard.html` file! 🚀
