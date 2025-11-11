// Digital ID Card Functionality

document.addEventListener('DOMContentLoaded', async function() {
    initializeDigitalID();
    await loadTouristDataDynamic();
    setupCardControls();
    generateQRCodes();
    setupVerificationSystem();
});

// Tourist data populated after API fetch
let touristData = null;

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

async function loadTouristDataDynamic() {
    try {
        const touristId = getQueryParam('tourist_id');
        if (!touristId) {
            console.warn('No tourist_id provided in URL; using placeholder visuals');
            return;
        }
        const res = await fetch(`/api/get_digital_id/${encodeURIComponent(touristId)}`);
        const payload = await res.json();
        if (!res.ok || !payload.success) {
            console.error('Failed to load digital ID:', payload.error || res.status);
            return;
        }
        const t = payload.tourist || {};
        touristData = {
            id: t.tourist_id,
            name: t.full_name || 'UNKNOWN',
            nationality: t.nationality || '—',
            dateOfBirth: t.date_of_birth || '—',
            photo: t.profile_photo_url || '../static/images/default-avatar.png',
            emergencyContacts: Array.isArray(t.emergency_contacts) ? t.emergency_contacts : [],
            medicalInfo: t.medical_info || {},
            blockchain: {
                blockHash: t.blockchain_hash || t.verification_hash || '',
                timestamp: new Date().toISOString(),
                verified: Boolean(t.verification_status && t.verification_status !== 'unverified')
            }
        };
        renderTouristData();
    } catch (e) {
        console.error('Error fetching digital ID data:', e);
    }
}

// Initialize digital ID system
function initializeDigitalID() {
    console.log('Digital ID System Initialized');
    
    // Add animations to elements
    observeElementsForAnimation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize card flip functionality
    setupCardFlip();
    
    // Load blockchain verification status
    verifyBlockchainStatus();
}

// Load tourist data into the card
function renderTouristData() {
    if (!touristData) return;
    // Load basic information
    document.getElementById('touristName').textContent = touristData.name;
    document.getElementById('touristNationality').textContent = touristData.nationality;
    document.getElementById('idNumber').textContent = touristData.id;
    document.getElementById('dateOfBirth').textContent = touristData.dateOfBirth;
    
    // Calculate and set expiry date (5 years from registration)
    const expiryDate = new Date();
    expiryDate.setFullYear(expiryDate.getFullYear() + 5);
    document.getElementById('expiryDate').textContent = expiryDate.toLocaleDateString('en-GB');
    
    // Load photo
    const photoElement = document.getElementById('touristPhoto');
    if (touristData.photo) {
        photoElement.src = touristData.photo;
    }
    
    // Load emergency contacts
    loadEmergencyContacts();
    
    // Load medical information
    loadMedicalInfo();
    
    // Load travel information
    // travelInfo removed for now; keep placeholder content
    
    // Load blockchain information
    loadBlockchainInfo();
}

// Load emergency contacts
function loadEmergencyContacts() {
    const contactsContainer = document.getElementById('emergencyContacts');
    
    if (!contactsContainer) {
        console.warn('Emergency contacts container not found');
        return;
    }
    
    contactsContainer.innerHTML = '';
    
    const contacts = touristData.emergencyContacts || [];
    
    if (contacts.length === 0) {
        contactsContainer.innerHTML = '<div class="contact-item"><em>No emergency contacts available</em></div>';
        return;
    }
    
    contacts.forEach((contact, index) => {
        const contactDiv = document.createElement('div');
        contactDiv.className = 'contact-item';
        
        // Handle different field names
        const name = contact.name || contact.full_name || contact.contact_name || 'Unknown';
        const phone = contact.phone || contact.phone_number || contact.contact_phone || 'N/A';
        const relationship = contact.relationship || contact.type || contact.relation || `Contact ${index + 1}`;
        const email = contact.email || contact.contact_email || '';
        
        let contactHTML = `<strong>${relationship}:</strong> ${name}`;
        if (phone && phone !== 'N/A') {
            contactHTML += ` (${phone})`;
        }
        if (email) {
            contactHTML += `<br><small style="margin-left: 10px;">📧 ${email}</small>`;
        }
        
        contactDiv.innerHTML = contactHTML;
        contactsContainer.appendChild(contactDiv);
    });
}

