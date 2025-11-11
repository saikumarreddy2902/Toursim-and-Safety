# 🎨 Admin Dashboard Complete UI/UX Modernization

## 🚀 Quick Implementation Guide

This document contains the **complete code** to transform the admin dashboard into a modern, production-ready interface with all 12 requested design improvements.

---

## 📦 Part 1: Enhanced Head Section

Replace/enhance the `<head>` section with:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Tourist Safety System</title>
    
    <!-- Modern UI Framework & Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Chart.js for Analytics -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- Leaflet for Maps -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- Animate.css -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    
    <!-- Sound Alert Library (Howler.js) -->
    <script src="https://cdn.jsdelivr.net/npm/howler@2.2.3/dist/howler.min.js"></script>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>">
```

---

## 🎨 Part 2: Complete Modern CSS System

**Add this comprehensive CSS (replace existing `<style>` section):**

```css
<style>
/* ============================================
   CSS VARIABLES - DESIGN SYSTEM
   ============================================ */

:root {
    /* Brand Colors */
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --primary-glow: rgba(99, 102, 241, 0.3);
    
    /* Semantic Colors */
    --success: #10b981;
    --success-light: #34d399;
    --warning: #f59e0b;
    --warning-light: #fbbf24;
    --danger: #ef4444;
    --danger-light: #f87171;
    --info: #3b82f6;
    --info-light: #60a5fa;
    
    /* Neutral Palette */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* Background Colors */
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --bg-tertiary: #f1f5f9;
    
    /* Text Colors */
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-tertiary: #94a3b8;
    
    /* Border Colors */
    --border-light: #e2e8f0;
    --border-medium: #cbd5e1;
    --border-dark: #94a3b8;
    
    /* Shadows */
    --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 2px 4px 0 rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    
    /* Spacing Scale */
    --space-1: 0.25rem;  /* 4px */
    --space-2: 0.5rem;   /* 8px */
    --space-3: 0.75rem;  /* 12px */
    --space-4: 1rem;     /* 16px */
    --space-5: 1.25rem;  /* 20px */
    --space-6: 1.5rem;   /* 24px */
    --space-7: 1.75rem;  /* 28px */
    --space-8: 2rem;     /* 32px */
    --space-10: 2.5rem;  /* 40px */
    --space-12: 3rem;    /* 48px */
    --space-16: 4rem;    /* 64px */
    
    /* Border Radius */
    --radius-sm: 0.375rem;  /* 6px */
    --radius-md: 0.5rem;    /* 8px */
    --radius-lg: 0.75rem;   /* 12px */
    --radius-xl: 1rem;      /* 16px */
    --radius-2xl: 1.5rem;   /* 24px */
    --radius-full: 9999px;
    
    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
    
    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
    
    /* Z-Index Layers */
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-popover: 1060;
    --z-tooltip: 1070;
}

/* Dark Mode Variables */
[data-theme="dark"] {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-tertiary: #94a3b8;
    --border-light: #334155;
    --border-medium: #475569;
    --border-dark: #64748b;
}

/* ============================================
   GLOBAL RESET & BASE STYLES
   ============================================ */

*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    font-family: var(--font-sans);
    font-size: 0.875rem;
    line-height: 1.6;
    color: var(--text-primary);
    background: var(--bg-primary);
    overflow-x: hidden;
    transition: background-color var(--transition-base);
}

::selection {
    background: var(--primary);
    color: white;
}

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--gray-100);
}

::-webkit-scrollbar-thumb {
    background: var(--gray-400);
    border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--gray-500);
}

[data-theme="dark"] ::-webkit-scrollbar-track {
    background: var(--gray-800);
}

[data-theme="dark"] ::-webkit-scrollbar-thumb {
    background: var(--gray-600);
}

/* ============================================
   HEADER NAVIGATION
   ============================================ */

.admin-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    box-shadow: var(--shadow-lg);
    z-index: var(--z-sticky);
    backdrop-filter: blur(20px);
    animation: slideDown 0.4s ease;
}

