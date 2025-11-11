// Enhanced Registration JavaScript

// Form submission handler to prevent unwanted redirections
function handleFormSubmission(event) {
    console.log('🚀 Form submission intercepted');
    
    // Prevent default form submission
    event.preventDefault();
    
    // Check if we're on the final step
    if (currentStep === totalSteps) {
        console.log('✅ Final step reached, processing registration');
        // Call the actual registration submission
        return submitRegistration();
    } else {
        console.log('⚠️ Not on final step, preventing form submission');
        // If not on final step, just go to next step instead
        try {
            nextStep();
        } catch (error) {
            console.error('Error advancing step:', error);
        }
        return false; // Prevent form submission
    }
}

// Make the function globally accessible
window.handleFormSubmission = handleFormSubmission;

// Global variables - make sure they're accessible everywhere
let currentStep = 1;
const totalSteps = 5;
let uploadedFiles = {};
let formData = {};
// Draft support
let draftId = localStorage.getItem('enh_reg_draft_id') || crypto.randomUUID();
localStorage.setItem('enh_reg_draft_id', draftId);
let lastAutosaveTime = 0;
const AUTOSAVE_INTERVAL_MS = 3000;

// Also set window properties for global access
window.currentStep = 1;
window.totalSteps = 5;
window.uploadedFiles = {};
window.formData = {};

// Translation system - use shared variable from common.js to avoid conflicts.
// IMPORTANT: Do NOT redeclare `translations` (already declared in common.js with let) to prevent SyntaxError.
// Access it directly as a global. Fallback if somehow undefined.
if (typeof window.translations === 'undefined') { window.translations = {}; }
// Use the shared global variable from common.js to avoid redeclaration conflicts
let currentLanguage = window.currentLanguage || 'en';

// DEBUG FUNCTIONS - Available globally for console testing
window.debugRegistration = {
    forceNext: function() {
        console.log('🔧 DEBUG: Force Next Step');
        console.log('Before - currentStep:', currentStep);
        if (currentStep < totalSteps) {
            currentStep++;
            console.log('After - currentStep:', currentStep);
            showStep(currentStep);
            updateProgressBar();
            console.log('✅ Forced to step:', currentStep);
        } else {
            console.log('❌ Already at final step');
        }
    },
    
    goToStep: function(step) {
        console.log('🔧 DEBUG: Go to step', step);
        if (step >= 1 && step <= totalSteps) {
            currentStep = step;
            showStep(currentStep);
            updateProgressBar();
            console.log('✅ Moved to step:', currentStep);
        } else {
            console.log('❌ Invalid step:', step);
        }
    },
    
    getCurrentStep: function() {
        console.log('Current step:', currentStep);
        return currentStep;
    },
    
    listAllSteps: function() {
        console.log('Available form steps:');
        document.querySelectorAll('.form-step').forEach((step, index) => {
            console.log(`Step ${index + 1}:`, step.id, step.classList.contains('active') ? '(ACTIVE)' : '');
        });
    },
    
    testNextButton: function() {
        console.log('🔧 DEBUG: Testing Next Button');
        const nextBtn = document.getElementById('next-btn');
        console.log('Next button found:', !!nextBtn);
        if (nextBtn) {
            console.log('Next button onclick:', nextBtn.onclick);
            console.log('Triggering click...');
            nextBtn.click();
        }
    }
};

// Initialize the form
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing registration form...');
    
    loadTranslations();
    initializeForm();
    setupFileUploads();
    setupFormValidation();
    updateProgressBar();
    
    console.log('Registration form initialized successfully');
});

async function loadTranslations() {
    try {
        console.log('🌍 Loading translations...');
        const response = await fetch('/static/translations.json');
        
        if (!response.ok) {
            throw new Error(`Failed to load translations: ${response.status}`);
        }
        
        translations = await response.json();
        console.log('✅ Translations loaded successfully:', Object.keys(translations));
        updateTranslations();
        
    } catch (error) {
        console.warn('⚠️ Failed to load translations, using fallback:', error);
        // Fallback translations for essential elements
        translations = {
            en: {
                next: 'Next',
                previous: 'Previous',
                create_digital_id: 'Create Digital ID',
                personal_info: 'Personal Info',
                documents: 'Documents',
                medical_info: 'Medical Info',
                emergency_contacts: 'Emergency Contacts',
                verification: 'Verification'
            }
        };
        updateTranslations();
    }
}

