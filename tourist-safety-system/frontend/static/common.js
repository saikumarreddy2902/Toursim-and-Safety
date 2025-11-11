// Common JavaScript functionality for Tourist Safety System

// Language support
// Use a single global variable across the site to avoid 'already been declared' errors
// If this script is included multiple times or other pages also define the variable,
// prefer the existing value.
if (typeof translations === 'undefined') {
    var translations = {};
}

// Language options with native names
const LANGUAGE_OPTIONS = {
    'en': 'English',
    'hi': 'हिंदी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'bn': 'বাংলা',
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
    'kn': 'ಕನ್ನಡ',
    'ml': 'മലയാളം',
    'pa': 'ਪੰਜਾਬੀ',
    'or': 'ଓଡ଼ିଆ',
    'as': 'অসমীয়া'
};

// Ensure language buttons always show ONLY the clean native name (avoid translated suffixes)
function resetLanguageButtonLabels() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        // Determine code from id="lang-xx" or data-lang
        let code = null;
        if (btn.id && btn.id.startsWith('lang-')) {
            code = btn.id.substring(5);
        } else if (btn.dataset.lang) {
            code = btn.dataset.lang;
        }
        if (code && LANGUAGE_OPTIONS[code]) {
            // Set plain native label (strip anything previously appended)
            btn.textContent = LANGUAGE_OPTIONS[code];
        }
    });
}

// ===================== FULL PAGE TRANSLATION VIA BATCH API (BHASHINI/GOOGLE) =====================
// Cache: { targetLang: { originalText: translatedText } }
window.pageTranslationCache = window.pageTranslationCache || {};
// Store original text nodes so we can restore to English or base language
window._originalTextNodes = window._originalTextNodes || new WeakMap();

const PAGE_TRANSLATION_CONFIG = {
    minLength: 3,               // skip very short tokens
    maxBatchSize: 20,           // smaller batches for faster response
    attrOriginal: 'data-original-text',
    excludeSelectors: [
        '.lang-btn', 
        '[data-no-translate]', 
        'script', 
        'style', 
        'noscript', 
        'meta', 
        'title',
        '.language-grid',       // exclude entire language grid
        '[id*="lang-"]',        // exclude any element with lang- in id
        '.language-selector'    // exclude language selectors
    ],
};

function shouldExcludeElement(el) {
    if (!el || el.nodeType !== 1) return false;
    for (const sel of PAGE_TRANSLATION_CONFIG.excludeSelectors) {
        try { if (el.matches(sel)) return true; } catch (_) { /* ignore */ }
    }
    return false;
}

function collectTranslatableTextNodes() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
            const text = node.textContent || '';
            const parent = node.parentElement;
            if (!parent) return NodeFilter.FILTER_REJECT;
            if (shouldExcludeElement(parent)) return NodeFilter.FILTER_REJECT;
            const trimmed = text.trim();
            if (!trimmed) return NodeFilter.FILTER_REJECT;
            if (trimmed.length < PAGE_TRANSLATION_CONFIG.minLength) return NodeFilter.FILTER_REJECT;
            // Skip pure numbers / symbols
            if (!/[A-Za-z\u0900-\u0CFF]/.test(trimmed)) return NodeFilter.FILTER_REJECT;
    // Mutation observer to auto-translate dynamically injected content
    let _translationObserverInitialized = false;
    function initializeTranslationObserver() {
        if (_translationObserverInitialized) return;
        const observer = new MutationObserver(mutations => {
            if (!currentLanguage || currentLanguage === 'en') return; // only needed for non-English
            let needsUpdate = false;
            for (const m of mutations) {
                if (m.addedNodes && m.addedNodes.length) {
                    needsUpdate = true; break;
                }
            }
            if (needsUpdate) {
                // Debounce
                clearTimeout(window._translateDebounceTimer);
                window._translateDebounceTimer = setTimeout(() => {
                    bulkTranslatePage(currentLanguage).catch(()=>{});
                    translatePlaceholders(currentLanguage).catch(()=>{});
                }, 250);
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
        _translationObserverInitialized = true;
    }
            return NodeFilter.FILTER_ACCEPT;
        }
    });
    const nodes = [];
    while (walker.nextNode()) {
        nodes.push(walker.currentNode);
    }
    return nodes;
}

