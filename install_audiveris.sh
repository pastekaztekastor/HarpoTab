#!/bin/bash
# Script d'installation d'Audiveris pour OCR musical

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                Installation Audiveris - OCR Musical              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Détecter le système d'exploitation
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Impossible de détecter le système d'exploitation"
    exit 1
fi

echo "📋 Système détecté : $OS"
echo ""

# Installation selon le système
case "$OS" in
    manjaro|arch)
        echo "🔧 Installation via AUR (yay)..."
        if command -v yay &> /dev/null; then
            yay -S audiveris --noconfirm
        else
            echo "❌ yay n'est pas installé. Installation manuelle requise."
            echo "   Installez yay puis relancez ce script"
            exit 1
        fi
        ;;

    ubuntu|debian|linuxmint)
        echo "🔧 Installation via apt..."
        sudo apt-get update
        sudo apt-get install -y audiveris
        ;;

    fedora|rhel|centos)
        echo "🔧 Installation via dnf..."
        sudo dnf install -y audiveris
        ;;

    *)
        echo "⚠️  Système non supporté automatiquement : $OS"
        echo ""
        echo "Installation manuelle requise :"
        echo "1. Téléchargez Audiveris : https://github.com/Audiveris/audiveris/releases"
        echo "2. Extrayez l'archive"
        echo "3. Ajoutez le binaire au PATH"
        echo ""
        exit 1
        ;;
esac

# Vérification de l'installation
echo ""
echo "🔍 Vérification de l'installation..."
if command -v audiveris &> /dev/null; then
    echo "✅ Audiveris installé avec succès !"
    echo ""
    audiveris --version || audiveris -v || echo "Version : installé (commande version non disponible)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✨ Installation terminée !"
    echo ""
    echo "HarpoTab peut maintenant utiliser Audiveris pour l'OCR musical réel."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ Erreur : Audiveris n'est pas accessible"
    echo "   Vérifiez l'installation manuellement"
    exit 1
fi
