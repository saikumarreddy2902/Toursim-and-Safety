/**
 * Global Translation System for Tourist Safety System
 * Persists language selection across all pages until logout
 */

class GlobalTranslationManager {
    constructor() {
        this.currentLanguage = this.getStoredLanguage() || 'en';
        this.translationCache = new Map();
        this.isTranslationEnabled = false;
        this.apiKey = null;
        
        this.init();
    }
    
    async init() {
        // Check translation service status
        try {
            const response = await fetch('/api/translate/status');
            const data = await response.json();
            this.isTranslationEnabled = data.translation_enabled;
            // If no stored language, sync with backend's current session language
            try {
                const stored = this.getStoredLanguage();
                if (!stored && data && data.current_language) {
                    this.setStoredLanguage(data.current_language);
                }
            } catch (_) {}
            
            if (this.isTranslationEnabled) {
                console.log('✅ Global Translation service initialized');
                this.setupGlobalLanguageHandlers();
                
                // Apply current language if not English
                if (this.currentLanguage !== 'en') {
                    await this.translatePage(this.currentLanguage);
                }
            } else {
                console.log('⚠️ Translation service not available');
            }
        } catch (error) {
            console.error('Translation service initialization failed:', error);
        }
    }
    
    getStoredLanguage() {
        // Get language from sessionStorage (persists until logout/browser close)
        return sessionStorage.getItem('selectedLanguage');
    }
    
    setStoredLanguage(language) {
        // Store language in sessionStorage
        sessionStorage.setItem('selectedLanguage', language);
        this.currentLanguage = language;
    }
    
    clearStoredLanguage() {
        // Clear on logout
        sessionStorage.removeItem('selectedLanguage');
        this.currentLanguage = 'en';
    }
    
    setupGlobalLanguageHandlers() {
        // Monitor all language selector changes across the site
        document.addEventListener('change', (e) => {
            if (e.target.matches('#language-select, .language-selector, select[name="language"]')) {
                this.handleGlobalLanguageChange(e.target.value);
            }
        });
        
        // Set initial language selector values
        this.updateLanguageSelectors();
    }
    
    updateLanguageSelectors() {
        const selectors = document.querySelectorAll('#language-select, .language-selector, select[name="language"]');
        selectors.forEach(selector => {
            if (selector && selector.value !== this.currentLanguage) {
                selector.value = this.currentLanguage;
            }
        });
    }
    
    async handleGlobalLanguageChange(newLanguage) {
        if (!this.isTranslationEnabled) return;
        
        const oldLanguage = this.currentLanguage;
        this.setStoredLanguage(newLanguage);
        
        console.log(`🌍 Global language change: ${oldLanguage} → ${newLanguage}`);
        
        // Update all language selectors
        this.updateLanguageSelectors();
        
        // Translate the entire page
        await this.translatePage(newLanguage);
        
        // Notify backend about language change
        this.notifyBackendLanguageChange(newLanguage);
    }
    
    async translatePage(targetLang) {
        if (targetLang === 'en') {
            this.resetToOriginal();
            return;
        }
        
        // Show loading indicator
        this.showTranslationLoading(true);
        
        try {
            // Translate all elements with data-translate
            await this.translateDataElements(targetLang);
            
            // Translate dynamic text content
            await this.translateDynamicContent(targetLang);
            
            // Translate form placeholders
            await this.translateFormPlaceholders(targetLang);
            
            console.log(`✅ Page translated to ${targetLang}`);
        } catch (error) {
            console.error('Page translation failed:', error);
        } finally {
            this.showTranslationLoading(false);
        }
    }
    
    async translateDataElements(targetLang) {
        const elements = document.querySelectorAll('[data-translate]');
        const batch = [];
        
        elements.forEach(el => {
            const key = el.getAttribute('data-translate');
            const originalText = el.dataset.originalText || el.textContent.trim();
            
            // Store original text
            if (!el.dataset.originalText) {
                el.dataset.originalText = originalText;
            }
            
            if (originalText) {
                batch.push({
                    element: el,
                    text: originalText,
                    key: key
                });
            }
        });
        
        // Translate in batches for better performance
        const batchSize = 10;
        for (let i = 0; i < batch.length; i += batchSize) {
            const currentBatch = batch.slice(i, i + batchSize);
            await this.translateBatch(currentBatch, targetLang);
        }
    }
    