async function batchTranslate(texts, targetLang) {
    if (!texts.length) return [];
    const payload = {
        texts,
        source_lang: 'auto',
        target_lang: targetLang
    };
    try {
        const resp = await fetch('/api/translate/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error('Batch translate failed');
        const data = await resp.json();
        if (data.success && Array.isArray(data.translations)) {
            return data.translations;
        }
    } catch (e) {
        console.warn('Batch translation error', e);
    }
    // Fallback: return originals
    return texts;
}

// Translation state management
window._isTranslating = false;
window._lastTranslationLang = null;

async function bulkTranslatePage(targetLang) {
    // Prevent multiple simultaneous translations
    if (window._isTranslating) {
        console.log('Translation already in progress, skipping...');
        return;
    }
    
    // Skip if same language as last translation
    if (window._lastTranslationLang === targetLang) {
        console.log('Already translated to', targetLang);
        return;
    }
    
    window._isTranslating = true;
    
    try {
        // Restore if English/base
        if (targetLang === 'en') {
            restoreOriginalPageText();
            window._lastTranslationLang = 'en';
            return;
        }
        
        const cacheForLang = window.pageTranslationCache[targetLang] = window.pageTranslationCache[targetLang] || {};
        const textNodes = collectTranslatableTextNodes();
        const uniqueTexts = [];
        
        // Collect only texts that need translation
        for (const node of textNodes) {
            const original = node.textContent || '';
            if (!window._originalTextNodes.has(node)) {
                window._originalTextNodes.set(node, original);
            }
            if (!(original in cacheForLang) && original.trim().length > 0) {
                uniqueTexts.push(original);
            }
        }

        console.log(`Translating ${uniqueTexts.length} unique texts to ${targetLang}`);

        // Chunk and translate missing texts with smaller batches for speed
        for (let i = 0; i < uniqueTexts.length; i += PAGE_TRANSLATION_CONFIG.maxBatchSize) {
            const slice = uniqueTexts.slice(i, i + PAGE_TRANSLATION_CONFIG.maxBatchSize);
            const results = await batchTranslate(slice, targetLang);
            results.forEach((translated, idx) => {
                const orig = slice[idx];
                cacheForLang[orig] = translated || orig;
            });
        }

        // Apply translations immediately
        textNodes.forEach(node => {
            const original = window._originalTextNodes.get(node) || node.textContent || '';
            const translated = cacheForLang[original];
            if (translated && translated !== original) {
                node.textContent = translated;
            }
        });
        
        window._lastTranslationLang = targetLang;
        
    } finally {
        window._isTranslating = false;
        
        // Ensure language buttons stay clean after translation
        setTimeout(() => {
            resetLanguageButtonLabels();
        }, 100);
    }
}

function restoreOriginalPageText() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    while (walker.nextNode()) {
        const node = walker.currentNode;
        if (window._originalTextNodes.has(node)) {
            const original = window._originalTextNodes.get(node);
            if (typeof original === 'string') {
                node.textContent = original;
            }
        }
    }
}

// Load translations
async function loadTranslations() {
    try {
        const response = await fetch('/static/translations.json');
        translations = await response.json();
        
        // Initialize language from backend/localStorage
        await initializeLanguage();
        
    } catch (error) {
        console.error('Error loading translations:', error);
        // Fallback to English if translations fail to load
        translations = {
            en: {},
            hi: {}
        };
        currentLanguage = 'en';
        updatePageText();
    }
}