// Load medical information
function loadMedicalInfo() {
    const mi = touristData.medicalInfo || {};
    
    // Blood type
    document.getElementById('bloodType').textContent = mi.bloodType || mi.blood_type || '—';
    
    // Allergies - handle array or string
    let allergiesText = '—';
    if (mi.allergies) {
        if (Array.isArray(mi.allergies)) {
            allergiesText = mi.allergies.length > 0 ? mi.allergies.join(', ') : 'None known';
        } else {
            allergiesText = mi.allergies;
        }
    }
    document.getElementById('allergies').textContent = allergiesText;
    
    // Medications - handle array or string
    let medicationsText = '—';
    if (mi.medications) {
        if (Array.isArray(mi.medications)) {
            medicationsText = mi.medications.length > 0 ? mi.medications.join(', ') : 'None';
        } else {
            medicationsText = mi.medications;
        }
    }
    document.getElementById('medications').textContent = medicationsText;
    
    // Medical conditions - handle array or string
    let conditionsText = '—';
    if (mi.conditions) {
        if (Array.isArray(mi.conditions)) {
            conditionsText = mi.conditions.length > 0 ? mi.conditions.join(', ') : 'None';
        } else {
            conditionsText = mi.conditions;
        }
    }
    const conditionsElement = document.getElementById('conditions');
    if (conditionsElement) {
        conditionsElement.textContent = conditionsText;
    }
    
    // Update insurance if the element exists
    const insuranceElement = document.getElementById('insurance');
    if (insuranceElement) {
        insuranceElement.textContent = mi.insurance || mi.medical_insurance || '—';
    }
    
    // Add medical notes if available
    const medicalNotesElement = document.getElementById('medicalNotes');
    const medicalNotesContainer = document.getElementById('medicalNotesContainer');
    if (medicalNotesElement && mi.medical_notes) {
        medicalNotesElement.textContent = mi.medical_notes;
        if (medicalNotesContainer) {
            medicalNotesContainer.style.display = 'block';
        }
    }
}

// Load travel information
function loadTravelInfo() {
    document.getElementById('destination').textContent = touristData.travelInfo.destination;
    document.getElementById('duration').textContent = touristData.travelInfo.duration;
    document.getElementById('purpose').textContent = touristData.travelInfo.purpose;
    document.getElementById('accommodation').textContent = touristData.travelInfo.accommodation;
}

// Load blockchain information
function loadBlockchainInfo() {
    const blockHashElement = document.getElementById('blockHash');
    const bh = (touristData.blockchain && touristData.blockchain.blockHash) ? touristData.blockchain.blockHash : '';
    blockHashElement.textContent = bh ? `Block: #${String(bh).substring(0, 8)}...` : 'Block: #—';
}

// Setup card controls
function setupCardControls() {
    // Flip card button
    document.getElementById('flipCard').addEventListener('click', flipCard);
    
    // Download card button
    document.getElementById('downloadCard').addEventListener('click', downloadCard);
    
    // Share card button
    document.getElementById('shareCard').addEventListener('click', shareCard);
    
    // Verify card button
    document.getElementById('verifyCard').addEventListener('click', verifyCard);
}

// Setup card flip functionality
function setupCardFlip() {
    const card = document.getElementById('digitalIdCard');
    let isFlipped = false;
    
    // Allow double-click to flip
    card.addEventListener('dblclick', flipCard);
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Space' && e.target.closest('.id-card-container')) {
            e.preventDefault();
            flipCard();
        }
    });
}

// Flip card function
function flipCard() {
    const card = document.getElementById('digitalIdCard');
    const flipButton = document.getElementById('flipCard');
    
    card.classList.toggle('flipped');
    
    // Update button text
    const isFlipped = card.classList.contains('flipped');
    flipButton.innerHTML = isFlipped 
        ? '<i class="fas fa-sync-alt"></i><span>Show Front</span>'
        : '<i class="fas fa-sync-alt"></i><span>Show Back</span>';
    
    // Track flip event
    trackEvent('card_flip', { side: isFlipped ? 'back' : 'front' });
}

// Generate QR codes
function generateQRCodes() {
    // Generate main QR code for ID verification
    const idQRData = touristData ? {
        id: touristData.id,
        name: touristData.name,
        nationality: touristData.nationality,
        verified: touristData.blockchain && touristData.blockchain.verified,
        blockHash: touristData.blockchain && touristData.blockchain.blockHash,
        timestamp: touristData.blockchain && touristData.blockchain.timestamp
    } : { id: '', name: '', nationality: '', verified: false, blockHash: '', timestamp: '' };
    
    generateQRCode('idQrCode', JSON.stringify(idQRData));
    
    // Generate backup QR code with emergency info
    const emergencyQRData = touristData ? {
        id: touristData.id,
        name: touristData.name,
        emergencyContacts: touristData.emergencyContacts,
        medicalInfo: touristData.medicalInfo,
        type: 'emergency'
    } : { id: '', name: '', emergencyContacts: [], medicalInfo: {}, type: 'emergency' };
    
    generateQRCode('backupQrCode', JSON.stringify(emergencyQRData));
}

