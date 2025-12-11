#!/bin/bash

# Script d'installation de LilyPond pour HarpoTab

echo "=========================================="
echo "  Installation de LilyPond"
echo "=========================================="
echo ""

# Détection de l'OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Système Linux détecté"
    echo ""

    # Vérifier si apt est disponible (Debian/Ubuntu)
    if command -v apt-get &> /dev/null; then
        echo "Installation via apt-get..."
        sudo apt-get update
        sudo apt-get install -y lilypond

    # Vérifier si pacman est disponible (Arch/Manjaro)
    elif command -v pacman &> /dev/null; then
        echo "Installation via pacman..."
        sudo pacman -S --noconfirm lilypond

    # Vérifier si dnf est disponible (Fedora)
    elif command -v dnf &> /dev/null; then
        echo "Installation via dnf..."
        sudo dnf install -y lilypond

    else
        echo "Gestionnaire de paquets non supporté"
        echo "Installez LilyPond manuellement depuis : https://lilypond.org/download.html"
        exit 1
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Système macOS détecté"
    echo ""

    # Vérifier si Homebrew est installé
    if command -v brew &> /dev/null; then
        echo "Installation via Homebrew..."
        brew install lilypond
    else
        echo "Homebrew n'est pas installé"
        echo "Installez Homebrew depuis : https://brew.sh"
        echo "Puis exécutez : brew install lilypond"
        exit 1
    fi

else
    echo "Système non supporté : $OSTYPE"
    echo "Téléchargez LilyPond depuis : https://lilypond.org/download.html"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Vérification de l'installation"
echo "=========================================="
echo ""

if command -v lilypond &> /dev/null; then
    lilypond --version | head -3
    echo ""
    echo "✓ LilyPond installé avec succès !"
else
    echo "✗ Erreur : LilyPond n'a pas été installé correctement"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Installation terminée !"
echo "=========================================="
echo ""
echo "Vous pouvez maintenant utiliser LilyPond pour générer"
echo "des partitions professionnelles avec HarpoTab."
echo ""
