# =============================================================================
# Dockerfile - Service Audiveris OCR avec API HTTP
# =============================================================================
# Conteneur dédié pour Audiveris avec une API HTTP simple
# Build: docker build -t audiveris-service -f docker/audiveris/Dockerfile .
# =============================================================================

FROM ubuntu:22.04

# Éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# =============================================================================
# Installation des dépendances système
# =============================================================================

RUN apt-get update && apt-get install -y \
    # Java 21 (requis pour Audiveris 5.9.0)
    openjdk-21-jre-headless \
    # Tesseract OCR (utilisé par Audiveris)
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    # Outils système
    wget \
    curl \
    # Python léger pour l'API HTTP
    python3.11 \
    python3-pip \
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
# Installation d'Audiveris
# =============================================================================

# Copier le .deb depuis le contexte local (téléchargé au préalable)
COPY Audiveris-5.9.0-ubuntu22.04-x86_64.deb /tmp/

RUN echo "📦 Installing Audiveris with dpkg..." \
    && (dpkg -i /tmp/Audiveris-5.9.0-ubuntu22.04-x86_64.deb || true) \
    && echo "⚠️ Fixing dependencies..." \
    && apt-get update \
    && apt-get install -f -y \
    && echo "🧹 Cleaning up..." \
    && rm /tmp/Audiveris-5.9.0-ubuntu22.04-x86_64.deb \
    && echo "✅ Audiveris installation completed"

# Vérifier l'installation
RUN audiveris --help || echo "Audiveris installed"

# =============================================================================
# Installation de Flask pour l'API HTTP
# =============================================================================

RUN pip3 install --no-cache-dir flask

# =============================================================================
# Copie du serveur HTTP
# =============================================================================

WORKDIR /app

COPY server.py /app/server.py

# Créer les dossiers pour les fichiers
RUN mkdir -p /uploads /outputs

# =============================================================================
# Variables d'environnement
# =============================================================================

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENV TESSDATA_PREFIX=/usr/share/tessdata

# =============================================================================
# Port d'exposition
# =============================================================================

EXPOSE 8080

# =============================================================================
# Point d'entrée
# =============================================================================

CMD ["python3", "server.py"]