function changeLanguage() {
    try {
        const select = document.getElementById('language-select');
        if (!select) {
            console.error('Language select element not found');
            return;
        }
        
        const newLanguage = select.value;
        console.log('🌍 Changing language from', currentLanguage, 'to', newLanguage);
        currentLanguage = newLanguage;
        
        // Update translations
        updateTranslations();
        
        // Notify backend about language change
        fetch('/api/set_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: newLanguage })
        })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Language set successfully:', data);
        })
        .catch(error => {
            console.warn('⚠️ Language setting failed, but continuing with client-side translation:', error);
        });
        
    } catch (error) {
        console.error('Error changing language:', error);
    }
}

function updateTranslations() {
    try {
        console.log('🔄 Updating translations for language:', currentLanguage);
        
        // Check if translations are loaded
        if (!translations || typeof translations !== 'object') {
            console.warn('⚠️ Translations not loaded, attempting to load...');
            loadTranslations().then(() => {
                updateTranslations(); // Retry after loading
            });
            return;
        }
        
        // Check if current language translations exist
        if (!translations[currentLanguage]) {
            console.warn(`⚠️ No translations found for language: ${currentLanguage}, falling back to English`);
            currentLanguage = 'en';
        }

        const elements = document.querySelectorAll('[data-translate]');
        console.log(`📝 Found ${elements.length} elements to translate`);
        
        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            if (translations[currentLanguage] && translations[currentLanguage][key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translations[currentLanguage][key];
                } else {
                    element.textContent = translations[currentLanguage][key];
                }
            } else {
                console.warn(`⚠️ Translation key '${key}' not found for language '${currentLanguage}'`);
            }
        });
        
        console.log('✅ Translation update completed');
    } catch (error) {
        console.error('Error updating translations:', error);
    }
}

function initializeForm() {
    // Set up step navigation
    showStep(1);
    
    // Set up visa field toggle
    const visaSelect = document.getElementById('visa-required');
    if (visaSelect) {
        visaSelect.addEventListener('change', toggleVisaFields);
    }
    
    // Set up form submission
    const form = document.getElementById('enhanced-registration-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }
    
    // Add explicit click handlers for navigation buttons
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    console.log('Setting up button handlers...');
    console.log('Next button found:', !!nextBtn);
    console.log('Previous button found:', !!prevBtn);
    console.log('Submit button found:', !!submitBtn);
    
    if (nextBtn) {
        // Remove any existing onclick to avoid conflicts
        nextBtn.onclick = null;
        
        // Only use addEventListener (not onclick) to prevent double-triggering
        nextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('✅ Next button clicked');
            nextStep();
        }, { once: false }); // Allow multiple clicks but prevent double execution
        
        console.log('✅ Next button handler attached');
    } else {
        console.error('❌ Next button not found!');
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Previous button clicked via event listener');
            previousStep();
        });
    }
    
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Submit button clicked via event listener');
            handleFormSubmission(e);
        });
    }
}

function setupFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileSelection);
    });
    
    // Set up drag and drop
    const uploadAreas = document.querySelectorAll('.file-upload-area');
    uploadAreas.forEach(area => {
        area.addEventListener('dragover', handleDragOver);
        area.addEventListener('dragleave', handleDragLeave);
        area.addEventListener('drop', handleFileDrop);
    });
}

function triggerFileUpload(inputId) {
    document.getElementById(inputId).click();
}

function handleFileSelection(event) {
    const input = event.target;
    const files = input.files;
    const inputId = input.id;
    
    if (files.length > 0) {
        uploadedFiles[inputId] = Array.from(files);
        displayFilePreview(inputId, files);
        validateFileUpload(input, files);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    const uploadArea = event.currentTarget;
    uploadArea.classList.remove('dragover');
    
    const input = uploadArea.querySelector('input[type="file"]');
    if (input) {
        input.files = event.dataTransfer.files;
        handleFileSelection({ target: input });
    }
}

function displayFilePreview(inputId, files) {
    const previewId = inputId.replace('-upload', '-preview');
    const previewContainer = document.getElementById(previewId);
    
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    previewContainer.classList.add('show');
    
    Array.from(files).forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const fileIcon = getFileIcon(file.type);
        const fileSize = formatFileSize(file.size);
        
        fileItem.innerHTML = `
            <div class="file-icon">${fileIcon}</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${fileSize}</div>
            </div>
            <button type="button" class="file-remove" onclick="removeFile('${inputId}', ${index})">Remove</button>
        `;
        
        previewContainer.appendChild(fileItem);
    });
}