// Switch language
async function switchLanguage(lang) {
    // Show loading indicator
    showLanguageChangeLoading(true);
    
    currentLanguage = lang;
    
    // Save to localStorage for immediate use
    localStorage.setItem('preferred_language', lang);
    
    // Send to backend to maintain session consistency
    try {
        await fetch('/api/set_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: lang })
        });
    } catch (error) {
        console.warn('Could not sync language with backend:', error);
    }
    
    // Update language selector if it exists
    const languageSelect = document.getElementById('language-select');
    if (languageSelect) {
        languageSelect.value = lang;
    }
    
    // Update button states
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const langBtn = document.getElementById('lang-' + lang);
    if (langBtn) {
        langBtn.classList.add('active');
    }

    // Restore clean button labels (prevents compounding translations)
    resetLanguageButtonLabels();
    
    updatePageText();
    
    // Show brief loading for translation
    showLanguageChangeLoading(true);
    
    // Perform full-page translation using batch API
    await bulkTranslatePage(lang);
    
    // Hide loading
    // Hide loading indicator (single call)
    showLanguageChangeLoading(false);
    
    // Show success message
    const languageNames = {
        'en': 'English', 'hi': 'हिंदी', 'ta': 'தமிழ்', 'te': 'తెలుగు',
        'bn': 'বাংলা', 'mr': 'मराठी', 'gu': 'ગુજરાતી', 'kn': 'ಕನ್ನಡ',
        'ml': 'മലയാളം', 'pa': 'ਪੰਜਾਬੀ', 'or': 'ଓଡ଼ିଆ', 'as': 'অসমীয়া'
    };
    showToast(`Language changed to ${languageNames[lang]}`, 'success');
    
    // Trigger custom event for other components to listen to language changes
    window.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { 
            language: lang,
            translations: translations[lang] || {}
        }
    }));
}

// Show/hide language change loading indicator
function showLanguageChangeLoading(show) {
    let loader = document.getElementById('language-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'language-loader';
        loader.innerHTML = `
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                        background: rgba(0,0,0,0.8); color: white; padding: 20px; border-radius: 10px; 
                        z-index: 10000; display: none;">
                <i class="fas fa-language fa-spin"></i> Switching language...
            </div>
        `;
        document.body.appendChild(loader);
    }
    
    const loaderContent = loader.querySelector('div');
    loaderContent.style.display = show ? 'block' : 'none';
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 10001;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    toast.textContent = message;
    
    // Add animation styles if not already present
    if (!document.getElementById('toast-styles')) {
        const styles = document.createElement('style');
        styles.id = 'toast-styles';
        styles.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Initialize user's preferred language from backend or localStorage
async function initializeLanguage() {
    try {
        // First check backend for session language
        const response = await fetch('/api/get_language');
        const data = await response.json();
        
        if (data.success && data.language) {
            currentLanguage = data.language;
        } else {
            // Fallback to localStorage
            currentLanguage = localStorage.getItem('preferred_language') || 'en';
        }
    } catch (error) {
        console.warn('Could not get language from backend, using localStorage:', error);
        currentLanguage = localStorage.getItem('preferred_language') || 'en';
    }
    
    // Set the language without making another API call
    localStorage.setItem('preferred_language', currentLanguage);
    
    // Update UI elements
    const languageSelect = document.getElementById('language-select');
    if (languageSelect) {
        languageSelect.value = currentLanguage;
    }
    
    // Initialize form language support
    initializeFormLanguageSupport();
    
    // Initialize navigation language support
    initializeNavigationLanguageSupport();
    
    updatePageText();
    // After page text updates, restore language button labels
    resetLanguageButtonLabels();
    
    // Trigger custom event for other components to listen to language changes
    window.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { 
            language: currentLanguage,
            translations: translations[currentLanguage] || {}
        }
    }));

    // Also listen for subsequent external languageChanged events (once) to keep labels clean
    if (!window._langButtonsLabelFixBound) {
        window.addEventListener('languageChanged', () => {
            resetLanguageButtonLabels();
        });
        window._langButtonsLabelFixBound = true;
    }

    // One-time initial page translation if the stored language isn't English.
    if (!window._initialLanguageApplied) {
        window._initialLanguageApplied = true;
        if (currentLanguage !== 'en') {
            // Defer to allow DOM ready handlers to finish
            setTimeout(() => switchLanguage(currentLanguage), 0);
        }
    }
}

