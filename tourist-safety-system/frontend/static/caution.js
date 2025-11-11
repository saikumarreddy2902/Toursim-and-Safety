/**
 * User Caution System for Tourist Safety Application
 * Provides comprehensive warnings and guidance for language and data entry
 */

class UserCautionSystem {
    constructor() {
        this.activeWarnings = new Set();
        this.cautionSettings = {
            showLanguageWarnings: true,
            showDataEntryWarnings: true,
            showTranslationAccuracyWarnings: true,
            autoHideTimeout: 15000 // 15 seconds
        };
        
        this.cautionTemplates = {
            languageSwitch: {
                title: '⚠️ Language Change Warning',
                type: 'warning',
                priority: 'high'
            },
            dataEntry: {
                title: '📝 Data Entry Guidance',
                type: 'info',
                priority: 'medium'
            },
            translationAccuracy: {
                title: '🔍 Translation Accuracy Notice',
                type: 'caution',
                priority: 'high'
            },
            emergencyInfo: {
                title: '🚨 Emergency Information',
                type: 'error',
                priority: 'critical'
            },
            privacySecurity: {
                title: '🔒 Privacy & Security Notice',
                type: 'info',
                priority: 'high'
            }
        };
        
        this.init();
    }
    
    init() {
        this.createCautionContainer();
        this.setupEventListeners();
        this.showInitialGuidance();
    }
    