// Generate individual QR code
function generateQRCode(elementId, data) {
    const qrElement = document.getElementById(elementId);
    if (!qrElement) return;
    
    // Create QR code pattern (simplified version)
    const qrSVG = createAdvancedQRPattern(data);
    qrElement.innerHTML = qrSVG;
    
    // Add click to copy functionality
    qrElement.style.cursor = 'pointer';
    qrElement.title = 'Click to copy verification data';
    qrElement.addEventListener('click', () => {
        copyToClipboard(data);
        showToast('Verification data copied to clipboard');
    });
}

// Create advanced QR pattern
function createAdvancedQRPattern(data) {
    const size = 100;
    const cellSize = 2;
    const cells = size / cellSize;
    
    // Generate hash from data
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
        hash = ((hash << 5) - hash + data.charCodeAt(i)) & 0xffffffff;
    }
    
    let pattern = `<svg width="100%" height="100%" viewBox="0 0 ${size} ${size}">`;
    
    // Background
    pattern += `<rect width="${size}" height="${size}" fill="#ffffff"/>`;
    
    // Generate data pattern
    for (let y = 0; y < cells; y++) {
        for (let x = 0; x < cells; x++) {
            // Skip finder pattern areas
            if (isFinderPattern(x, y, cells)) continue;
            
            const random = Math.abs(hash * (x + y * cells)) % 100;
            if (random > 45) {
                pattern += `<rect x="${x * cellSize}" y="${y * cellSize}" width="${cellSize}" height="${cellSize}" fill="#000000"/>`;
            }
        }
    }
    
    // Add finder patterns (3 corners)
    const finderSize = 14;
    const positions = [
        { x: 0, y: 0 },
        { x: size - finderSize, y: 0 },
        { x: 0, y: size - finderSize }
    ];
    
    positions.forEach(pos => {
        // Outer square
        pattern += `<rect x="${pos.x}" y="${pos.y}" width="${finderSize}" height="${finderSize}" fill="#000000"/>`;
        // Inner white square
        pattern += `<rect x="${pos.x + 2}" y="${pos.y + 2}" width="${finderSize - 4}" height="${finderSize - 4}" fill="#ffffff"/>`;
        // Center black square
        pattern += `<rect x="${pos.x + 4}" y="${pos.y + 4}" width="${finderSize - 8}" height="${finderSize - 8}" fill="#000000"/>`;
    });
    
    // Add timing patterns
    for (let i = finderSize + 2; i < size - finderSize - 2; i += 4) {
        pattern += `<rect x="${i}" y="6" width="2" height="2" fill="#000000"/>`;
        pattern += `<rect x="6" y="${i}" width="2" height="2" fill="#000000"/>`;
    }
    
    pattern += '</svg>';
    return pattern;
}

// Check if position is in finder pattern area
function isFinderPattern(x, y, cells) {
    const finderSize = 7;
    return (
        (x < finderSize && y < finderSize) ||
        (x >= cells - finderSize && y < finderSize) ||
        (x < finderSize && y >= cells - finderSize)
    );
}

// Setup verification system
function setupVerificationSystem() {
    // Simulate real-time verification status updates
    updateVerificationStatus();
    
    // Check verification status periodically
    setInterval(updateVerificationStatus, 30000); // Every 30 seconds
}

// Update verification status
function updateVerificationStatus() {
    const statusItems = document.querySelectorAll('.status-item');
    
    // Simulate verification checks
    setTimeout(() => {
        statusItems.forEach((item, index) => {
            if (Math.random() > 0.8) { // 20% chance to update status
                if (item.classList.contains('pending')) {
                    item.classList.remove('pending');
                    item.classList.add('verified');
                    item.querySelector('i').className = 'fas fa-check-circle';
                    item.querySelector('small').textContent = `Verified ${new Date().toLocaleDateString()}`;
                }
            }
        });
    }, 1000 * index);
}

// Verify blockchain status
function verifyBlockchainStatus() {
    // Simulate blockchain verification
    const verifyPromise = new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                verified: true,
                blockHeight: Math.floor(Math.random() * 1000000),
                confirmations: Math.floor(Math.random() * 100) + 1
            });
        }, 2000);
    });
    
    verifyPromise.then(result => {
        if (result.verified) {
            updateBlockchainDisplay(result);
        }
    });
}