// Language-aware API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Accept-Language': currentLanguage,
            ...options.headers
        }
    };
    
    // Add language to request body if it's a POST/PUT request
    if (options.method && ['POST', 'PUT', 'PATCH'].includes(options.method.toUpperCase())) {
        if (options.body && typeof options.body === 'string') {
            try {
                const bodyData = JSON.parse(options.body);
                bodyData.language = currentLanguage;
                options.body = JSON.stringify(bodyData);
            } catch (e) {
                // If body is not JSON, append language as query parameter
                url += (url.includes('?') ? '&' : '?') + `language=${currentLanguage}`;
            }
        } else if (options.body && typeof options.body === 'object') {
            options.body.language = currentLanguage;
            options.body = JSON.stringify(options.body);
        }
    } else {
        // For GET requests, add language as query parameter
        url += (url.includes('?') ? '&' : '?') + `language=${currentLanguage}`;
    }
    
    return fetch(url, { ...defaultOptions, ...options });
}

// Form submission wrapper to ensure language consistency
function submitFormWithLanguage(form, options = {}) {
    const formData = new FormData(form);
    
    // Ensure language is included
    if (!formData.has('language')) {
        formData.append('language', currentLanguage || 'en');
    }
    
    // Convert FormData to JSON if needed
    if (options.asJson) {
        const jsonData = {};
        for (let [key, value] of formData.entries()) {
            jsonData[key] = value;
        }
        
        return apiRequest(form.action || options.url, {
            method: form.method || 'POST',
            body: JSON.stringify(jsonData),
            ...options
        });
    }
    
    return apiRequest(form.action || options.url, {
        method: form.method || 'POST',
        body: formData,
        headers: {
            // Remove Content-Type to let browser set it with boundary for FormData
            ...Object.fromEntries(Object.entries(options.headers || {}).filter(([key]) => 
                key.toLowerCase() !== 'content-type'))
        },
        ...options
    });
}

// Auto-attach language preservation to all forms
function initializeFormLanguageSupport() {
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.tagName === 'FORM' && !form.hasAttribute('data-no-lang')) {
            // Add hidden language field if not present
            let langInput = form.querySelector('input[name="language"]');
            if (!langInput) {
                langInput = document.createElement('input');
                langInput.type = 'hidden';
                langInput.name = 'language';
                form.appendChild(langInput);
            }
            langInput.value = currentLanguage || 'en';
        }
    });
}

// Enhanced function to handle dynamic content with language support
function loadContentWithLanguage(url, targetElement, options = {}) {
    const languageUrl = url + (url.includes('?') ? '&' : '?') + `language=${currentLanguage}`;
    
    return fetch(languageUrl, {
        headers: {
            'Accept-Language': currentLanguage,
            ...options.headers
        },
        ...options
    })
    .then(response => response.text())
    .then(html => {
        if (targetElement) {
            targetElement.innerHTML = html;
            // Re-initialize language support for new content
            const newForms = targetElement.querySelectorAll('form');
            newForms.forEach(form => {
                if (!form.hasAttribute('data-no-lang')) {
                    let langInput = form.querySelector('input[name="language"]');
                    if (!langInput) {
                        langInput = document.createElement('input');
                        langInput.type = 'hidden';
                        langInput.name = 'language';
                        langInput.value = currentLanguage || 'en';
                        form.appendChild(langInput);
                    }
                }
            });
            
            // Update any translatable elements in new content
            updatePageText();
        }
        return html;
    })
    .catch(error => {
        console.error('Error loading content:', error);
        showToast('Error loading content', 'error');
        throw error;
    });
}