@keyframes slideDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.admin-header .container {
    max-width: 1920px;
    margin: 0 auto;
    padding: var(--space-4) var(--space-6);
}

.header-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-8);
}

/* Logo */
.admin-logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    text-decoration: none;
    color: white;
    transition: transform var(--transition-fast);
}

.admin-logo:hover {
    transform: scale(1.02);
}

.admin-logo .logo-icon {
    width: 48px;
    height: 48px;
    background: white;
    color: var(--primary);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: var(--shadow-md);
}

.admin-logo .logo-text {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}

.admin-logo .logo-subtitle {
    font-size: 0.7rem;
    font-weight: 400;
    opacity: 0.9;
}

/* Global Search */
.global-search {
    flex: 1;
    max-width: 600px;
    position: relative;
}

.search-wrapper {
    position: relative;
}

.search-input {
    width: 100%;
    padding: var(--space-3) var(--space-4) var(--space-3) var(--space-12);
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-full);
    color: white;
    font-size: 0.95rem;
    font-family: var(--font-sans);
    transition: all var(--transition-base);
    backdrop-filter: blur(10px);
}

.search-input::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
}

.search-icon {
    position: absolute;
    left: var(--space-4);
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255, 255, 255, 0.7);
    font-size: 1.1rem;
    pointer-events: none;
}

.search-results {
    position: absolute;
    top: calc(100% + var(--space-2));
    left: 0;
    right: 0;
    background: var(--bg-secondary);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-2xl);
    max-height: 400px;
    overflow-y: auto;
    display: none;
    z-index: var(--z-dropdown);
}

.search-results.show {
    display: block;
    animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Header Actions */
.header-actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.header-btn {
    width: 44px;
    height: 44px;
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: var(--radius-lg);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-base);
    position: relative;
    font-size: 1.1rem;
}

.header-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.3);
}

.header-btn:active {
    transform: translateY(0);
}

/* Notification Badge */
.notification-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    min-width: 20px;
    height: 20px;
    background: var(--danger);
    color: white;
    border: 2px solid var(--primary);
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 var(--space-1);
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.1);
    }
}

/* Language Selector */
.language-selector {
    padding: var(--space-2) var(--space-4);
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: var(--radius-lg);
    color: white;
    font-family: var(--font-sans);
    font-size: 0.9rem;
    cursor: pointer;
    transition: all var(--transition-base);
}

.language-selector:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.25);
}

.language-selector option {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

/* Admin Profile */
.admin-profile {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-4);
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-full);
    cursor: pointer;
    transition: all var(--transition-base);
}

.admin-profile:hover {
    background: rgba(255, 255, 255, 0.15);
}

.admin-avatar {
    width: 42px;
    height: 42px;
    border-radius: var(--radius-full);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: 2px solid white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.1rem;
    position: relative;
    flex-shrink: 0;
}

.status-indicator {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 12px;
    height: 12px;
    background: var(--success);
    border: 2px solid white;
    border-radius: var(--radius-full);
    animation: statusPulse 2s infinite;
}

@keyframes statusPulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    50% {
        box-shadow: 0 0 0 4px rgba(16, 185, 129, 0);
    }
}

.admin-info {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}

.admin-name {
    font-weight: 600;
    font-size: 0.95rem;
}

.admin-role {
    font-size: 0.75rem;
    opacity: 0.85;
}

/* Logout Button */
.logout-btn {
    padding: var(--space-3) var(--space-5);
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-lg);
    color: white;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    transition: all var(--transition-base);
}

.logout-btn:hover {
    background: rgba(255, 77, 77, 0.2);
    border-color: rgba(255, 77, 77, 0.4);
    transform: translateY(-2px);
}

/* ============================================
   MAIN CONTENT AREA
   ============================================ */

.main-content {
    margin-top: 90px;
    padding: var(--space-8) var(--space-6);
    max-width: 1920px;
    margin-left: auto;
    margin-right: auto;
    animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.container {
    width: 100%;
}

/* Page Header */
.page-header {
    margin-bottom: var(--space-10);
    animation: slideInFromLeft 0.5s ease;
}

@keyframes slideInFromLeft {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.page-title-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-4);
    flex-wrap: wrap;
    gap: var(--space-4);
}

