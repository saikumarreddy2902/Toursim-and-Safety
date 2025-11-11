// App Download Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeDownloadPage();
    generateQRCodes();
    setupInstructionTabs();
    setupPWAInstall();
    trackDownloads();
});

// Initialize download page
function initializeDownloadPage() {
    console.log('Tourist Safety App Download Page Initialized');
    
    // Animate elements on scroll
    observeElements();
    
    // Add click animations to buttons
    addButtonAnimations();
    
    // Check device type and highlight appropriate download option
    detectDeviceAndHighlight();
}

// Generate QR codes for different platforms
function generateQRCodes() {
    const qrCodes = {
        android: 'https://play.google.com/store/apps/details?id=com.tourist.safety',
        ios: 'https://apps.apple.com/app/tourist-safety/id123456789',
        web: window.location.origin + '/app'
    };
    
    // Generate QR codes for each platform
    Object.keys(qrCodes).forEach(platform => {
        generateQRCode(platform, qrCodes[platform]);
    });
}

// Generate individual QR code
function generateQRCode(platform, url) {
    const qrElement = document.querySelector(`.${platform}-card .qr-code`);
    if (!qrElement) return;
    
    // Simple QR code pattern simulation (in real app, use QR code library)
    const qrPattern = createQRPattern(url);
    
    // Replace placeholder with generated pattern
    qrElement.innerHTML = `
        <div class="generated-qr" data-url="${url}">
            ${qrPattern}
        </div>
    `;
    
    // Add click event to copy URL
    qrElement.addEventListener('click', () => copyToClipboard(url));
}

// Create QR pattern (simplified visual representation)
function createQRPattern(url) {
    const size = 120;
    const cellSize = 4;
    const cells = size / cellSize;
    
    let pattern = '<svg width="120" height="120" viewBox="0 0 120 120">';
    
    // Generate pseudo-random pattern based on URL
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
        hash = ((hash << 5) - hash + url.charCodeAt(i)) & 0xffffffff;
    }
    
    // Create pattern
    for (let y = 0; y < cells; y++) {
        for (let x = 0; x < cells; x++) {
            const random = Math.abs(hash * (x + y * cells)) % 100;
            if (random > 50) {
                pattern += `<rect x="${x * cellSize}" y="${y * cellSize}" width="${cellSize}" height="${cellSize}" fill="#000"/>`;
            }
        }
    }
    
    // Add finder patterns (corners)
    pattern += `
        <rect x="0" y="0" width="28" height="28" fill="#000"/>
        <rect x="4" y="4" width="20" height="20" fill="#fff"/>
        <rect x="8" y="8" width="12" height="12" fill="#000"/>
        
        <rect x="92" y="0" width="28" height="28" fill="#000"/>
        <rect x="96" y="4" width="20" height="20" fill="#fff"/>
        <rect x="100" y="8" width="12" height="12" fill="#000"/>
        
        <rect x="0" y="92" width="28" height="28" fill="#000"/>
        <rect x="4" y="96" width="20" height="20" fill="#fff"/>
        <rect x="8" y="100" width="12" height="12" fill="#000"/>
    `;
    
    pattern += '</svg>';
    return pattern;
}

// Setup instruction tabs functionality
function setupInstructionTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.instruction-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.tab;
            
            // Remove active class from all tabs and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            panels.forEach(panel => panel.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding panel
            button.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
}

// Progressive Web App installation
function setupPWAInstall() {
    let deferredPrompt;
    
    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        
        // Show PWA install button
        showPWAInstallButton();
    });
    
    // Handle PWA install button click
    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('pwa-btn')) {
            e.preventDefault();
            
            if (deferredPrompt) {
                // Show the install prompt
                deferredPrompt.prompt();
                
                // Wait for the user to respond to the prompt
                const { outcome } = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                    trackEvent('pwa_install', 'accepted');
                } else {
                    console.log('User dismissed the install prompt');
                    trackEvent('pwa_install', 'dismissed');
                }
                
                // Clear the deferredPrompt
                deferredPrompt = null;
            } else {
                // Fallback for browsers that don't support PWA installation
                showPWAInstructions();
            }
        }
    });
}

// Show PWA install button
function showPWAInstallButton() {
    const pwaButtons = document.querySelectorAll('.pwa-btn');
    pwaButtons.forEach(button => {
        button.style.display = 'flex';
        button.innerHTML = '<i class="fas fa-download"></i> Install App';
    });
}

