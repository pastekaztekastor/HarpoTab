#!/bin/bash
# Script de setup complet pour HarpoTab

echo "=========================================="
echo "   HarpoTab - Installation Complète"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Vérifier Python
echo "1. Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installé: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 n'est pas installé"
    exit 1
fi
echo ""

# 2. Créer/activer environnement virtuel
echo "2. Configuration de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    echo "  Création de l'environnement virtuel..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Environnement virtuel créé"
else
    echo -e "${GREEN}✓${NC} Environnement virtuel existe déjà"
fi
echo ""

# 3. Installer les dépendances Python
echo "3. Installation des dépendances Python..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
echo "  Installation en cours..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dépendances Python installées"
else
    echo -e "${YELLOW}⚠${NC} Problème lors de l'installation (vérifiez votre connexion)"
fi
echo ""

# 4. Vérifier Audiveris
echo "4. Vérification d'Audiveris (OCR musical)..."
if command -v audiveris &> /dev/null; then
    AUDIVERIS_VERSION=$(audiveris -version 2>&1 | head -n 1 || echo "version inconnue")
    echo -e "${GREEN}✓${NC} Audiveris est installé: $AUDIVERIS_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Audiveris n'est pas installé"
    echo ""
    echo "  Pour installer Audiveris:"
    echo "    ./install_audiveris.sh"
    echo ""
    echo "  Audiveris permet l'OCR musical RÉEL sur PDF/images"
    echo "  Sans Audiveris, l'application fonctionnera avec des données de démo"
fi
echo ""

# 5. Créer dossiers nécessaires
echo "5. Création des dossiers nécessaires..."
mkdir -p static/uploads
mkdir -p static/output
mkdir -p static/lilypond
echo -e "${GREEN}✓${NC} Dossiers créés"
echo ""

# 6. Vérifier LilyPond
echo "6. Vérification de LilyPond (génération PDF)..."
if command -v lilypond &> /dev/null; then
    LILYPOND_VERSION=$(lilypond --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} LilyPond est installé: $LILYPOND_VERSION"
else
    echo -e "${YELLOW}⚠${NC} LilyPond n'est pas installé"
    echo ""
    echo "  Pour installer LilyPond:"
    echo "    sudo pacman -S lilypond  # Manjaro/Arch"
    echo "    sudo apt install lilypond  # Ubuntu/Debian"
    echo ""
    echo "  LilyPond permet la génération de partitions professionnelles"
    echo "  Sans LilyPond, l'application utilisera ReportLab (basique)"
fi
echo ""

# 7. Test de l'application
echo "7. Test de l'application..."
if python3 -c "from modules.pdf_reader import check_audiveris_installed" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Modules Python OK"
else
    echo -e "${RED}✗${NC} Problème avec les modules Python"
fi
echo ""

# Résumé
echo "=========================================="
echo "   Installation terminée !"
echo "=========================================="
echo ""
echo "Pour lancer l'application:"
echo "  ./run.sh"
echo ""
echo "Pour tester l'OCR Audiveris:"
echo "  source venv/bin/activate"
echo "  python test_audiveris_ocr.py"
echo ""
echo "Documentation:"
echo "  README.md"
echo ""