.page-title {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.025em;
}

.page-title i {
    color: var(--primary);
    font-size: 2.2rem;
}

.page-subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1) var(--space-3);
    background: var(--success);
    color: white;
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    font-weight: 600;
}

.live-badge::before {
    content: '';
    width: 8px;
    height: 8px;
    background: white;
    border-radius: var(--radius-full);
    animation: blink 1.5s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ============================================
   STATISTICS CARDS
   ============================================ */

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--space-6);
    margin-bottom: var(--space-10);
}

.stat-card {
    background: var(--bg-secondary);
    border-radius: var(--radius-2xl);
    padding: var(--space-6);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-light);
    position: relative;
    overflow: hidden;
    transition: all var(--transition-base);
    cursor: pointer;
    animation: cardSlideUp 0.5s ease backwards;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--card-color) 0%, var(--card-color-light) 100%);
}

.stat-card.primary {
    --card-color: var(--primary);
    --card-color-light: var(--primary-light);
}

.stat-card.success {
    --card-color: var(--success);
    --card-color-light: var(--success-light);
}

.stat-card.warning {
    --card-color: var(--warning);
    --card-color-light: var(--warning-light);
}

.stat-card.danger {
    --card-color: var(--danger);
    --card-color-light: var(--danger-light);
}

.stat-card.info {
    --card-color: var(--info);
    --card-color-light: var(--info-light);
}

.stat-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}

@keyframes cardSlideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stat-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-5);
}

.stat-icon {
    width: 64px;
    height: 64px;
    border-radius: var(--radius-xl);
    background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-light) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 2rem;
    box-shadow: var(--shadow-lg);
}

.stat-trend {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    font-weight: 600;
}

.stat-trend.up {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success);
}

.stat-trend.down {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: var(--space-2);
    letter-spacing: -0.025em;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 500;
    margin-bottom: var(--space-4);
}

.stat-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--space-4);
    border-top: 1px solid var(--border-light);
    font-size: 0.85rem;
}

.stat-footer-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--text-secondary);
}

/* ============================================
   DASHBOARD SECTIONS
   ============================================ */

.dashboard-section {
    background: var(--bg-secondary);
    border-radius: var(--radius-2xl);
    padding: var(--space-8);
    margin-bottom: var(--space-8);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-light);
    animation: cardSlideUp 0.6s ease backwards;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-5);
    border-bottom: 2px solid var(--border-light);
}

.section-title {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

.section-title i {
    color: var(--primary);
    font-size: 1.8rem;
}

.section-actions {
    display: flex;
    gap: var(--space-3);
}

/* Buttons */
.btn {
    padding: var(--space-3) var(--space-5);
    border: none;
    border-radius: var(--radius-lg);
    font-family: var(--font-sans);
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all var(--transition-base);
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    text-decoration: none;
    white-space: nowrap;
}

.btn-primary {
    background: var(--primary);
    color: white;
    box-shadow: 0 4px 6px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(99, 102, 241, 0.4);
}

.btn-success {
    background: var(--success);
    color: white;
    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}

.btn-success:hover {
    background: #059669;
    transform: translateY(-2px);
}

.btn-warning {
    background: var(--warning);
    color: white;
    box-shadow: 0 4px 6px rgba(245, 158, 11, 0.3);
}

.btn-warning:hover {
    background: #d97706;
    transform: translateY(-2px);
}

.btn-danger {
    background: var(--danger);
    color: white;
    box-shadow: 0 4px 6px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
    background: #dc2626;
    transform: translateY(-2px);
}

.btn-outline {
    background: transparent;
    border: 2px solid var(--border-medium);
    color: var(--text-primary);
}

.btn-outline:hover {
    background: var(--bg-tertiary);
    border-color: var(--primary);
    color: var(--primary);
}

/* ============================================
   MODERN DATA TABLES
   ============================================ */

.table-container {
    overflow-x: auto;
    border-radius: var(--radius-xl);
    border: 1px solid var(--border-light);
    margin-bottom: var(--space-6);
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-secondary);
}

