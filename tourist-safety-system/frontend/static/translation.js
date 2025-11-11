/**
 * Google Translate Integration for Tourist Safety System
 * Provides real-time translation of form data and user content
 */

class TranslationManager {
    constructor() {
        // Initialize language from global manager, sessionStorage, cookie or default to English
        const getCookie = (name) => {
            const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
            return match ? decodeURIComponent(match[2]) : null;
        };
        this.currentLanguage = (window.globalTranslationManager && window.globalTranslationManager.currentLanguage)
            || sessionStorage.getItem('selectedLanguage')
            || getCookie('language')
            || 'en';
        this.originalFormData = {};
        this.translationCache = new Map();
        this.isTranslationEnabled = false;
        this.warningShown = false;
        
        this.init();
    }
    
    async init() {
        // Check translation service status
        try {
            const response = await fetch('/api/translate/status');
            const data = await response.json();
            this.isTranslationEnabled = data.translation_enabled;
            if (!sessionStorage.getItem('selectedLanguage') && data && data.current_language) {
                sessionStorage.setItem('selectedLanguage', data.current_language);
                this.currentLanguage = data.current_language;
            }
            
            if (this.isTranslationEnabled) {
                console.log('✅ Translation service initialized');
                this.setupFormTranslation();
                this.setupLanguageChangeHandlers();
            } else {
                console.log('⚠️ Translation service not available');
            }
        } catch (error) {
            console.error('Translation service initialization failed:', error);
        }
    }
    