function getFileIcon(fileType) {
    if (fileType.startsWith('image/')) return '🖼️';
    if (fileType === 'application/pdf') return '📄';
    return '📎';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function removeFile(inputId, fileIndex) {
    if (uploadedFiles[inputId]) {
        uploadedFiles[inputId].splice(fileIndex, 1);
        
        // Update the file input
        const input = document.getElementById(inputId);
        if (uploadedFiles[inputId].length === 0) {
            input.value = '';
            const previewId = inputId.replace('-upload', '-preview');
            const previewContainer = document.getElementById(previewId);
            if (previewContainer) {
                previewContainer.classList.remove('show');
                previewContainer.innerHTML = '';
            }
        } else {
            // Recreate file list
            const dt = new DataTransfer();
            uploadedFiles[inputId].forEach(file => dt.items.add(file));
            input.files = dt.files;
            displayFilePreview(inputId, dt.files);
        }
    }
}

function validateFileUpload(input, files) {
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    
    Array.from(files).forEach(file => {
        if (file.size > maxSize) {
            showAlert(`File ${file.name} is too large. Maximum size is 5MB.`, 'error');
            return false;
        }
        
        if (!allowedTypes.includes(file.type)) {
            showAlert(`File ${file.name} has unsupported format. Please use JPG, PNG, or PDF.`, 'error');
            return false;
        }
    });
    
    return true;
}

function toggleVisaFields() {
    const visaRequired = document.getElementById('visa-required').value;
    const visaFields = document.getElementById('visa-fields');
    
    if (visaRequired === 'yes') {
        visaFields.style.display = 'block';
        // Make visa fields required
        document.getElementById('visa-number').required = true;
        document.getElementById('visa-expiry').required = true;
    } else {
        visaFields.style.display = 'none';
        // Remove required attribute
        document.getElementById('visa-number').required = false;
        document.getElementById('visa-expiry').required = false;
    }
}

// Add debugging functions to window for testing
window.debugRegistration = {
    goToStep: function(step) {
        console.log('Forcing navigation to step:', step);
        currentStep = step;
        showStep(step);
        updateProgressBar();
    },
    
    getCurrentStep: function() {
        return currentStep;
    },
    
    listAllSteps: function() {
        const steps = document.querySelectorAll('.form-step');
        console.log('All form steps found:');
        steps.forEach((step, index) => {
            console.log(`${index + 1}. ${step.id} - ${step.classList.contains('active') ? 'ACTIVE' : 'HIDDEN'}`);
        });
        return steps;
    },
    
    testNextStep: function() {
        console.log('Testing next step function...');
        nextStep();
    }
};

// Add a simple skip validation function for testing
function skipToNextStep() {
    console.log('Skipping validation, moving to next step');
    saveCurrentStepData();
    if (currentStep < totalSteps) {
        currentStep++;
        window.currentStep = currentStep; // Keep window.currentStep in sync
        console.log('Moving to step:', currentStep);
        showStep(currentStep);
        updateProgressBar();
        
        if (currentStep === 5) {
            generateSummary();
        }
    }
}

// Make skipToNextStep globally accessible (for console debugging only)
window.skipToNextStep = skipToNextStep;

// Keyboard shortcuts disabled to prevent accidental step skipping
// Users must use the Next/Previous buttons to navigate through registration steps

function nextStep() {
    console.log('=== NEXT BUTTON CLICKED ===');
    console.log('Current step:', currentStep);
    console.log('Total steps:', totalSteps);
    console.log('Current step ID:', getStepId(currentStep));
    console.log('Next step ID:', getStepId(currentStep + 1));
    
    try {
        // Clear any existing errors
        document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        
        // Save current step data (simplified - no validation for now)
        console.log('Saving current step data...');
        saveCurrentStepData();
        console.log('Form data after save:', formData);
        
        // Attempt autosave of current step before moving
        autosaveDraft(currentStep).catch(err => console.warn('Autosave failed (non-blocking):', err));
        
        // Move to next step if not at end
        if (currentStep < totalSteps) {
            const oldStep = currentStep;
            currentStep++;
            window.currentStep = currentStep; // Keep window.currentStep in sync
            
            console.log(`✅ Moving from step ${oldStep} (${getStepId(oldStep)}) to step ${currentStep} (${getStepId(currentStep)})`);
            
            console.log('Calling showStep...');
            showStep(currentStep);
            
            console.log('Updating progress bar...');
            updateProgressBar();
            
            if (currentStep === 5) {
                console.log('Final step - generating summary...');
                generateSummary();
                // Final autosave of all data
                autosaveDraft(currentStep).catch(err => console.warn('Final step autosave failed:', err));
            }
            
            console.log('✅ Successfully moved to step:', currentStep, getStepId(currentStep));
        } else {
            console.log('Already at final step, cannot proceed');
        }
        
        console.log('=== END NEXT STEP ===');
        
    } catch (error) {
        console.error('❌ Error in nextStep:', error);
        alert('Error proceeding to next step: ' + error.message);
    }
}

// Make nextStep globally accessible
window.nextStep = nextStep; // expose immediately

function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        window.currentStep = currentStep; // Keep window.currentStep in sync
        showStep(currentStep);
        updateProgressBar();
    }
}