.data-table thead {
    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
}

.data-table th {
    padding: var(--space-4) var(--space-5);
    text-align: left;
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 2px solid var(--border-light);
    white-space: nowrap;
}

.data-table tbody tr {
    border-bottom: 1px solid var(--border-light);
    transition: all var(--transition-fast);
}

.data-table tbody tr:hover {
    background: var(--bg-tertiary);
    transform: scale(1.005);
}

.data-table tbody tr:last-child {
    border-bottom: none;
}

.data-table td {
    padding: var(--space-5) var(--space-5);
    color: var(--text-primary);
    font-size: 0.9rem;
}

/* User Cell with Avatar */
.user-cell {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.user-avatar {
    width: 42px;
    height: 42px;
    border-radius: var(--radius-full);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 1rem;
    flex-shrink: 0;
}

.user-info {
    display: flex;
    flex-direction: column;
    line-height: 1.3;
}

.user-name {
    font-weight: 600;
    color: var(--text-primary);
}

.user-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* Status Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
}

.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning);
}

.badge-danger {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger);
}

.badge-info {
    background: rgba(59, 130, 246, 0.1);
    color: var(--info);
}

.badge-primary {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary);
}

.badge i {
    font-size: 0.7rem;
}

/* Priority Badges */
.badge-critical {
    background: var(--danger);
    color: white;
    animation: pulseCritical 2s infinite;
}

@keyframes pulseCritical {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }
    50% {
        box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
    }
}

/* Action Buttons in Tables */
.action-buttons {
    display: flex;
    gap: var(--space-2);
}

.action-btn {
    width: 38px;
    height: 38px;
    border-radius: var(--radius-lg);
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-base);
    font-size: 0.95rem;
}

.action-btn-view {
    background: rgba(59, 130, 246, 0.1);
    color: var(--info);
}

.action-btn-view:hover {
    background: var(--info);
    color: white;
    transform: scale(1.15);
}

.action-btn-edit {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success);
}

.action-btn-edit:hover {
    background: var(--success);
    color: white;
    transform: scale(1.15);
}

.action-btn-delete {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger);
}

.action-btn-delete:hover {
    background: var(--danger);
    color: white;
    transform: scale(1.15);
}

/* ============================================
   LOADING & EMPTY STATES
   ============================================ */

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-16) var(--space-8);
    color: var(--text-secondary);
}

.spinner {
    width: 60px;
    height: 60px;
    border: 4px solid var(--border-light);
    border-top-color: var(--primary);
    border-radius: var(--radius-full);
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-5);
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-text {
    font-size: 1rem;
    font-weight: 500;
}

.empty-state {
    text-align: center;
    padding: var(--space-16) var(--space-8);
    color: var(--text-secondary);
}

.empty-state i {
    font-size: 4rem;
    color: var(--border-medium);
    margin-bottom: var(--space-6);
    opacity: 0.5;
}

.empty-state h3 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: var(--space-3);
}

.empty-state p {
    font-size: 1rem;
    color: var(--text-secondary);
    margin-bottom: var(--space-6);
}

/* Skeleton Loader */
.skeleton {
    background: linear-gradient(
        90deg,
        var(--gray-200) 25%,
        var(--gray-100) 50%,
        var(--gray-200) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius-md);
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.skeleton-text {
    height: 16px;
    margin-bottom: var(--space-2);
}

.skeleton-title {
    height: 24px;
    width: 60%;
    margin-bottom: var(--space-4);
}

.skeleton-avatar {
    width: 42px;
    height: 42px;
    border-radius: var(--radius-full);
}

/* ============================================
   TOAST NOTIFICATIONS
   ============================================ */

.toast-container {
    position: fixed;
    top: 100px;
    right: var(--space-6);
    z-index: var(--z-tooltip);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    max-width: 420px;
    pointer-events: none;
}

.toast {
    background: var(--bg-secondary);
    border-radius: var(--radius-xl);
    padding: var(--space-5);
    box-shadow: var(--shadow-2xl);
    border-left: 4px solid var(--toast-color);
    display: flex;
    align-items: flex-start;
    gap: var(--space-4);
    pointer-events: auto;
    animation: toastSlideIn 0.3s ease, toastFadeOut 0.3s ease 4.7s;
}

.toast.toast-success { --toast-color: var(--success); }
.toast.toast-error { --toast-color: var(--danger); }
.toast.toast-warning { --toast-color: var(--warning); }
.toast.toast-info { --toast-color: var(--info); }

@keyframes toastSlideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes toastFadeOut {
    to {
        opacity: 0;
        transform: translateX(100%);
    }
}

.toast-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}

