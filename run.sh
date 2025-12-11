#!/bin/bash

# HarpoTab - Script de lancement rapide

echo "=========================================="
echo "  HarpoTab - Convertisseur Partition"
echo "  vers Tablature Harmonica"
echo "=========================================="
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 détecté"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo ""
    echo "⚠️  Environnement virtuel non trouvé"
    echo "   Exécutez d'abord : ./setup.sh"
    exit 1
fi

echo "✓ Environnement virtuel détecté"

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si les dépendances sont installées
if ! python -c "import flask" &> /dev/null; then
    echo ""
    echo "⚠️  Dépendances manquantes"
    echo "   Installation en cours..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
fi

echo "✓ Dépendances installées"
echo ""
echo "🚀 Démarrage de l'application..."
echo "   URL: http://localhost:5000"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

# Lancer l'application
python app.py
