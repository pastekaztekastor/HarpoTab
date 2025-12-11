#!/bin/bash

# HarpoTab - Script d'installation
# Auteur: Mathurin C.
# Description: Installation automatique des dépendances pour HarpoTab

set -e  # Arrêter en cas d'erreur

echo "================================================"
echo "  HarpoTab - Installation"
echo "================================================"
echo ""

# Détection de l'OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/arch-release ]; then
        OS="arch"
    elif [ -f /etc/debian_version ]; then
        OS="debian"
    elif [ -f /etc/fedora-release ]; then
        OS="fedora"
    else
        OS="unknown"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    OS="unknown"
fi

echo "Système détecté: $OS"
echo ""

# Installation des dépendances système
install_system_deps() {
    echo "=== Installation des dépendances système ==="

    case $OS in
        arch)
            echo "Installation pour Arch Linux / Manjaro..."

            # Vérifier si yay est installé
            if ! command -v yay &> /dev/null; then
                echo "⚠️  yay n'est pas installé. Installation de yay..."
                sudo pacman -S --needed --noconfirm git base-devel
                git clone https://aur.archlinux.org/yay.git /tmp/yay
                cd /tmp/yay
                makepkg -si --noconfirm
                cd -
            fi

            # Installer les paquets
            echo "Installation de Lilypond, Poppler, Tesseract..."
            sudo pacman -S --needed --noconfirm lilypond poppler tesseract tesseract-data-fra python-pip

            # Audiveris (AUR)
            echo "Installation d'Audiveris..."
            yay -S --needed --noconfirm audiveris
            ;;

        debian)
            echo "Installation pour Debian / Ubuntu..."
            sudo apt update
            sudo apt install -y lilypond poppler-utils tesseract-ocr tesseract-ocr-fra python3-pip python3-venv

            echo "⚠️  Note: Audiveris doit être installé manuellement depuis:"
            echo "    https://github.com/Audiveris/audiveris/releases"
            ;;

        fedora)
            echo "Installation pour Fedora..."
            sudo dnf install -y lilypond poppler-utils tesseract tesseract-langpack-fra python3-pip

            echo "⚠️  Note: Audiveris doit être installé manuellement depuis:"
            echo "    https://github.com/Audiveris/audiveris/releases"
            ;;

        macos)
            echo "Installation pour macOS..."

            if ! command -v brew &> /dev/null; then
                echo "❌ Homebrew n'est pas installé. Installez-le depuis https://brew.sh"
                exit 1
            fi

            brew install lilypond poppler tesseract python@3.9

            echo "⚠️  Note: Audiveris doit être installé manuellement depuis:"
            echo "    https://github.com/Audiveris/audiveris/releases"
            ;;

        *)
            echo "❌ Système non supporté automatiquement."
            echo "Installez manuellement:"
            echo "  - Python 3.9+"
            echo "  - Lilypond"
            echo "  - Poppler"
            echo "  - Audiveris"
            echo "  - Tesseract (optionnel)"
            exit 1
            ;;
    esac

    echo "✅ Dépendances système installées"
    echo ""
}

# Vérification des dépendances
check_dependencies() {
    echo "=== Vérification des dépendances ==="

    local missing=0

    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "✅ Python $PYTHON_VERSION"
    else
        echo "❌ Python 3 non trouvé"
        missing=1
    fi

    # Lilypond
    if command -v lilypond &> /dev/null; then
        LILY_VERSION=$(lilypond --version | head -n1 | cut -d' ' -f3)
        echo "✅ Lilypond $LILY_VERSION"
    else
        echo "❌ Lilypond non trouvé"
        missing=1
    fi

    # Audiveris
    if command -v audiveris &> /dev/null; then
        echo "✅ Audiveris installé"
    else
        echo "⚠️  Audiveris non trouvé (requis pour OCR musical)"
        echo "    Installez depuis: https://github.com/Audiveris/audiveris/releases"
    fi

    # Poppler (pdftoppm)
    if command -v pdftoppm &> /dev/null; then
        echo "✅ Poppler installé"
    else
        echo "❌ Poppler non trouvé"
        missing=1
    fi

    # Tesseract (optionnel)
    if command -v tesseract &> /dev/null; then
        echo "✅ Tesseract installé (optionnel)"
    else
        echo "ℹ️  Tesseract non installé (optionnel)"
    fi

    echo ""

    if [ $missing -eq 1 ]; then
        echo "❌ Certaines dépendances sont manquantes."
        read -p "Voulez-vous les installer automatiquement? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_system_deps
        else
            echo "Installation annulée."
            exit 1
        fi
    fi
}

# Installation de l'environnement Python
setup_python_env() {
    echo "=== Configuration environnement Python ==="

    # Créer environnement virtuel
    if [ ! -d "venv" ]; then
        echo "Création de l'environnement virtuel..."
        python3 -m venv venv
        echo "✅ Environnement virtuel créé"
    else
        echo "ℹ️  Environnement virtuel déjà existant"
    fi

    # Activer venv
    source venv/bin/activate

    # Upgrade pip
    echo "Mise à jour de pip..."
    pip install --upgrade pip

    # Installer les dépendances
    echo "Installation des dépendances Python..."
    pip install -r requirements.txt

    echo "✅ Dépendances Python installées"
    echo ""
}

# Créer les dossiers nécessaires
setup_directories() {
    echo "=== Configuration des dossiers ==="

    mkdir -p static/uploads
    mkdir -p static/outputs
    mkdir -p temp

    echo "✅ Dossiers créés"
    echo ""
}

# Configuration finale
finalize() {
    echo "================================================"
    echo "  ✅ Installation terminée !"
    echo "================================================"
    echo ""
    echo "Pour lancer HarpoTab:"
    echo ""
    echo "  1. Activez l'environnement virtuel:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. Lancez l'application:"
    echo "     python app.py"
    echo ""
    echo "  3. Ouvrez votre navigateur:"
    echo "     http://localhost:5000"
    echo ""
    echo "Documentation: README.md"
    echo "Cahier des charges: CAHIER_DES_CHARGES.md"
    echo ""
}

# Exécution principale
main() {
    check_dependencies
    setup_python_env
    setup_directories
    finalize
}

main