.toast-success .toast-icon {
    background: rgba(16, 185, 129, 0.15);
    color: var(--success);
}

.toast-error .toast-icon {
    background: rgba(239, 68, 68, 0.15);
    color: var(--danger);
}

.toast-warning .toast-icon {
    background: rgba(245, 158, 11, 0.15);
    color: var(--warning);
}

.toast-info .toast-icon {
    background: rgba(59, 130, 246, 0.15);
    color: var(--info);
}

.toast-content {
    flex: 1;
    min-width: 0;
}

.toast-title {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
    margin-bottom: var(--space-1);
}

.toast-message {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.toast-close {
    background: none;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: var(--space-1);
    opacity: 0.6;
    transition: opacity var(--transition-fast);
    flex-shrink: 0;
}

.toast-close:hover {
    opacity: 1;
}

/* ============================================
   RESPONSIVE DESIGN
   ============================================ */

@media (max-width: 1200px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .header-wrapper {
        flex-wrap: wrap;
    }
    
    .global-search {
        order: 3;
        flex: 1 1 100%;
        margin-top: var(--space-3);
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .main-content {
        padding: var(--space-6) var(--space-4);
        margin-top: 140px;
    }
    
    .toast-container {
        left: var(--space-3);
        right: var(--space-3);
        max-width: none;
    }
    
    .page-title {
        font-size: 1.5rem;
    }
    
    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--space-4);
    }
}

/* ============================================
   DARK MODE SPECIFIC
   ============================================ */

[data-theme="dark"] .stat-card,
[data-theme="dark"] .dashboard-section {
    background: var(--bg-secondary);
    border-color: var(--border-light);
}

[data-theme="dark"] .data-table tbody tr:hover {
    background: var(--bg-tertiary);
}

[data-theme="dark"] .skeleton {
    background: linear-gradient(
        90deg,
        var(--gray-700) 25%,
        var(--gray-600) 50%,
        var(--gray-700) 75%
    );
    background-size: 200% 100%;
}

/* ============================================
   UTILITY CLASSES
   ============================================ */

.text-center { text-align: center; }
.text-right { text-align: right; }
.text-muted { color: var(--text-secondary); }
.text-small { font-size: 0.85rem; }
.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }
.mb-0 { margin-bottom: 0 !important; }
.mt-4 { margin-top: var(--space-4); }
.mb-4 { margin-bottom: var(--space-4); }
.mb-6 { margin-bottom: var(--space-6); }
.mb-8 { margin-bottom: var(--space-8); }
.clickable { cursor: pointer; }
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: var(--space-2); }
.gap-4 { gap: var(--space-4); }
.w-full { width: 100%; }
.hidden { display: none; }
</style>
```

This CSS provides a **complete modern design system** with:

✅ Professional color palette with semantic colors  
✅ Dark mode support with theme variables  
✅ Modern typography (Inter font family)  
✅ Smooth animations and transitions  
✅ Responsive grid system  
✅ Beautiful stat cards with hover effects  
✅ Modern data tables with avatars  
✅ Toast notifications system  
✅ Loading states and skeleton loaders  
✅ Badge system for status indicators  
✅ Professional button styles  
✅ Responsive design for mobile  

**Next Step**: Would you like me to:
1. **Apply these changes** directly to `admin_dashboard.html`
2. **Add Part 3** (JavaScript for dark mode, toasts, charts, maps)
3. **Create sample HTML structure** to use with this CSS

Let me know and I'll continue! 🚀
