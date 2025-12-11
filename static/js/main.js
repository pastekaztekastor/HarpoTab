/**
 * HarpoTab - Main JavaScript File
 * Handles client-side interactions and enhancements
 */

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('HarpoTab loaded successfully!');

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // File upload preview
    setupFileUploadPreview();

    // Form validation
    setupFormValidation();

    // Auto-dismiss alerts
    autoDismissAlerts();
});


/**
 * Setup file upload preview
 */
function setupFileUploadPreview() {
    const fileInput = document.getElementById('file');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];

            if (file) {
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
                const fileType = file.type;

                console.log(`Fichier sélectionné: ${fileName} (${fileSize} MB)`);

                // Vérifier la taille du fichier (max 10 MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('Le fichier est trop volumineux. La taille maximale est de 10 MB.');
                    fileInput.value = '';
                    return;
                }

                // Vérifier le type de fichier
                const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
                if (!allowedTypes.includes(fileType)) {
                    alert('Type de fichier non autorisé. Utilisez PDF, PNG ou JPG.');
                    fileInput.value = '';
                    return;
                }

                // Afficher une indication visuelle
                showFileInfo(fileName, fileSize, fileType);
            }
        });
    }
}


/**
 * Display file information
 */
function showFileInfo(fileName, fileSize, fileType) {
    // Créer ou mettre à jour l'élément d'information
    let infoDiv = document.getElementById('file-info');

    if (!infoDiv) {
        infoDiv = document.createElement('div');
        infoDiv.id = 'file-info';
        infoDiv.className = 'alert alert-info mt-3';
        document.querySelector('form').appendChild(infoDiv);
    }

    let icon = '📄';
    if (fileType.includes('pdf')) {
        icon = '📕';
    } else if (fileType.includes('image')) {
        icon = '🖼️';
    }

    infoDiv.innerHTML = `
        <strong>${icon} Fichier sélectionné :</strong> ${fileName} (${fileSize} MB)
    `;
}


/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
}


/**
 * Auto-dismiss alerts after 5 seconds
 */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

    alerts.forEach(function(alert) {
        // Ne pas auto-dismiss les alertes d'erreur
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}


/**
 * Show loading spinner on button click
 */
function showLoadingSpinner(button, text = 'Chargement...') {
    if (!button) return;

    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${text}
    `;
}


/**
 * Copy tablature to clipboard
 */
function copyTablatureToClipboard() {
    const tablatureElements = document.querySelectorAll('.tab-notation-badge');
    const tablature = Array.from(tablatureElements)
        .map(el => el.textContent)
        .join(' ');

    navigator.clipboard.writeText(tablature).then(function() {
        alert('Tablature copiée dans le presse-papiers !');
    }, function(err) {
        console.error('Erreur lors de la copie :', err);
    });
}


/**
 * Print tablature
 */
function printTablature() {
    window.print();
}


/**
 * Download file with progress indication
 */
function downloadWithProgress(url, filename) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur de téléchargement');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Erreur de téléchargement :', error);
            alert('Erreur lors du téléchargement du fichier');
        });
}


/**
 * Smooth scroll to element
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}


/**
 * Toggle dark mode (future feature)
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
}


/**
 * Load user preferences
 */
function loadUserPreferences() {
    // Dark mode preference
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }

    // Notation style preference
    const notationStyle = localStorage.getItem('notationStyle');
    if (notationStyle) {
        const radio = document.querySelector(`input[name="notation_style"][value="${notationStyle}"]`);
        if (radio) {
            radio.checked = true;
        }
    }
}


/**
 * Save user preferences
 */
function saveUserPreferences() {
    // Save notation style
    const notationStyle = document.querySelector('input[name="notation_style"]:checked');
    if (notationStyle) {
        localStorage.setItem('notationStyle', notationStyle.value);
    }

    // Save tonality
    const tonality = document.querySelector('select[name="tonality"]');
    if (tonality) {
        localStorage.setItem('tonality', tonality.value);
    }
}


// Load preferences on page load
loadUserPreferences();

// Save preferences when form changes
document.addEventListener('change', function(e) {
    if (e.target.name === 'notation_style' || e.target.name === 'tonality') {
        saveUserPreferences();
    }
});


// Utility: Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}


// Expose some functions globally for inline onclick handlers
window.copyTablatureToClipboard = copyTablatureToClipboard;
window.printTablature = printTablature;
window.toggleDarkMode = toggleDarkMode;