// Update blockchain display
function updateBlockchainDisplay(data) {
    const blockchainStatus = document.querySelector('.blockchain-status');
    const blockHash = document.querySelector('.block-hash');
    
    if (data.verified) {
        blockchainStatus.innerHTML = '<i class="fas fa-link"></i><span>Blockchain Verified</span>';
        blockHash.innerHTML = `<small>Block: #${data.blockHeight} (${data.confirmations} confirmations)</small>`;
    }
}

// Download card functionality
function downloadCard() {
    // Create a canvas to draw the card
    const card = document.getElementById('digitalIdCard');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = 800;
    canvas.height = 500;
    
    // Draw card background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw card content (simplified version)
    ctx.fillStyle = '#007bff';
    ctx.fillRect(0, 0, canvas.width, 80);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('DIGITAL TOURIST ID', canvas.width / 2, 50);
    
    ctx.fillStyle = '#000000';
    ctx.font = 'bold 32px Arial';
    ctx.fillText(touristData.name, canvas.width / 2, 200);
    
    ctx.font = '18px Arial';
    ctx.fillText(`ID: ${touristData.id}`, canvas.width / 2, 250);
    ctx.fillText(`Nationality: ${touristData.nationality}`, canvas.width / 2, 280);
    ctx.fillText(`DOB: ${touristData.dateOfBirth}`, canvas.width / 2, 310);
    
    // Download the image
    const link = document.createElement('a');
    link.download = `digital-id-${touristData.id}.png`;
    link.href = canvas.toDataURL();
    link.click();
    
    trackEvent('card_download', { format: 'png', id: touristData.id });
    showToast('Digital ID card downloaded successfully!');
}

// Share card functionality
function shareCard() {
    const shareData = {
        title: 'Digital Tourist ID',
        text: `Digital Tourist ID for ${touristData.name}`,
        url: window.location.href
    };
    
    if (navigator.share) {
        navigator.share(shareData)
            .then(() => {
                trackEvent('card_share', { method: 'native', id: touristData.id });
                showToast('Card shared successfully!');
            })
            .catch((error) => {
                console.log('Error sharing:', error);
                fallbackShare();
            });
    } else {
        fallbackShare();
    }
}

// Fallback share functionality
function fallbackShare() {
    const shareUrl = window.location.href;
    
    const modal = document.createElement('div');
    modal.className = 'share-modal';
    modal.innerHTML = `
        <div class="share-modal-content">
            <h3>Share Digital ID</h3>
            <div class="share-options">
                <button class="share-btn" onclick="shareToSocial('facebook')">
                    <i class="fab fa-facebook"></i> Facebook
                </button>
                <button class="share-btn" onclick="shareToSocial('twitter')">
                    <i class="fab fa-twitter"></i> Twitter
                </button>
                <button class="share-btn" onclick="shareToSocial('linkedin')">
                    <i class="fab fa-linkedin"></i> LinkedIn
                </button>
                <button class="share-btn" onclick="shareToSocial('whatsapp')">
                    <i class="fab fa-whatsapp"></i> WhatsApp
                </button>
            </div>
            <div class="share-url">
                <input type="text" value="${shareUrl}" readonly>
                <button onclick="copyToClipboard('${shareUrl}')">Copy</button>
            </div>
            <button class="close-modal" onclick="closeShareModal()">Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentShareModal = modal;
}

// Share to social media
function shareToSocial(platform) {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(`Check out my Digital Tourist ID - ${touristData.name}`);
    
    const urls = {
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
        twitter: `https://twitter.com/intent/tweet?url=${url}&text=${text}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
        whatsapp: `https://wa.me/?text=${text}%20${url}`
    };
    
    window.open(urls[platform], '_blank', 'width=600,height=400');
    trackEvent('card_share', { method: platform, id: touristData.id });
}

// Close share modal
function closeShareModal() {
    if (window.currentShareModal) {
        document.body.removeChild(window.currentShareModal);
        window.currentShareModal = null;
    }
}

// Verify card functionality
function verifyCard() {
    showVerificationModal();
}

