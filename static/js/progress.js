/**
 * Gestion de la barre de progression en temps réel
 * Utilise Server-Sent Events (SSE) pour recevoir les updates
 */

class ProgressTracker {
    constructor(sessionId, containerId) {
        this.sessionId = sessionId;
        this.container = document.getElementById(containerId);
        this.eventSource = null;
        this.isComplete = false;
    }

    start() {
        // Afficher le container de progression
        if (this.container) {
            this.container.style.display = 'block';
        }

        // Créer la connexion SSE
        this.eventSource = new EventSource(`/progress/${this.sessionId}`);

        this.eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateProgress(data);

            // Fermer si terminé
            if (data.overall_progress >= 100) {
                this.complete(data);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('Erreur SSE:', error);
            this.eventSource.close();
            this.showError("Erreur de connexion au serveur");
        };
    }

    updateProgress(data) {
        // Mise à jour de la barre globale
        const overallBar = document.getElementById('overall-progress-bar');
        const overallText = document.getElementById('overall-progress-text');

        if (overallBar) {
            overallBar.style.width = `${data.overall_progress}%`;
            overallBar.setAttribute('aria-valuenow', data.overall_progress);
        }

        if (overallText) {
            overallText.textContent = `${data.overall_progress}%`;
        }

        // Mise à jour du temps écoulé
        const timeElapsed = document.getElementById('time-elapsed');
        if (timeElapsed) {
            timeElapsed.textContent = this.formatTime(data.elapsed_time);
        }

        // Mise à jour des étapes
        this.updateSteps(data.steps);
    }

    updateSteps(steps) {
        const stepsContainer = document.getElementById('steps-container');
        if (!stepsContainer) return;

        stepsContainer.innerHTML = '';

        steps.forEach((step, index) => {
            const stepElement = this.createStepElement(step, index + 1);
            stepsContainer.appendChild(stepElement);
        });
    }

    createStepElement(step, stepNumber) {
        const div = document.createElement('div');
        div.className = 'progress-step mb-3';

        // Icône et statut
        let statusIcon = '<i class="bi bi-circle"></i>';
        let statusClass = 'text-muted';

        if (step.status === 'completed') {
            statusIcon = '<i class="bi bi-check-circle-fill"></i>';
            statusClass = 'text-success';
        } else if (step.status === 'in_progress') {
            statusIcon = '<i class="bi bi-arrow-clockwise spin"></i>';
            statusClass = 'text-primary';
        } else if (step.status === 'error') {
            statusIcon = '<i class="bi bi-x-circle-fill"></i>';
            statusClass = 'text-danger';
        }

        div.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <span class="${statusClass} me-2">${statusIcon}</span>
                <strong>${stepNumber}. ${step.name}</strong>
                ${step.message ? `<small class="text-muted ms-2">${step.message}</small>` : ''}
            </div>
            ${step.substeps && step.substeps.length > 0 ? this.createSubsteps(step.substeps) : ''}
            ${step.progress > 0 ? `
                <div class="progress" style="height: 4px;">
                    <div class="progress-bar ${statusClass.replace('text-', 'bg-')}"
                         style="width: ${step.progress}%"
                         aria-valuenow="${step.progress}">
                    </div>
                </div>
            ` : ''}
        `;

        return div;
    }

    createSubsteps(substeps) {
        if (!substeps || substeps.length === 0) return '';

        const html = substeps.map(substep => {
            let icon = '·';
            let className = 'text-muted';

            if (substep.status === 'completed') {
                icon = '✓';
                className = 'text-success';
            } else if (substep.status === 'in_progress') {
                icon = '→';
                className = 'text-primary';
            } else if (substep.status === 'error') {
                icon = '✗';
                className = 'text-danger';
            }

            return `
                <div class="ms-4 small ${className}">
                    ${icon} ${substep.name}
                    ${substep.message ? `<span class="text-muted"> - ${substep.message}</span>` : ''}
                </div>
            `;
        }).join('');

        return `<div class="substeps">${html}</div>`;
    }

    complete(data) {
        if (this.isComplete) return;
        this.isComplete = true;

        if (this.eventSource) {
            this.eventSource.close();
        }

        // Afficher le message de succès
        const completionMessage = document.getElementById('completion-message');
        if (completionMessage) {
            completionMessage.style.display = 'block';
        }

        // Redirection automatique vers le résultat
        setTimeout(() => {
            // Récupérer le filename depuis la réponse ou l'URL
            const urlParams = new URLSearchParams(window.location.search);
            const filename = urlParams.get('filename');
            if (filename) {
                window.location.href = `/result/${filename}?success=true`;
            }
        }, 2000);
    }

    showError(message) {
        const errorContainer = document.getElementById('error-message');
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// CSS pour l'animation de rotation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spin {
        animation: spin 1s linear infinite;
        display: inline-block;
    }
`;
document.head.appendChild(style);