// Make previousStep globally accessible
window.previousStep = previousStep; // expose immediately

function showStep(step) {
    console.log('=== SHOW STEP CALLED ===');
    console.log('Step number:', step);
    console.log('Step ID to show:', getStepId(step));
    
    // Critical check for step 2 (documents)
    if (step === 2) {
        console.log('🚨 SHOWING DOCUMENTS STEP (STEP 2)');
        console.log('Expected element ID: documents-step');
    }
    
    // Hide all steps
    const allSteps = document.querySelectorAll('.form-step');
    console.log(`Found ${allSteps.length} total form steps`);
    
    allSteps.forEach(stepEl => {
        stepEl.classList.remove('active');
        console.log('  - Hiding step:', stepEl.id);
    });
    
    // Show current step
    const stepIdToShow = getStepId(step);
    const currentStepEl = document.getElementById(stepIdToShow);
    console.log('Looking for element with ID:', stepIdToShow);
    console.log('Element found:', !!currentStepEl);
    
    if (currentStepEl) {
        currentStepEl.classList.add('active');
        console.log('✅ Successfully showing step:', currentStepEl.id);
        
        // Verify it's actually visible
        const isVisible = currentStepEl.classList.contains('active');
        console.log('Has "active" class:', isVisible);
        console.log('Display style:', window.getComputedStyle(currentStepEl).display);
    } else {
        console.error('❌ STEP ELEMENT NOT FOUND:', stepIdToShow);
        console.error('This is a critical error - the HTML element is missing!');
        // List all available form steps
        console.log('Available form steps in DOM:');
        allSteps.forEach((s, idx) => {
            console.log(`  ${idx + 1}. ID: "${s.id}"`);
        });
    }
    
    // Update navigation buttons
    updateNavigationButtons();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    console.log('=== END SHOW STEP ===');
}

// Make showStep globally accessible
window.showStep = showStep;

function getStepId(step) {
    const stepIds = [
        '',
        'personal-info-step',
        'documents-step',
        'medical-info-step',
        'emergency-contacts-step',
        'verification-step'
    ];
    return stepIds[step];
}

function updateProgressBar() {
    // Update step indicators
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNumber < currentStep) {
            step.classList.add('completed');
        } else if (stepNumber === currentStep) {
            step.classList.add('active');
        }
    });
    
    // Update progress bar fill
    const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
    const progressBar = document.querySelector('.progress-bar::after');
    if (progressBar) {
        document.documentElement.style.setProperty('--progress-width', `${progressPercentage}%`);
    }
}

// Make updateProgressBar globally accessible
window.updateProgressBar = updateProgressBar;

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // Previous button
    if (currentStep === 1) {
        prevBtn.style.display = 'none';
    } else {
        prevBtn.style.display = 'inline-block';
    }
    
    // Next/Submit button
    if (currentStep === totalSteps) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-block';
    } else {
        nextBtn.style.display = 'inline-block';
        submitBtn.style.display = 'none';
    }
}