    createCautionContainer() {
        if (document.getElementById('cautionSystem')) return;
        
        const container = document.createElement('div');
        container.id = 'cautionSystem';
        container.className = 'caution-system-container';
        
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            width: 350px;
            max-height: 80vh;
            overflow-y: auto;
            z-index: 9999;
            pointer-events: none;
        `;
        
        document.body.appendChild(container);
    }
    
    setupEventListeners() {
        // Language change warnings
        const languageSelectors = document.querySelectorAll('select[name="language"], #languageSelect, #language-select');
        languageSelectors.forEach(selector => {
            selector.addEventListener('change', (e) => {
                this.showLanguageChangeWarning(e.target.value);
            });
        });
        
        // Form input warnings
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            this.setupFormCautions(form);
        });
        
        // Emergency contact warnings
        const emergencyButtons = document.querySelectorAll('[onclick*="emergency"], [onclick*="panic"]');
        emergencyButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.showEmergencyGuidance();
            });
        });
    }
    
    setupFormCautions(form) {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
        
        inputs.forEach(input => {
            // First focus warning
            let hasShownFirstWarning = false;
            
            input.addEventListener('focus', () => {
                if (!hasShownFirstWarning) {
                    this.showDataEntryGuidance(input);
                    hasShownFirstWarning = true;
                }
            });
            
            // Character input warnings for non-English languages
            input.addEventListener('input', (e) => {
                this.checkInputLanguage(e.target);
            });
            
            // Validation warnings
            input.addEventListener('blur', (e) => {
                this.validateInputAndWarn(e.target);
            });
        });
    }
    
    showLanguageChangeWarning(newLanguage) {
        if (!this.cautionSettings.showLanguageWarnings) return;
        
        const currentLang = localStorage.getItem('preferred_language') || 'en';
        if (newLanguage === currentLang) return;
        
        const message = {
            title: this.cautionTemplates.languageSwitch.title,
            content: `
                <div class="caution-content">
                    <p><strong>You are changing the language to ${this.getLanguageName(newLanguage)}.</strong></p>
                    <ul class="caution-list">
                        <li>🔄 All interface text will be translated</li>
                        <li>📝 Any data you've entered will be automatically translated</li>
                        <li>⚠️ Please review translations for accuracy</li>
                        <li>🔍 Important information may need manual verification</li>
                    </ul>
                    <div class="caution-actions">
                        <button onclick="cautionSystem.confirmLanguageChange('${newLanguage}')" class="btn-confirm">
                            Continue with ${this.getLanguageName(newLanguage)}
                        </button>
                        <button onclick="cautionSystem.cancelLanguageChange('${currentLang}')" class="btn-cancel">
                            Keep ${this.getLanguageName(currentLang)}
                        </button>
                    </div>
                </div>
            `,
            type: 'warning',
            persistent: true
        };
        
        this.showCaution('languageChange', message);
    }
    
    showDataEntryGuidance(input) {
        if (!this.cautionSettings.showDataEntryWarnings) return;
        
        const fieldName = input.name || input.id || 'this field';
        const fieldType = this.getFieldType(input);
        
        const message = {
            title: this.cautionTemplates.dataEntry.title,
            content: `
                <div class="caution-content">
                    <p><strong>Entering ${fieldType}: ${fieldName}</strong></p>
                    <ul class="caution-list">
                        <li>📝 Enter information in your preferred language</li>
                        <li>🌐 Text will be automatically translated if needed</li>
                        <li>✅ Ensure accuracy of important details</li>
                        <li>🔒 Your data is encrypted for security</li>
                    </ul>
                    ${this.getFieldSpecificGuidance(fieldType)}
                </div>
            `,
            type: 'info',
            timeout: 8000
        };
        
        this.showCaution(`dataEntry_${fieldName}`, message);
    }
    
    checkInputLanguage(input) {
        const text = input.value;
        if (text.length < 3) return;
        
        // Detect script type
        const hasDevanagari = /[\u0900-\u097F]/.test(text);
        const hasTamil = /[\u0B80-\u0BFF]/.test(text);
        const hasTelugu = /[\u0C00-\u0C7F]/.test(text);
        const hasBengali = /[\u0980-\u09FF]/.test(text);
        
        if (hasDevanagari || hasTamil || hasTelugu || hasBengali) {
            this.showTranslationAccuracyWarning(input);
        }
    }
    
    showTranslationAccuracyWarning(input) {
        if (!this.cautionSettings.showTranslationAccuracyWarnings) return;
        
        const warningId = `translation_${input.name || input.id}`;
        if (this.activeWarnings.has(warningId)) return;
        
        const message = {
            title: this.cautionTemplates.translationAccuracy.title,
            content: `
                <div class="caution-content">
                    <p><strong>Multi-language input detected</strong></p>
                    <ul class="caution-list">
                        <li>🔍 Please verify translation accuracy</li>
                        <li>📝 Important details may need manual review</li>
                        <li>✨ Use consistent language for better results</li>
                        <li>🆘 For emergencies, use simple, clear language</li>
                    </ul>
                </div>
            `,
            type: 'caution',
            timeout: 10000
        };
        
        this.showCaution(warningId, message);
    }
    
    showEmergencyGuidance() {
        const message = {
            title: this.cautionTemplates.emergencyInfo.title,
            content: `
                <div class="caution-content">
                    <p><strong>Emergency Procedures</strong></p>
                    <ul class="caution-list">
                        <li>🚨 Emergency services have been notified</li>
                        <li>📍 Your location is being shared</li>
                        <li>📞 Stay on the line if contacted</li>
                        <li>🔒 Your safety information is secure</li>
                        <li>👮 Local authorities will assist you</li>
                    </ul>
                    <div class="emergency-contacts">
                        <p><strong>Indian Emergency Numbers:</strong></p>
                        <p>🚓 Police: 100 | 🚑 Ambulance: 108 | 🔥 Fire: 101</p>
                    </div>
                </div>
            `,
            type: 'error',
            persistent: true
        };
        
        this.showCaution('emergencyGuidance', message);
    }
    
    showPrivacySecurityNotice() {
        const message = {
            title: this.cautionTemplates.privacySecurity.title,
            content: `
                <div class="caution-content">
                    <p><strong>Your Privacy & Security</strong></p>
                    <ul class="caution-list">
                        <li>🔒 All data is encrypted using government-grade security</li>
                        <li>🛡️ Information is stored securely on blockchain</li>
                        <li>👤 Access limited to authorized personnel only</li>
                        <li>🌐 Translation data is processed securely</li>
                        <li>❌ No data is stored by translation services</li>
                    </ul>
                </div>
            `,
            type: 'info',
            timeout: 12000
        };
        
        this.showCaution('privacySecurity', message);
    }
    
    showInitialGuidance() {
        setTimeout(() => {
            const welcomeMessage = {
                title: '👋 Welcome to Tourist Safety System',
                content: `
                    <div class="caution-content">
                        <p><strong>Getting Started</strong></p>
                        <ul class="caution-list">
                            <li>🌐 Select your preferred language from the dropdown</li>
                            <li>📝 Enter your details in any supported language</li>
                            <li>🔄 Information will be automatically translated</li>
                            <li>🔒 Your data is protected with advanced encryption</li>
                            <li>🆘 Emergency services are available 24/7</li>
                        </ul>
                        <p class="caution-footer">System is ready for use!</p>
                    </div>
                `,
                type: 'info',
                timeout: 15000
            };
            
            this.showCaution('welcome', welcomeMessage);
        }, 2000);
    }
    
    showCaution(id, message) {
        if (this.activeWarnings.has(id)) return;
        
        this.activeWarnings.add(id);
        
        const cautionElement = document.createElement('div');
        cautionElement.className = `caution-alert caution-${message.type}`;
        cautionElement.id = `caution_${id}`;
        
        cautionElement.style.cssText = `
            background: white;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            pointer-events: auto;
            animation: slideInRight 0.3s ease;
            border-left: 4px solid ${this.getTypeColor(message.type)};
        `;
        
        cautionElement.innerHTML = `
            <div class="caution-header" style="
                padding: 12px 15px 8px 15px;
                border-bottom: 1px solid #f0f0f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <h4 style="margin: 0; color: ${this.getTypeColor(message.type)}; font-size: 0.9em;">
                    ${message.title}
                </h4>
                <button onclick="cautionSystem.dismissCaution('${id}')" style="
                    background: none;
                    border: none;
                    font-size: 1.2em;
                    cursor: pointer;
                    color: #999;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                ">×</button>
            </div>
            <div class="caution-body" style="padding: 10px 15px 15px 15px; font-size: 0.85em;">
                ${message.content}
            </div>
        `;
        
        const container = document.getElementById('cautionSystem');
        container.appendChild(cautionElement);
        
        // Auto-dismiss if not persistent
        if (!message.persistent && message.timeout) {
            setTimeout(() => {
                this.dismissCaution(id);
            }, message.timeout);
        }
    }
    
    dismissCaution(id) {
        const element = document.getElementById(`caution_${id}`);
        if (element) {
            element.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (element.parentNode) {
                    element.remove();
                }
                this.activeWarnings.delete(id);
            }, 300);
        }
    }
    
    confirmLanguageChange(newLanguage) {
        localStorage.setItem('preferred_language', newLanguage);
        this.dismissCaution('languageChange');
        
        // Show confirmation
        const confirmMessage = {
            title: '✅ Language Changed',
            content: `<p>Interface language changed to ${this.getLanguageName(newLanguage)}</p>`,
            type: 'info',
            timeout: 3000
        };
        this.showCaution('languageConfirm', confirmMessage);
    }
    
    cancelLanguageChange(oldLanguage) {
        // Revert language selector
        const selectors = document.querySelectorAll('select[name="language"], #languageSelect, #language-select');
        selectors.forEach(selector => {
            selector.value = oldLanguage;
        });
        this.dismissCaution('languageChange');
    }
    
    getFieldType(input) {
        const type = input.type.toLowerCase();
        const name = (input.name || input.id || '').toLowerCase();
        
        if (type === 'email') return 'email address';
        if (name.includes('phone')) return 'phone number';
        if (name.includes('name')) return 'name';
        if (name.includes('address')) return 'address';
        if (name.includes('medical')) return 'medical information';
        if (name.includes('emergency')) return 'emergency contact';
        if (name.includes('passport')) return 'passport details';
        
        return 'information';
    }
    
    getFieldSpecificGuidance(fieldType) {
        const guidance = {
            'email address': '<p class="field-tip">💡 Use your primary email for important notifications</p>',
            'phone number': '<p class="field-tip">💡 Include country code for international numbers</p>',
            'medical information': '<p class="field-tip">⚕️ Include allergies, medications, and conditions</p>',
            'emergency contact': '<p class="field-tip">📞 Provide local and home country contacts</p>',
            'passport details': '<p class="field-tip">📄 Ensure passport is valid for your entire stay</p>',
            'address': '<p class="field-tip">📍 Include local accommodation details</p>'
        };
        
        return guidance[fieldType] || '<p class="field-tip">💡 Provide accurate information for your safety</p>';
    }
    
    getTypeColor(type) {
        const colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'caution': '#fd7e14'
        };
        return colors[type] || '#6c757d';
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
    
    // Public methods for external use
    showCustomCaution(id, title, content, type = 'info', timeout = 8000) {
        const message = { title, content, type, timeout };
        this.showCaution(id, message);
    }
    
    dismissAllCautions() {
        this.activeWarnings.forEach(id => this.dismissCaution(id));
    }
    
    toggleCautionSetting(setting, value) {
        if (this.cautionSettings.hasOwnProperty(setting)) {
            this.cautionSettings[setting] = value;
            localStorage.setItem('cautionSettings', JSON.stringify(this.cautionSettings));
        }
    }
}

// Initialize caution system when DOM is loaded
let cautionSystem;

document.addEventListener('DOMContentLoaded', function() {
    cautionSystem = new UserCautionSystem();
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { 
                transform: translateX(100%);
                opacity: 0;
            }
            to { 
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from { 
                transform: translateX(0);
                opacity: 1;
            }
            to { 
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .caution-list {
            margin: 10px 0;
            padding-left: 15px;
        }
        
        .caution-list li {
            margin-bottom: 5px;
            line-height: 1.4;
        }
        
        .caution-actions {
            margin-top: 15px;
            display: flex;
            gap: 8px;
        }
        
        .caution-actions button {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .btn-confirm {
            background: #28a745;
            color: white;
        }
        
        .btn-cancel {
            background: #6c757d;
            color: white;
        }
        
        .field-tip {
            margin-top: 8px;
            padding: 6px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.8em;
            color: #495057;
        }
        
        .caution-footer {
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            font-weight: 500;
            color: #28a745;
        }
        
        .emergency-contacts {
            margin-top: 12px;
            padding: 8px;
            background: #ffe6e6;
            border-radius: 4px;
            border: 1px solid #ffb3b3;
        }
        
        .emergency-contacts p {
            margin: 2px 0;
            font-size: 0.85em;
        }
    `;
    document.head.appendChild(style);
});

// Global functions for external use
function showUserCaution(id, title, content, type = 'info') {
    if (cautionSystem) {
        cautionSystem.showCustomCaution(id, title, content, type);
    }
}

function dismissUserCaution(id) {
    if (cautionSystem) {
        cautionSystem.dismissCaution(id);
    }
}