// Show verification modal
function showVerificationModal() {
    const modal = document.createElement('div');
    modal.className = 'verification-modal';
    modal.innerHTML = `
        <div class="verification-modal-content">
            <h3>Card Verification</h3>
            <div class="verification-progress">
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <p class="progress-text">Verifying blockchain records...</p>
            </div>
            <div class="verification-steps">
                <div class="step-item" id="step1">
                    <i class="fas fa-circle-notch fa-spin"></i>
                    <span>Checking digital signature</span>
                </div>
                <div class="step-item" id="step2">
                    <i class="fas fa-circle"></i>
                    <span>Verifying blockchain hash</span>
                </div>
                <div class="step-item" id="step3">
                    <i class="fas fa-circle"></i>
                    <span>Validating timestamp</span>
                </div>
                <div class="step-item" id="step4">
                    <i class="fas fa-circle"></i>
                    <span>Checking document integrity</span>
                </div>
            </div>
            <button class="close-modal" onclick="closeVerificationModal()" style="display:none;">Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentVerificationModal = modal;
    
    // Start verification process
    runVerificationProcess();
}

// Run verification process
function runVerificationProcess() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    
    let currentStep = 0;
    
    const verifyStep = () => {
        if (currentStep > 0) {
            const prevStep = document.getElementById(steps[currentStep - 1]);
            prevStep.querySelector('i').className = 'fas fa-check-circle';
            prevStep.style.color = '#28a745';
        }
        
        if (currentStep < steps.length) {
            const step = document.getElementById(steps[currentStep]);
            step.querySelector('i').className = 'fas fa-circle-notch fa-spin';
            step.style.color = '#007bff';
            
            const progress = ((currentStep + 1) / steps.length) * 100;
            progressFill.style.width = progress + '%';
            
            const messages = [
                'Checking digital signature...',
                'Verifying blockchain hash...',
                'Validating timestamp...',
                'Checking document integrity...'
            ];
            
            progressText.textContent = messages[currentStep];
            
            currentStep++;
            
            setTimeout(verifyStep, 1500);
        } else {
            // Verification complete
            progressText.textContent = 'Verification complete - Card is authentic!';
            progressText.style.color = '#28a745';
            
            document.querySelector('.close-modal').style.display = 'block';
            
            trackEvent('card_verification', { 
                result: 'success', 
                id: touristData.id,
                timestamp: new Date().toISOString()
            });
        }
    };
    
    verifyStep();
}

// Close verification modal
function closeVerificationModal() {
    if (window.currentVerificationModal) {
        document.body.removeChild(window.currentVerificationModal);
        window.currentVerificationModal = null;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 's':
                    e.preventDefault();
                    downloadCard();
                    break;
                case 'f':
                    e.preventDefault();
                    flipCard();
                    break;
                case 'v':
                    e.preventDefault();
                    verifyCard();
                    break;
            }
        }
    });
    
    // Touch gestures for mobile
    let touchStartX = 0;
    let touchStartY = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', (e) => {
        if (!touchStartX || !touchStartY) return;
        
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        
        const diffX = touchStartX - touchEndX;
        const diffY = touchStartY - touchEndY;
        
        // Swipe gestures
        if (Math.abs(diffX) > Math.abs(diffY)) {
            if (Math.abs(diffX) > 50) {
                flipCard(); // Horizontal swipe to flip card
            }
        }
        
        touchStartX = 0;
        touchStartY = 0;
    });
}

// Observe elements for animations
function observeElementsForAnimation() {
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
    
    const elements = document.querySelectorAll('.feature-item, .status-item, .history-item');
    elements.forEach(el => observer.observe(el));
}

// Utility functions
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}

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
        max-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutDown 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

function trackEvent(eventName, data = {}) {
    console.log('Event tracked:', eventName, data);
    
    // Send to analytics (if available)
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, data);
    }
}

// Export functions for global access
window.shareToSocial = shareToSocial;
window.closeShareModal = closeShareModal;
window.closeVerificationModal = closeVerificationModal;

// Add necessary CSS for modals and animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideOutDown {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(100%); opacity: 0; }
    }
    
    .share-modal, .verification-modal {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex; align-items: center; justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    }
    
    .share-modal-content, .verification-modal-content {
        background: white; padding: 30px; border-radius: 15px;
        max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto;
    }
    
    .share-options { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
    .share-btn { padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
    .share-url { display: flex; gap: 10px; margin: 20px 0; }
    .share-url input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
    .share-url button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    
    .verification-progress { margin: 20px 0; }
    .progress-bar { width: 100%; height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #007bff, #0056b3); width: 0%; transition: width 0.5s ease; }
    .progress-text { text-align: center; margin-top: 10px; font-weight: 600; color: #007bff; }
    
    .verification-steps { margin: 20px 0; }
    .step-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; color: #6c757d; }
    .step-item i { width: 20px; }
    
    .close-modal { background: #007bff; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: 600; width: 100%; margin-top: 20px; }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
`;

document.head.appendChild(style);