// Language persistence for browser navigation
function initializeNavigationLanguageSupport() {
    // Update all links to include language parameter
    document.addEventListener('click', function(event) {
        const link = event.target.closest('a');
        if (link && !link.hasAttribute('data-no-lang') && link.href && !link.href.includes('language=')) {
            const url = new URL(link.href);
            url.searchParams.set('language', currentLanguage || 'en');
            link.href = url.toString();
        }
    });
    
    // Handle back/forward navigation
    window.addEventListener('popstate', function(event) {
        // Ensure language consistency when navigating back/forward
        const urlParams = new URLSearchParams(window.location.search);
        const urlLanguage = urlParams.get('language');
        if (urlLanguage && urlLanguage !== currentLanguage) {
            switchLanguage(urlLanguage);
        }
    });
}

// Update page text based on current language
function updatePageText() {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translations[currentLanguage][key];
            } else {
                element.textContent = translations[currentLanguage][key];
            }
        }
    });
    
    // Update placeholders
    const placeholderElements = document.querySelectorAll('[data-translate-placeholder]');
    placeholderElements.forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            element.placeholder = translations[currentLanguage][key];
        }
    });
}

// Geolocation utilities
class LocationService {
    constructor() {
        this.watchId = null;
        this.lastKnownPosition = null;
    }
    
    // Get current position
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported by this browser'));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.lastKnownPosition = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date()
                    };
                    resolve(this.lastKnownPosition);
                },
                (error) => {
                    reject(this.getLocationError(error));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 minutes
                }
            );
        });
    }
    
    // Watch position changes
    watchPosition(callback, errorCallback) {
        if (!navigator.geolocation) {
            errorCallback(new Error('Geolocation is not supported'));
            return;
        }
        
        this.watchId = navigator.geolocation.watchPosition(
            (position) => {
                this.lastKnownPosition = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date()
                };
                callback(this.lastKnownPosition);
            },
            (error) => {
                errorCallback(this.getLocationError(error));
            },
            {
                enableHighAccuracy: true,
                timeout: 30000,
                maximumAge: 60000 // 1 minute
            }
        );
    }
    
    // Stop watching position
    stopWatching() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }
    
    // Get human-readable error message
    getLocationError(error) {
        switch(error.code) {
            case error.PERMISSION_DENIED:
                return new Error(translations[currentLanguage].location_permission_denied || 
                    "Location access denied. Please enable location permissions.");
            case error.POSITION_UNAVAILABLE:
                return new Error(translations[currentLanguage].location_unavailable || 
                    "Location information is unavailable.");
            case error.TIMEOUT:
                return new Error(translations[currentLanguage].location_timeout || 
                    "Location request timed out.");
            default:
                return new Error(translations[currentLanguage].location_unknown_error || 
                    "An unknown error occurred while retrieving location.");
        }
    }
    
    // Calculate distance between two points (in meters)
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Earth's radius in meters
        const φ1 = lat1 * Math.PI/180;
        const φ2 = lat2 * Math.PI/180;
        const Δφ = (lat2-lat1) * Math.PI/180;
        const Δλ = (lon2-lon1) * Math.PI/180;

        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                Math.cos(φ1) * Math.cos(φ2) *
                Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        return R * c;
    }
}

// Notification system
class NotificationService {
    constructor() {
        this.requestPermission();
    }
    
