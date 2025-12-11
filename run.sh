#!/bin/bash

# HarpoTab - Script de lancement rapide

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Lancez d'abord: ./setup.sh"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Charger les variables d'environnement si .env existe
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Lancer l'application Flask
echo "🚀 Lancement de HarpoTab..."
echo "📍 Interface: http://localhost:5000"
echo ""
python app.py
