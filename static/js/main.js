// HarpoTab - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('HarpoTab loaded');

    // Initialize tooltips (Bootstrap 5)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
            }
        });
    }

    // Form submission handler
    const convertForm = document.getElementById('convertForm');
    if (convertForm) {
        convertForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            if (!fileInput.files.length) {
                e.preventDefault();
                alert('Veuillez sélectionner un fichier');
                return false;
            }

            // Show loading state
            const submitBtn = convertForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Conversion en cours...';
            }
        });
    }

    // Drag and drop support (future enhancement)
    initDragAndDrop();
});

/**
 * Validate uploaded file
 */
function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10 MB
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];

    // Check size
    if (file.size > maxSize) {
        alert('Le fichier est trop volumineux. Taille maximale : 10 MB');
        document.getElementById('file').value = '';
        return false;
    }

    // Check type
    if (!allowedTypes.includes(file.type)) {
        alert('Format de fichier non supporté. Utilisez PDF, PNG ou JPEG.');
        document.getElementById('file').value = '';
        return false;
    }

    // Display file info
    displayFileInfo(file);
    return true;
}

/**
 * Display file information
 */
function displayFileInfo(file) {
    const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
    console.log(`Fichier sélectionné: ${file.name} (${sizeInMB} MB)`);

    // Could add visual feedback here
}

/**
 * Initialize drag and drop for file upload
 */
function initDragAndDrop() {
    const dropZone = document.querySelector('.drop-zone');
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', handleDrop);
}

/**
 * Handle file drop
 */
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
        const fileInput = document.getElementById('file');
        if (fileInput) {
            fileInput.files = files;
            validateFile(files[0]);
        }
    }
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Traitement en cours...') {
    // TODO: Implement loading overlay
    console.log('Loading:', message);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    // TODO: Implement
    console.log('Loading finished');
}

/**
 * Display error message
 */
function showError(message) {
    alert('Erreur: ' + message);
}

/**
 * Display success message
 */
function showSuccess(message) {
    console.log('Success:', message);
}