    async requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    }
    
    show(title, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(title, {
                icon: '/static/icon-192.png',
                badge: '/static/icon-72.png',
                ...options
            });
            
            // Auto close after 5 seconds
            setTimeout(() => notification.close(), 5000);
            
            return notification;
        } else {
            // Fallback to in-page notification
            this.showInPageNotification(title, options.body);
        }
    }
    
    showInPageNotification(title, body) {
        const notification = document.createElement('div');
        notification.className = 'in-page-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <strong>${title}</strong>
                ${body ? `<p>${body}</p>` : ''}
                <button onclick="this.parentElement.parentElement.remove()" class="close-btn">×</button>
            </div>
        `;
        
        // Add CSS if not already added
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .in-page-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    z-index: 1000;
                    max-width: 300px;
                }
                .notification-content {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                .notification-content .close-btn {
                    align-self: flex-end;
                    background: none;
                    border: none;
                    font-size: 1.2rem;
                    cursor: pointer;
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// API utilities
class ApiService {
    constructor() {
        this.baseUrl = '';
    }
    
    async request(endpoint, options = {}) {
        const url = this.baseUrl + endpoint;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    get(endpoint, options = {}) {
        return this.request(endpoint, { method: 'GET', ...options });
    }
    
    post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }
    
    put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }
    
    delete(endpoint, options = {}) {
        return this.request(endpoint, { method: 'DELETE', ...options });
    }
}

// Form validation utilities
class FormValidator {
    constructor() {
        this.rules = {
            required: (value) => value.trim() !== '',
            email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            phone: (value) => /^[\+]?[0-9\s\-\(\)]{10,}$/.test(value),
            aadhaar: (value) => /^[0-9]{12}$/.test(value.replace(/\s/g, '')),
            passport: (value) => /^[A-Z]{1}[0-9]{7}$/.test(value)
        };
    }
    
    validate(form) {
        const errors = {};
        const formData = new FormData(form);
        
        // Check required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            const value = formData.get(field.name) || '';
            if (!this.rules.required(value)) {
                errors[field.name] = translations[currentLanguage].field_required || 'This field is required';
            }
        });
        
        // Validate specific field types
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            const value = formData.get(field.name) || '';
            if (value && !this.rules.email(value)) {
                errors[field.name] = translations[currentLanguage].invalid_email || 'Please enter a valid email';
            }
        });
        
        const phoneFields = form.querySelectorAll('input[type="tel"]');
        phoneFields.forEach(field => {
            const value = formData.get(field.name) || '';
            if (value && !this.rules.phone(value)) {
                errors[field.name] = translations[currentLanguage].invalid_phone || 'Please enter a valid phone number';
            }
        });
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    }
    
    showErrors(form, errors) {
        // Clear previous errors
        form.querySelectorAll('.error-message').forEach(el => el.remove());
        form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        
        // Show new errors
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('error');
                
                const errorMessage = document.createElement('div');
                errorMessage.className = 'error-message';
                errorMessage.textContent = errors[fieldName];
                errorMessage.style.color = '#c53030';
                errorMessage.style.fontSize = '0.9rem';
                errorMessage.style.marginTop = '5px';
                
                field.parentElement.appendChild(errorMessage);
            }
        });
    }
}

// Storage utilities
class StorageService {
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error storing data:', error);
        }
    }
    
    static get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (error) {
            console.error('Error retrieving data:', error);
            return defaultValue;
        }
    }
    
    static remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing data:', error);
        }
    }
    
    static clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Error clearing storage:', error);
        }
    }
}

// Initialize global services
const locationService = new LocationService();
const notificationService = new NotificationService();
const apiService = new ApiService();
const formValidator = new FormValidator();

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load translations; initializeLanguage inside will read session/local preference.
    loadTranslations();
    
    // Initialize form validation for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const validation = formValidator.validate(form);
            if (!validation.isValid) {
                e.preventDefault();
                formValidator.showErrors(form, validation.errors);
            }
        });
    });
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString(currentLanguage === 'hi' ? 'hi-IN' : 'en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatCoordinates(lat, lng) {
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other scripts
window.TouristSafety = {
    locationService,
    notificationService,
    apiService,
    formValidator,
    StorageService,
    switchLanguage,
    formatDate,
    formatCoordinates,
    generateId,
    debounce
};