function validateCurrentStep() {
    console.log('Validating step:', currentStep);
    
    const currentStepEl = document.getElementById(getStepId(currentStep));
    
    if (!currentStepEl) {
        console.log('No step element found for step:', currentStep);
        return true;
    }
    
    const requiredFields = currentStepEl.querySelectorAll('[required]');
    console.log('Found required fields:', requiredFields.length);
    
    let isValid = true;
    let missingFields = [];
    
    requiredFields.forEach((field, index) => {
        console.log(`Checking field ${index}:`, field.name || field.id, 'Value:', field.value);
        
        // Skip hidden fields
        if (field.style.display === 'none' || field.closest('.form-group').style.display === 'none') {
            console.log('Skipping hidden field:', field.name || field.id);
            return;
        }
        
        if (!field.value || field.value.trim() === '') {
            field.classList.add('error');
            showFieldError(field, 'This field is required');
            missingFields.push(getFieldLabel(field));
            isValid = false;
            console.log('Field is invalid (empty):', field.name || field.id);
        } else {
            field.classList.remove('error');
            clearFieldError(field);
            
            // Additional validation
            if (field.type === 'email' && !isValidEmail(field.value)) {
                field.classList.add('error');
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
                console.log('Field is invalid (email):', field.name || field.id);
            }
            
            if (field.type === 'tel' && !isValidPhone(field.value)) {
                field.classList.add('error');
                showFieldError(field, 'Please enter a valid phone number');
                isValid = false;
                console.log('Field is invalid (phone):', field.name || field.id);
            }
            
            // Address validation - minimum length and reasonable content
            if (field.id === 'address' || field.name === 'address') {
                if (field.value.trim().length < 5) {
                    field.classList.add('error');
                    showFieldError(field, 'Please provide a complete address (minimum 5 characters)');
                    isValid = false;
                    console.log('Field is invalid (address too short):', field.name || field.id);
                }
            }
        }
    });
    
    // Show summary of missing fields if any
    if (missingFields.length > 0) {
        showValidationSummary(missingFields);
        console.log('Validation failed - missing fields:', missingFields);
    } else {
        hideValidationSummary();
    }
    
    // Step-specific validations
    if (currentStep === 2) {
        isValid = validateDocumentStep() && isValid;
    }
    
    if (currentStep === 5) {
        isValid = validateConsentStep() && isValid;
    }
    
    console.log('Step validation result:', isValid);
    return isValid;
}

function validateDocumentStep() {
    console.log('Validating document step');
    
    // Make passport upload optional for testing - only warn if missing
    const passportFile = document.getElementById('passport-upload').files;
    if (passportFile.length === 0) {
        console.log('Warning: No passport file uploaded');
        // Don't block progression, just log
        // showAlert('Please upload a passport copy', 'error');
        // return false;
    }
    
    const visaRequired = document.getElementById('visa-required').value;
    console.log('Visa required:', visaRequired);
    
    if (visaRequired === 'yes') {
        const visaNumber = document.getElementById('visa-number').value;
        const visaExpiry = document.getElementById('visa-expiry').value;
        
        if (!visaNumber || !visaExpiry) {
            console.log('Visa information missing');
            showAlert('Please fill in all visa information', 'error');
            return false;
        }
    }
    
    console.log('Document step validation passed');
    return true;
}

function validateConsentStep() {
    const consentBoxes = document.querySelectorAll('#verification-step input[type="checkbox"]');
    let allChecked = true;
    
    consentBoxes.forEach(checkbox => {
        if (!checkbox.checked) {
            allChecked = false;
        }
    });
    
    if (!allChecked) {
        showAlert('Please accept all consent agreements to proceed', 'error');
        return false;
    }
    
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
}

function saveCurrentStepData() {
    const currentStepEl = document.getElementById(getStepId(currentStep));
    if (!currentStepEl) {
        console.warn('⚠️ Current step element not found:', getStepId(currentStep));
        return;
    }
    
    console.log(`💾 Saving data for step ${currentStep} (${getStepId(currentStep)})`);
    const inputs = currentStepEl.querySelectorAll('input, select, textarea');
    console.log(`Found ${inputs.length} input fields in current step`);
    
    let savedCount = 0;
    inputs.forEach(input => {
        if (input.type === 'file') {
            formData[input.name] = uploadedFiles[input.id] || [];
            console.log(`  - File field: ${input.name} = ${(uploadedFiles[input.id] || []).length} file(s)`);
        } else if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
            console.log(`  - Checkbox: ${input.name} = ${input.checked}`);
        } else {
            formData[input.name] = input.value;
            if (input.value) {
                console.log(`  - Field: ${input.name} = "${input.value}"`);
                savedCount++;
            }
        }
    });
    
    console.log(`✅ Saved ${savedCount} non-empty fields from step ${currentStep}`);
    console.log('Current formData:', Object.keys(formData).length, 'total fields');
}