    setupFormTranslation() {
        // Monitor form inputs for real-time translation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            this.setupFormMonitoring(form);
        });
    }
    
    setupFormMonitoring(form) {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
        
        inputs.forEach(input => {
            // Store original values
            if (input.value) {
                this.originalFormData[input.name || input.id] = input.value;
            }
            
            // Add translation indicator
            this.addTranslationIndicator(input);
            
            // Monitor changes
            input.addEventListener('input', (e) => {
                this.handleInputChange(e.target);
            });
            
            input.addEventListener('blur', (e) => {
                this.handleInputBlur(e.target);
            });
        });
    }
    
    addTranslationIndicator(input) {
        const container = input.parentElement;
        const indicator = document.createElement('div');
        indicator.className = 'translation-indicator';
        indicator.innerHTML = `
            <span class="translation-status" data-status="original">
                🌐 <span class="status-text">Original</span>
            </span>
        `;
        container.appendChild(indicator);
    }
    
    updateTranslationIndicator(input, status, sourceLang = '', targetLang = '') {
        const indicator = input.parentElement.querySelector('.translation-indicator .translation-status');
        if (!indicator) return;
        
        const statusText = indicator.querySelector('.status-text');
        
        switch (status) {
            case 'translating':
                indicator.dataset.status = 'translating';
                indicator.innerHTML = '🔄 <span class="status-text">Translating...</span>';
                break;
            case 'translated':
                indicator.dataset.status = 'translated';
                indicator.innerHTML = `🌍 <span class="status-text">Translated (${sourceLang} → ${targetLang})</span>`;
                break;
            case 'error':
                indicator.dataset.status = 'error';
                indicator.innerHTML = '❌ <span class="status-text">Translation failed</span>';
                break;
            default:
                indicator.dataset.status = 'original';
                indicator.innerHTML = '🌐 <span class="status-text">Original</span>';
        }
    }
    
    setupLanguageChangeHandlers() {
        // Monitor language selector changes
        const languageSelectors = document.querySelectorAll('select[name="language"], #languageSelect, #language-select, .language-selector');
        
        languageSelectors.forEach(selector => {
            selector.addEventListener('change', (e) => {
                this.handleLanguageChange(e.target.value);
            });
        });
    }
    
    async handleLanguageChange(newLanguage) {
        if (!this.isTranslationEnabled) return;
        
        const oldLanguage = this.currentLanguage;
        this.currentLanguage = newLanguage;

        // Persist on backend as well to keep session consistent
        try {
            await fetch('/api/set_language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: newLanguage })
            });
            sessionStorage.setItem('selectedLanguage', newLanguage);
        } catch (_) {}
        
        // Show warning if user has entered data
        if (this.hasUserEnteredData() && !this.warningShown) {
            this.showLanguageChangeWarning(oldLanguage, newLanguage);
        }
        
        // Translate existing form data
        await this.translateAllFormData(oldLanguage, newLanguage);
    }
    
    hasUserEnteredData() {
        const forms = document.querySelectorAll('form');
        for (const form of forms) {
            const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
            for (const input of inputs) {
                if (input.value.trim()) {
                    return true;
                }
            }
        }
        return false;
    }
    
    showLanguageChangeWarning(oldLang, newLang) {
        const warning = document.createElement('div');
        warning.className = 'translation-warning';
        warning.innerHTML = `
            <div class="warning-content">
                <h4>⚠️ Language Change Detected</h4>
                <p>You are changing from <strong>${this.getLanguageName(oldLang)}</strong> to <strong>${this.getLanguageName(newLang)}</strong>.</p>
                <p>Your entered data will be automatically translated. Please review the translations for accuracy.</p>
                <div class="warning-actions">
                    <button onclick="translationManager.dismissWarning()" class="btn-primary">I Understand</button>
                    <button onclick="translationManager.revertLanguage('${oldLang}')" class="btn-secondary">Keep Original Language</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(warning);
        this.warningShown = true;
        
        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            this.dismissWarning();
        }, 10000);
    }
    
    dismissWarning() {
        const warning = document.querySelector('.translation-warning');
        if (warning) {
            warning.remove();
        }
    }
    
    revertLanguage(oldLang) {
        this.currentLanguage = oldLang;
        const selectors = document.querySelectorAll('select[name="language"], #languageSelect');
        selectors.forEach(selector => {
            if (selector) {
                selector.value = oldLang;
            }
        });
        this.dismissWarning();
    }
    
    async handleInputChange(input) {
        if (!this.isTranslationEnabled) return;
        
        // Store original value if not already stored
        if (!this.originalFormData[input.name || input.id]) {
            this.originalFormData[input.name || input.id] = input.value;
        }
    }
    
    async handleInputBlur(input) {
        if (!this.isTranslationEnabled || !input.value.trim()) return;
        
        // Auto-translate if current language is not English
        if (this.currentLanguage !== 'en') {
            await this.translateInput(input, 'auto', this.currentLanguage);
        }
    }
    
    async translateInput(input, sourceLang = 'auto', targetLang = this.currentLanguage) {
        if (!input.value.trim()) return;
        
        const cacheKey = `${input.value}-${sourceLang}-${targetLang}`;
        
        // Check cache first
        if (this.translationCache.has(cacheKey)) {
            const cached = this.translationCache.get(cacheKey);
            input.value = cached.translated_text;
            this.updateTranslationIndicator(input, 'translated', cached.source_language, targetLang);
            return;
        }
        
        this.updateTranslationIndicator(input, 'translating');
        
        try {
            const response = await fetch('/api/translate/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: input.value,
                    source_lang: sourceLang,
                    target_lang: targetLang
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                input.value = result.translated_text;
                this.translationCache.set(cacheKey, result);
                this.updateTranslationIndicator(input, 'translated', result.source_language, targetLang);
            } else {
                this.updateTranslationIndicator(input, 'error');
                console.error('Translation failed:', result.error);
            }
        } catch (error) {
            this.updateTranslationIndicator(input, 'error');
            console.error('Translation request failed:', error);
        }
    }
    
    async translateAllFormData(sourceLang, targetLang) {
        const forms = document.querySelectorAll('form');
        
        for (const form of forms) {
            const formData = this.collectFormData(form);
            if (Object.keys(formData).length === 0) continue;
            
            try {
                const response = await fetch('/api/translate/form', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        form_data: formData,
                        source_lang: sourceLang,
                        target_lang: targetLang
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.applyTranslatedFormData(form, result.translated_data);
                    this.updateFormTranslationIndicators(form, 'translated', sourceLang, targetLang);
                } else {
                    this.updateFormTranslationIndicators(form, 'error');
                    console.error('Form translation failed:', result.error);
                }
            } catch (error) {
                this.updateFormTranslationIndicators(form, 'error');
                console.error('Form translation request failed:', error);
            }
        }
    }
    
    collectFormData(form) {
        const formData = {};
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
        
        inputs.forEach(input => {
            if (input.value.trim()) {
                formData[input.name || input.id] = input.value;
            }
        });
        
        return formData;
    }
    
    applyTranslatedFormData(form, translatedData) {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
        
        inputs.forEach(input => {
            const fieldName = input.name || input.id;
            if (translatedData[fieldName]) {
                input.value = translatedData[fieldName];
            }
        });
    }
    
    updateFormTranslationIndicators(form, status, sourceLang = '', targetLang = '') {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
        inputs.forEach(input => {
            this.updateTranslationIndicator(input, status, sourceLang, targetLang);
        });
    }
    
    getLanguageName(code) {
        const languages = {
            'en': 'English',
            'hi': 'हिंदी (Hindi)',
            'ta': 'தமிழ் (Tamil)',
            'te': 'తెలుగు (Telugu)',
            'bn': 'বাংলা (Bengali)',
            'mr': 'मराठी (Marathi)',
            'gu': 'ગુજરાતી (Gujarati)',
            'kn': 'ಕನ್ನಡ (Kannada)',
            'ml': 'മലയാളം (Malayalam)',
            'pa': 'ਪੰਜਾਬੀ (Punjabi)',
            'or': 'ଓଡ଼ିଆ (Odia)',
            'as': 'অসমীয়া (Assamese)'
        };
        return languages[code] || code;
    }
    
    // Utility method to manually translate text
    async translateText(text, sourceLang = 'auto', targetLang = this.currentLanguage) {
        try {
            const response = await fetch('/api/translate/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    source_lang: sourceLang,
                    target_lang: targetLang
                })
            });
            
            const result = await response.json();
            return result.success ? result.translated_text : text;
        } catch (error) {
            console.error('Translation failed:', error);
            return text;
        }
    }
    
    // Reset all translations to original values
    resetToOriginal() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
            inputs.forEach(input => {
                const fieldName = input.name || input.id;
                if (this.originalFormData[fieldName]) {
                    input.value = this.originalFormData[fieldName];
                    this.updateTranslationIndicator(input, 'original');
                }
            });
        });
    }
}

// Initialize translation manager when DOM is loaded
let translationManager;

document.addEventListener('DOMContentLoaded', function() {
    translationManager = new TranslationManager();
});

// Global function for manual translation
async function translateUserText(text, targetLang = null) {
    if (!translationManager || !translationManager.isTranslationEnabled) {
        return text;
    }
    
    return await translationManager.translateText(text, 'auto', targetLang || translationManager.currentLanguage);
}