    async translateBatch(batch, targetLang) {
        const texts = batch.map(item => item.text);
        
        try {
            const response = await fetch('/api/translate/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    texts: texts,
                    source_lang: 'en',
                    target_lang: targetLang
                })
            });
            
            const result = await response.json();
            
            if (result.success && result.translations) {
                batch.forEach((item, index) => {
                    if (result.translations[index]) {
                        item.element.textContent = result.translations[index];
                    }
                });
            } else {
                // Fallback: translate individual texts
                for (const item of batch) {
                    await this.translateSingleElement(item.element, item.text, targetLang);
                }
            }
        } catch (error) {
            console.error('Batch translation failed, falling back to individual:', error);
            // Fallback: translate individual texts
            for (const item of batch) {
                await this.translateSingleElement(item.element, item.text, targetLang);
            }
        }
    }
    
    async translateSingleElement(element, text, targetLang) {
        const cacheKey = `${text}-en-${targetLang}`;
        
        // Check cache
        if (this.translationCache.has(cacheKey)) {
            element.textContent = this.translationCache.get(cacheKey);
            return;
        }
        
        try {
            const response = await fetch('/api/translate/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    source_lang: 'en',
                    target_lang: targetLang
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                element.textContent = result.translated_text;
                this.translationCache.set(cacheKey, result.translated_text);
            }
        } catch (error) {
            console.error('Single element translation failed:', error);
        }
    }
    
    async translateDynamicContent(targetLang) {
        // Translate common dynamic elements
        const selectors = [
            'h1, h2, h3, h4, h5, h6',
            'p:not([data-translate])',
            'button:not([data-translate])',
            'label:not([data-translate])',
            '.btn:not([data-translate])',
            '.alert:not([data-translate])'
        ];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                if (el.textContent.trim() && !el.dataset.originalText) {
                    await this.translateSingleElement(el, el.textContent.trim(), targetLang);
                }
            }
        }
    }
    
    async translateFormPlaceholders(targetLang) {
        const inputs = document.querySelectorAll('input[placeholder], textarea[placeholder]');
        
        for (const input of inputs) {
            const originalPlaceholder = input.dataset.originalPlaceholder || input.placeholder;
            
            if (!input.dataset.originalPlaceholder) {
                input.dataset.originalPlaceholder = originalPlaceholder;
            }
            
            if (targetLang === 'en') {
                input.placeholder = originalPlaceholder;
            } else {
                const translated = await this.translateText(originalPlaceholder, 'en', targetLang);
                input.placeholder = translated;
            }
        }
    }
    
    async translateText(text, sourceLang = 'en', targetLang = this.currentLanguage) {
        const cacheKey = `${text}-${sourceLang}-${targetLang}`;
        
        if (this.translationCache.has(cacheKey)) {
            return this.translationCache.get(cacheKey);
        }
        
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
            
            if (result.success) {
                this.translationCache.set(cacheKey, result.translated_text);
                return result.translated_text;
            }
        } catch (error) {
            console.error('Translation failed:', error);
        }
        
        return text; // Return original if translation fails
    }
    
    resetToOriginal() {
        // Reset all translated elements to original text
        const elements = document.querySelectorAll('[data-original-text]');
        elements.forEach(el => {
            el.textContent = el.dataset.originalText;
        });
        
        // Reset placeholders
        const inputs = document.querySelectorAll('[data-original-placeholder]');
        inputs.forEach(input => {
            input.placeholder = input.dataset.originalPlaceholder;
        });
    }
    
    showTranslationLoading(show) {
        let loader = document.getElementById('translation-loader');
        
        if (show && !loader) {
            loader = document.createElement('div');
            loader.id = 'translation-loader';
            loader.innerHTML = `
                <div style="position: fixed; top: 20px; right: 20px; background: #007bff; color: white; padding: 10px 15px; border-radius: 5px; z-index: 9999; font-size: 14px;">
                    <span>🌍 Translating page...</span>
                </div>
            `;
            document.body.appendChild(loader);
        } else if (!show && loader) {
            loader.remove();
        }
    }
    
    async notifyBackendLanguageChange(language) {
        try {
            await fetch('/api/set_language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ language: language })
            });
        } catch (error) {
            console.warn('Failed to notify backend of language change:', error);
        }
    }
    
    // Method to call on logout
    logout() {
        this.clearStoredLanguage();
        this.resetToOriginal();
        console.log('🔐 User logged out, language reset to English');
    }
}

// Initialize global translation manager
let globalTranslationManager;

document.addEventListener('DOMContentLoaded', function() {
    globalTranslationManager = new GlobalTranslationManager();
    
    // Make it globally accessible
    window.globalTranslationManager = globalTranslationManager;
});

// Global functions
window.translateToLanguage = function(language) {
    if (globalTranslationManager) {
        globalTranslationManager.handleGlobalLanguageChange(language);
    }
};

window.resetLanguage = function() {
    if (globalTranslationManager) {
        globalTranslationManager.handleGlobalLanguageChange('en');
    }
};

window.logoutAndResetLanguage = function() {
    if (globalTranslationManager) {
        globalTranslationManager.logout();
    }
};