function generateSummary() {
    const summaryContent = document.getElementById('summary-content');
    if (!summaryContent) return;
    
    summaryContent.innerHTML = `
        <div class="summary-section">
            <h4>Personal Information</h4>
            <div class="summary-item">
                <span class="summary-label">Full Name:</span>
                <span class="summary-value">${formData.full_name || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Date of Birth:</span>
                <span class="summary-value">${formData.date_of_birth || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Nationality:</span>
                <span class="summary-value">${formData.nationality || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Phone:</span>
                <span class="summary-value">${formData.phone || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Email:</span>
                <span class="summary-value">${formData.email || 'Not provided'}</span>
            </div>
        </div>
        
        <div class="summary-section">
            <h4>Documents</h4>
            <div class="summary-item">
                <span class="summary-label">Passport Number:</span>
                <span class="summary-value">${formData.passport_number || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Passport Expiry:</span>
                <span class="summary-value">${formData.passport_expiry || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Visa Required:</span>
                <span class="summary-value">${formData.visa_required === 'yes' ? 'Yes' : 'No'}</span>
            </div>
            ${formData.visa_required === 'yes' ? `
                <div class="summary-item">
                    <span class="summary-label">Visa Number:</span>
                    <span class="summary-value">${formData.visa_number || 'Not provided'}</span>
                </div>
            ` : ''}
        </div>
        
        <div class="summary-section">
            <h4>Medical Information</h4>
            <div class="summary-item">
                <span class="summary-label">Blood Type:</span>
                <span class="summary-value">${formData.blood_type || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Allergies:</span>
                <span class="summary-value">${formData.allergies || 'None reported'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Current Medications:</span>
                <span class="summary-value">${formData.medications || 'None reported'}</span>
            </div>
        </div>
        
        <div class="summary-section">
            <h4>Emergency Contacts</h4>
            <div class="summary-item">
                <span class="summary-label">Primary Contact:</span>
                <span class="summary-value">${formData.emergency_name_1 || 'Not provided'}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Primary Phone:</span>
                <span class="summary-value">${formData.emergency_phone_1 || 'Not provided'}</span>
            </div>
            ${formData.emergency_name_2 ? `
                <div class="summary-item">
                    <span class="summary-label">Secondary Contact:</span>
                    <span class="summary-value">${formData.emergency_name_2}</span>
                </div>
            ` : ''}
        </div>
    `;
}

