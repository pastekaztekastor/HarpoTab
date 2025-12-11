# Guide d'Installation - HarpoTab

Guide rapide pour installer et lancer HarpoTab en développement.

## Prérequis

### Système d'exploitation
- Linux (Arch/Manjaro, Debian/Ubuntu, Fedora)
- macOS
- Windows (via WSL2 recommandé)

### Logiciels requis

#### Obligatoires
- **Python 3.9+** (testé avec Python 3.13.7)
- **Lilypond** : Génération de partitions
- **Poppler** : Conversion PDF vers images

#### Optionnels (Phase 1)
- **Audiveris** : OCR musical (sera nécessaire pour la conversion réelle)
- **Tesseract** : OCR texte pour métadonnées

## Installation Rapide

### Option 1 : Script automatique (recommandé)

```bash
# Cloner le projet
git clone https://github.com/mathurinc/harpotab.git
cd harpotab

# Lancer l'installation
chmod +x setup.sh
./setup.sh
```

Le script détecte automatiquement votre distribution et installe les dépendances.

### Option 2 : Installation manuelle

#### 1. Dépendances système

**Arch Linux / Manjaro :**
```bash
# Packages système
sudo pacman -S lilypond poppler python-pip

# Tesseract (optionnel)
sudo pacman -S tesseract tesseract-data-fra

# Audiveris (AUR)
yay -S audiveris
```

**Debian / Ubuntu :**
```bash
sudo apt update
sudo apt install -y lilypond poppler-utils python3-pip python3-venv

# Tesseract (optionnel)
sudo apt install -y tesseract-ocr tesseract-ocr-fra
```

**Fedora :**
```bash
sudo dnf install -y lilypond poppler-utils python3-pip

# Tesseract (optionnel)
sudo dnf install -y tesseract tesseract-langpack-fra
```

**macOS :**
```bash
brew install lilypond poppler python@3.9 tesseract
```

#### 2. Environnement Python

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

## Vérification de l'installation

### Vérifier Python

```bash
source venv/bin/activate
python -c "
import flask
from PIL import Image
import cv2
print('✅ Toutes les dépendances Python OK')
"
```

### Vérifier le système

```bash
# Lilypond
lilypond --version

# Poppler
pdftoppm -v

# Audiveris (optionnel)
audiveris --version
```

## Lancement de l'application

### Mode développement

```bash
# Méthode 1 : Script rapide
./run.sh

# Méthode 2 : Manuel
source venv/bin/activate
python app.py
```

L'application sera accessible sur **http://localhost:5000**

### Configuration

Créez un fichier `.env` à partir du template :

```bash
cp .env.example .env
```

Éditez `.env` selon vos besoins :

```bash
SECRET_KEY=votre-clé-secrète-ici
FLASK_DEBUG=true
AUDIVERIS_PATH=/usr/local/bin/audiveris
LILYPOND_PATH=lilypond
```

## Tests

```bash
source venv/bin/activate

# Lancer tous les tests
pytest

# Tests spécifiques
pytest tests/test_ocr.py
pytest tests/test_transposition.py
```

## Dépannage

### Erreur : `pdf2image` ne trouve pas Poppler

**Solution :** Installer Poppler :
```bash
# Arch/Manjaro
sudo pacman -S poppler

# Debian/Ubuntu
sudo apt install poppler-utils
```

### Erreur : `Module PIL not found`

**Solution :** Réinstaller Pillow :
```bash
source venv/bin/activate
pip install --upgrade Pillow
```

### Audiveris non trouvé

Audiveris n'est pas critique pour le développement initial. Vous pouvez :

1. **L'installer plus tard** quand vous implémenterez l'OCR
2. **Télécharger depuis GitHub** : https://github.com/Audiveris/audiveris/releases
3. **Sur Arch/Manjaro** : `yay -S audiveris`

### Port 5000 déjà utilisé

```bash
# Changer le port dans app.py ou :
export FLASK_RUN_PORT=8000
python app.py
```

## Structure après installation

```
HarpoTab/
├── venv/                   # Environnement virtuel (ignoré par git)
├── static/uploads/         # Uploads temporaires
├── static/outputs/         # PDFs générés
├── temp/                   # Fichiers temporaires
└── ...
```

## Docker (Alternative)

Si vous préférez utiliser Docker :

```bash
# Build l'image
docker build -t harpotab .

# Lancer le conteneur
docker run -p 5000:5000 harpotab
```

> **Note :** Le Dockerfile sera ajouté en Phase 2.

## Prochaines étapes

1. ✅ Installation terminée
2. ✅ Vérification OK
3. 🚀 Lancer l'application : `./run.sh`
4. 🌐 Ouvrir : http://localhost:5000
5. 📝 Consulter : `CAHIER_DES_CHARGES.pdf`

## Support

- **GitHub Issues** : https://github.com/mathurinc/harpotab/issues
- **Documentation** : README.md
- **Spécifications** : CAHIER_DES_CHARGES.pdf

---

**Dernière mise à jour** : 11 décembre 2025
