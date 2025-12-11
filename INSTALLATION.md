# HarpoTab - Guide d'Installation

## État Actuel du Système ✅

### Installé et Fonctionnel
- ✅ Python 3.13.7
- ✅ Flask 3.1.2 (serveur web)
- ✅ ReportLab 4.4.5 (génération PDF basique)
- ✅ Pillow 12.0.0 (traitement images)
- ✅ PDFPlumber 0.11.8 (lecture PDF)
- ✅ LilyPond 2.24.4 (génération partitions professionnelles)
- ✅ Environnement virtuel Python (venv)
- ✅ Tous les modules de base de HarpoTab

### À Installer (Fonctionnalités Avancées)
- ⚠️ **music21** - Support MusicXML (import depuis MuseScore/Finale)
- ⚠️ **Audiveris** - OCR musical RÉEL pour reconnaissance de partitions

## Installation Rapide

### 1. Installation Automatique (Recommandé)
```bash
# Exécuter le script d'installation complet
./setup.sh

# Vérifier l'installation
python check_system.py
```

### 2. Installation Manuelle

#### A. Dépendances Python de Base (✅ Déjà installées)
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

#### B. music21 (Support MusicXML)
```bash
source venv/bin/activate
pip install music21
```

**Pourquoi music21 ?**
- Import direct de fichiers MusicXML (.musicxml, .mxl, .xml)
- Zéro perte de données depuis MuseScore, Finale, Sibelius
- Extraction précise des notes, accords, métadonnées
- Requis pour parser les résultats d'Audiveris

#### C. Audiveris (OCR Musical RÉEL)
```bash
./install_audiveris.sh
```

**Ou manuellement selon votre système :**
```bash
# Manjaro / Arch Linux
yay -S audiveris

# Ubuntu / Debian
sudo apt-get install audiveris

# Fedora / RHEL
sudo dnf install audiveris

# macOS
brew install audiveris
```

**Pourquoi Audiveris ?**
- OCR musical RÉEL (reconnaissance optique de partitions)
- Standard open-source professionnel
- Analyse automatique de PDF et images de partitions
- Export MusicXML haute précision
- Sans Audiveris : données de démonstration uniquement

## Fonctionnalités par Niveau d'Installation

### Niveau 1 : Base (Installation Actuelle) ✅
**Fonctionnalités disponibles :**
- ✅ Upload de partitions (PDF, images)
- ✅ Génération tablature avec données de démo
- ✅ Support harmonica diatonique (10 trous) et chromatique (12 trous)
- ✅ 7 tonalités (C, G, A, D, E, F, Bb)
- ✅ 3 styles de notation (flèches, lettres, symboles)
- ✅ Génération PDF avec LilyPond (professionnel)
- ✅ Export MIDI et fichiers .ly
- ✅ Vérification de jouabilité
- ✅ Suggestions de transposition automatique
- ✅ Édition manuelle de tablature
- ✅ Playback audio MIDI

**Limitations :**
- ❌ Pas de support MusicXML (import depuis MuseScore/Finale)
- ❌ Pas d'OCR réel (utilise données de démo)

### Niveau 2 : Avec music21 (MusicXML)
**Fonctionnalités supplémentaires :**
- ✅ Import direct de fichiers MusicXML
- ✅ Extraction automatique titre, compositeur, tempo
- ✅ Parsing précis des notes et durées
- ✅ Support partitions multi-voix
- ✅ Zéro perte depuis logiciels de notation

### Niveau 3 : Complet (music21 + Audiveris) 🎯
**Toutes les fonctionnalités :**
- ✅ OCR RÉEL de partitions PDF/images
- ✅ Reconnaissance automatique des notes
- ✅ Import MusicXML + OCR + Démo
- ✅ Pipeline complet : Partition → OCR → MusicXML → Tablature

## Scripts Utiles

### check_system.py
Vérification complète de l'installation :
```bash
python check_system.py
```

Affiche :
- État de chaque dépendance
- Versions installées
- Dossiers requis
- Recommandations d'installation

### test_audiveris_ocr.py
Test de l'OCR Audiveris :
```bash
source venv/bin/activate
python test_audiveris_ocr.py
```

Vérifie :
- Installation d'Audiveris
- Fonctionnement de l'OCR
- Extraction de notes depuis une partition test

### setup.sh
Installation automatique complète :
```bash
./setup.sh
```

Effectue :
- Création venv
- Installation dépendances Python
- Vérification Audiveris et LilyPond
- Création dossiers requis
- Test des modules

## Vérification Post-Installation

### 1. Vérifier que tout fonctionne
```bash
# Vérification système
python check_system.py

# Test Audiveris (si installé)
python test_audiveris_ocr.py

# Lancer l'application
./run.sh
```

### 2. Tester l'application
```
Ouvrir : http://localhost:5000

Tests recommandés :
1. Upload PDF/image → Vérifier données de démo
2. Upload MusicXML → Vérifier parsing réel
3. Vérifier jouabilité et transposition
4. Éditer tablature manuellement
5. Télécharger PDF et MIDI
6. Écouter le playback
```

## Dépannage

### Problème : "Module non trouvé"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problème : "Port 5000 déjà utilisé"
Modifier `app.py`, ligne finale :
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Problème : "music21 n'installe pas"
Vérifier votre connexion internet, puis :
```bash
source venv/bin/activate
pip install --no-cache-dir music21
```

### Problème : "Audiveris non trouvé"
Vérifier qu'Audiveris est dans le PATH :
```bash
which audiveris
audiveris -version
```

Si non installé :
```bash
./install_audiveris.sh
```

### Problème : "Erreur lors de l'OCR"
Vérifications :
1. Audiveris installé : `which audiveris`
2. Java installé : `java -version` (requis par Audiveris)
3. Partition lisible (bonne qualité, pas de scan flou)

## Architecture des Dossiers

```
HarpoTab/
├── venv/                    # Environnement virtuel Python ✅
├── static/
│   ├── uploads/            # Partitions uploadées ✅
│   ├── output/             # PDF générés ✅
│   └── lilypond/           # Fichiers LilyPond ✅
├── modules/                # Code Python ✅
├── templates/              # Templates HTML ✅
├── data/                   # Mappings harmonica ✅
├── setup.sh               # Installation auto ✅
├── check_system.py        # Vérification système ✅
├── test_audiveris_ocr.py  # Test OCR ✅
├── install_audiveris.sh   # Installation Audiveris ✅
├── run.sh                 # Lancement app ✅
└── requirements.txt       # Dépendances Python ✅
```

## Prochaines Étapes

### Pour l'utilisateur :

1. **Si connexion internet OK :**
   ```bash
   source venv/bin/activate
   pip install music21
   ```

2. **Installer Audiveris (optionnel mais recommandé) :**
   ```bash
   ./install_audiveris.sh
   ```

3. **Vérifier l'installation :**
   ```bash
   python check_system.py
   ```

4. **Lancer l'application :**
   ```bash
   ./run.sh
   ```

### État du Projet

✅ **TERMINÉ :**
- Structure de base
- Support diatonique + chromatique
- Vérification jouabilité
- Transposition automatique
- Édition manuelle
- Playback MIDI
- Génération PDF LilyPond
- Support MusicXML (code prêt, module à installer)
- Intégration Audiveris (code prêt, logiciel à installer)

⏳ **À INSTALLER :**
- music21 (quand connexion stable)
- Audiveris (optionnel, pour OCR réel)

---

**Version :** 2.0 - Installation complète avec OCR réel
**Auteur :** HarpoTab Team
**Licence :** MIT