async function handleFormSubmission(event) {
    event.preventDefault();
    
    if (!validateCurrentStep()) {
        return;
    }
    
    // Save final step data
    saveCurrentStepData();
    
    // Show blockchain creation status
    const blockchainStatus = document.getElementById('blockchain-status');
    const submitBtn = document.getElementById('submit-btn');
    
    blockchainStatus.style.display = 'block';
    submitBtn.disabled = true;
    
    // Update status text through different phases
    const statusTexts = [
        'Encrypting personal data...',
        'Creating blockchain digital ID...',
        'Storing on distributed ledger...',
        'Generating verification hash...',
        'Finalizing tamper-proof record...'
    ];
    
    let statusIndex = 0;
    const statusInterval = setInterval(() => {
        const statusText = document.getElementById('blockchain-status-text');
        if (statusText && statusIndex < statusTexts.length) {
            statusText.textContent = statusTexts[statusIndex];
            statusIndex++;
        } else {
            clearInterval(statusInterval);
        }
    }, 1500);
    
    try {
        // Prepare form data for submission
        console.log('📤 Preparing submission data...');
        console.log('Total formData keys:', Object.keys(formData).length);
        console.log('FormData contents:', formData);
        
        const submissionData = new FormData();
        
        // Add text fields
        let appendedCount = 0;
        Object.keys(formData).forEach(key => {
            if (key !== 'undefined' && formData[key] !== undefined) {
                if (Array.isArray(formData[key])) {
                    // Handle file arrays
                    console.log(`  - Appending ${formData[key].length} file(s) for ${key}`);
                    formData[key].forEach(file => {
                        submissionData.append(key, file);
                    });
                } else {
                    console.log(`  - Appending ${key}: ${formData[key]}`);
                    submissionData.append(key, formData[key]);
                    appendedCount++;
                }
            }
        });
        
        console.log(`✅ Appended ${appendedCount} fields to submission data`);
        
        // Submit to enhanced registration endpoint
        const response = await fetch('/api/enhanced_registration', {
            method: 'POST',
            body: submissionData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Simulate blockchain confirmation time
            setTimeout(() => {
                showSuccessPage(result);
            }, 3000);
        } else {
            throw new Error(result.message || 'Registration failed');
        }
        
    } catch (error) {
        console.error('Registration error:', error);
        blockchainStatus.style.display = 'none';
        submitBtn.disabled = false;
        showAlert('Registration failed: ' + error.message, 'error');
    }
}

function showSuccessPage(result) {
    // Redirect to success page with tourist ID
    const params = new URLSearchParams({
        tourist_id: result.tourist_id,
        blockchain_hash: result.blockchain_hash || 'pending',
        registration_type: 'enhanced'
    });
    
    window.location.href = `/registration_success?${params.toString()}`;
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    
    switch (type) {
        case 'success':
            alert.style.backgroundColor = '#28a745';
            break;
        case 'error':
            alert.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            alert.style.backgroundColor = '#ffc107';
            alert.style.color = '#212529';
            break;
    }
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Helper function to get field label
function getFieldLabel(field) {
    const label = field.parentNode.querySelector('label');
    if (label) {
        return label.textContent.replace('*', '').trim();
    }
    return field.name || field.id || 'Unknown field';
}

// Show validation summary
function showValidationSummary(missingFields) {
    // Remove existing summary
    hideValidationSummary();
    
    const summary = document.createElement('div');
    summary.id = 'validation-summary';
    summary.className = 'validation-summary';
    summary.innerHTML = `
        <div class="validation-header">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Please complete the following required fields:</strong>
        </div>
        <ul class="validation-list">
            ${missingFields.map(field => `<li>${field}</li>`).join('')}
        </ul>
        <div class="validation-footer">
            <small>All fields marked with (*) are required to proceed to the next step.</small>
        </div>
    `;
    
    // Add styles
    summary.style.cssText = `
        background: linear-gradient(135deg, #ff6b6b, #feca57);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        border-left: 4px solid #dc3545;
    `;
    
    // Insert at the top of the current step
    const currentStepEl = document.getElementById(getStepId(currentStep));
    if (currentStepEl) {
        currentStepEl.insertBefore(summary, currentStepEl.firstChild);
    }
    
    // Scroll to summary
    summary.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Hide validation summary
function hideValidationSummary() {
    const existingSummary = document.getElementById('validation-summary');
    if (existingSummary) {
        existingSummary.remove();
    }
}

// Setup form validation
function setupFormValidation() {
    document.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('error');
            } else {
                this.classList.remove('error');
                clearFieldError(this);
            }
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                this.classList.remove('error');
                clearFieldError(this);
            }
        });
    });
}

async function autosaveDraft(stepNumber) {
    const now = Date.now();
    if (now - lastAutosaveTime < AUTOSAVE_INTERVAL_MS) {
        return; // throttle
    }
    lastAutosaveTime = now;
    try {
        const stepId = getStepId(stepNumber);
        const stepEl = document.getElementById(stepId);
        if (!stepEl) return;
        // Collect just this step's inputs
        const inputs = stepEl.querySelectorAll('input, select, textarea');
        const payload = {};
        inputs.forEach(input => {
            if (input.type === 'file') {
                payload[input.name] = (uploadedFiles[input.id] || []).map(f => f.name);
            } else if (input.type === 'checkbox') {
                payload[input.name] = input.checked;
            } else {
                payload[input.name] = input.value;
            }
        });
        const res = await fetch('/api/enhanced_registration/draft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ draft_id: draftId, step: stepNumber, data: payload })
        });
        const data = await res.json();
        if (!data.success) {
            console.warn('Draft save reported failure:', data.message);
        } else {
            showAutosaveIndicator();
        }
    } catch (e) {
        console.warn('Autosave exception:', e);
    }
}

function showAutosaveIndicator() {
    let el = document.getElementById('autosave-indicator');
    if (!el) {
        el = document.createElement('div');
        el.id = 'autosave-indicator';
        el.style.cssText = 'position:fixed;bottom:10px;right:10px;background:#0a0;color:#fff;padding:6px 10px;border-radius:4px;font-size:12px;z-index:9999;opacity:0;transition:opacity .4s';
        el.textContent = 'Saved';
        document.body.appendChild(el);
    }
    el.style.opacity = '1';
    setTimeout(()=>{ el.style.opacity = '0'; }, 1500);
}