// Show PWA manual installation instructions
function showPWAInstructions() {
    const modal = document.createElement('div');
    modal.className = 'pwa-modal';
    modal.innerHTML = `
        <div class="pwa-modal-content">
            <h3>Install Tourist Safety App</h3>
            <div class="pwa-instructions">
                <h4>Chrome (Android/Desktop):</h4>
                <ol>
                    <li>Click the menu button (⋮)</li>
                    <li>Select "Add to Home screen" or "Install app"</li>
                    <li>Follow the prompts to install</li>
                </ol>
                
                <h4>Safari (iOS):</h4>
                <ol>
                    <li>Tap the share button (⬆)</li>
                    <li>Scroll down and tap "Add to Home Screen"</li>
                    <li>Tap "Add" to confirm</li>
                </ol>
            </div>
            <button class="close-modal">Got it!</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal
    modal.querySelector('.close-modal').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Detect device type and highlight appropriate download
function detectDeviceAndHighlight() {
    const userAgent = navigator.userAgent;
    let recommendedCard = null;
    
    if (/Android/i.test(userAgent)) {
        recommendedCard = document.querySelector('.android-card');
    } else if (/iPhone|iPad|iPod/i.test(userAgent)) {
        recommendedCard = document.querySelector('.ios-card');
    } else {
        recommendedCard = document.querySelector('.web-card');
    }
    
    if (recommendedCard) {
        recommendedCard.classList.add('recommended');
        
        // Add recommendation badge
        const badge = document.createElement('div');
        badge.className = 'recommendation-badge';
        badge.innerHTML = '<i class="fas fa-star"></i> Recommended for your device';
        recommendedCard.insertBefore(badge, recommendedCard.firstChild);
    }
}

// Add button click animations
function addButtonAnimations() {
    const buttons = document.querySelectorAll('.download-btn, .tab-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                left: ${x}px;
                top: ${y}px;
                width: ${size}px;
                height: ${size}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Observe elements for scroll animations
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe cards and sections
    const elements = document.querySelectorAll('.download-card, .feature-card, .requirement-card, .support-item');
    elements.forEach(el => observer.observe(el));
}

// Copy URL to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Download link copied to clipboard!');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Download link copied to clipboard!');
    }
}

// Show toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 1000;
        animation: slideInUp 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutDown 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Track download events
function trackDownloads() {
    const downloadButtons = document.querySelectorAll('.download-btn');
    
    downloadButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const platform = e.target.closest('.download-card').querySelector('.platform-info h3').textContent;
            const buttonType = e.target.textContent.trim();
            
            trackEvent('download_click', {
                platform: platform,
                button_type: buttonType,
                user_agent: navigator.userAgent
            });
        });
    });
}

// Generic event tracking
function trackEvent(eventName, data = {}) {
    // In a real application, this would send data to analytics service
    console.log('Event tracked:', eventName, data);
    
    // Example: Send to Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, data);
    }
}

// Handle download redirects
function handleDownload(platform, type) {
    const downloads = {
        android: {
            store: 'https://play.google.com/store/apps/details?id=com.tourist.safety',
            direct: '/downloads/tourist-safety-android.apk'
        },
        ios: {
            store: 'https://apps.apple.com/app/tourist-safety/id123456789',
            direct: 'https://apps.apple.com/app/tourist-safety/id123456789'
        },
        web: {
            app: '/app',
            pwa: '/app'
        }
    };
    
    const url = downloads[platform]?.[type];
    if (url) {
        if (url.startsWith('http')) {
            window.open(url, '_blank');
        } else {
            window.location.href = url;
        }
        
        trackEvent('download_redirect', {
            platform: platform,
            type: type,
            url: url
        });
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutDown {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(100%);
            opacity: 0;
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease both;
    }
    
    .recommended {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.2);
    }
    
    .recommendation-badge {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin-bottom: 15px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pwa-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    }
    
    .pwa-modal-content {
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    .pwa-instructions h4 {
        color: #495057;
        margin: 20px 0 10px 0;
    }
    
    .pwa-instructions ol {
        margin-bottom: 20px;
        padding-left: 20px;
    }
    
    .pwa-instructions li {
        margin-bottom: 5px;
        color: #6c757d;
    }
    
    .close-modal {
        background: #007bff;
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        width: 100%;
        margin-top: 20px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;

document.head.appendChild(style);

// Export functions for global access
window.handleDownload = handleDownload;
window.copyToClipboard = copyToClipboard;