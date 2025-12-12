# =============================================================================
# Dockerfile pour HarpoTab avec Audiveris
# =============================================================================
# Image de base pour tests d'intégration complets incluant Audiveris OCR
# Utilisé pour la CI/CD et le déploiement
#
# Build: docker build -t harpotab:latest .
# Run:   docker run -it harpotab:latest pytest tests/
# =============================================================================

FROM ubuntu:22.04

# Éviter les prompts interactifs pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# =============================================================================
# ÉTAPE 1: Installation des dépendances système
# =============================================================================

RUN apt-get update && apt-get install -y \
    # Python et pip
    python3.11 \
    python3-pip \
    python3.11-venv \
    # Java 21 (requis pour Audiveris 5.9.0)
    openjdk-21-jre-headless \
    # Tesseract OCR (optionnel pour Audiveris)
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    # Poppler (pour pdf2image)
    poppler-utils \
    # Lilypond (génération de partitions)
    lilypond \
    # Outils système
    wget \
    curl \
    unzip \
    ca-certificates \
    # Dépendances graphiques pour Audiveris (mode headless)
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libfreetype6 \
    fontconfig \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# ÉTAPE 2: Installation d'Audiveris
# =============================================================================

# Télécharger et installer Audiveris 5.9.0
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.9.0/Audiveris_5.9.0.deb \
    && dpkg -i Audiveris_5.9.0.deb || apt-get install -f -y \
    && rm Audiveris_5.9.0.deb

# Vérifier l'installation d'Audiveris
RUN audiveris --help || echo "Audiveris installed but may need X11 for some features"

# =============================================================================
# ÉTAPE 3: Configuration de l'environnement Python
# =============================================================================

# Créer un lien symbolique python -> python3.11
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# =============================================================================
# ÉTAPE 4: Installation des dépendances Python HarpoTab
# =============================================================================

# Copier requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# =============================================================================
# ÉTAPE 5: Configuration de l'application
# =============================================================================

# Créer le répertoire de travail
WORKDIR /app

# Copier le code source
COPY . /app/

# Créer les dossiers nécessaires
RUN mkdir -p temp/ocr_output static/uploads static/outputs

# =============================================================================
# ÉTAPE 6: Configuration des variables d'environnement
# =============================================================================

# Java pour Audiveris
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Tesseract
ENV TESSDATA_PREFIX=/usr/share/tessdata

# Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# =============================================================================
# ÉTAPE 7: Tests de santé
# =============================================================================

# Vérifier que tout est bien installé
RUN python --version && \
    java --version && \
    lilypond --version && \
    tesseract --version && \
    pip list | grep -E "pytest|flask|pillow"

# =============================================================================
# ÉTAPE 8: Point d'entrée
# =============================================================================

# Par défaut, lancer les tests
CMD ["pytest", "tests/", "-v", "--tb=short"]

# Pour lancer l'application Flask:
# CMD ["python", "app.py"]

# Pour un shell interactif:
# docker run -it harpotab:latest /bin/bash
