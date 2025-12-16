# =============================================================================
# Dockerfile - HarpoTab App (léger, sans Audiveris)
# =============================================================================
# Image légère pour l'application Flask
# Audiveris est dans un conteneur séparé (voir docker/audiveris/)
#
# Build: docker build -t harpotab-app .
# Run:   docker-compose up
# =============================================================================

FROM python:3.11-slim

# Éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1

# =============================================================================
# Installation des dépendances système légères
# =============================================================================

RUN apt-get update && apt-get install -y \
    # Poppler (pour pdf2image)
    poppler-utils \
    # Lilypond (génération de partitions)
    lilypond \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Installation des dépendances Python
# =============================================================================

WORKDIR /app

# Copier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Copie du code source
# =============================================================================

COPY . /app/

# Créer les dossiers nécessaires
RUN mkdir -p temp/ocr_output static/uploads static/outputs

# =============================================================================
# Variables d'environnement
# =============================================================================

ENV PYTHONPATH=/app
ENV AUDIVERIS_SERVICE_URL=http://audiveris:8080

# =============================================================================
# Port d'exposition
# =============================================================================

EXPOSE 5000

# =============================================================================
# Point d'entrée
# =============================================================================

CMD ["python", "app.py"]
