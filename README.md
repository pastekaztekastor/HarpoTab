# HarpoTab

Convertisseur automatique de partitions musicales en tablatures pour harmonica.

## Description

HarpoTab est un outil qui permet de convertir des partitions de piano (ou autres instruments) en tablatures adaptées pour harmonica diatonique ou chromatique. L'application extrait automatiquement la mélodie principale, effectue une transposition intelligente si nécessaire, et génère un PDF professionnel avec la partition et la tablature synchronisées.

## Fonctionnalités

### Phase 1 (En développement)
- 📄 **Lecture de partitions** : Support PDF et images (JPEG, PNG)
- 🎵 **OCR musical** : Extraction automatique via Audiveris
- 🎼 **Isolation de mélodie** : Extraction de la ligne mélodique principale
- 🔄 **Transposition automatique** : Adaptation intelligente à votre harmonica
- 🎹 **Support multi-harmonica** : Diatoniques (C, D, G, etc.) et chromatiques
- 📝 **Tablature détaillée** : Numéros de trous, sens du souffle, techniques (bends)
- 🎨 **Génération PDF** : Partition + tablature via Lilypond
- 🌐 **Interface web** : Application Flask avec Bootstrap 5

### Phase 2 (À venir)
- 🎧 Extraction depuis fichiers audio (MP3)
- 📹 Conversion depuis liens YouTube
- 🎤 Analyse spectrale avancée

## Architecture

```
HarpoTab/
├── app.py                      # Application Flask principale
├── config.py                   # Configuration
├── requirements.txt            # Dépendances Python
├── CAHIER_DES_CHARGES.md       # Spécifications complètes
│
├── modules/                    # Modules de traitement
│   ├── ocr_reader.py           # OCR musical (Audiveris)
│   ├── melody_extractor.py     # Extraction mélodie
│   ├── music_analyzer.py       # Analyse musicale
│   ├── transposer.py           # Transposition
│   ├── harmonica_mapper.py     # Mapping notes → tablature
│   └── lilypond_generator.py   # Génération PDF
│
├── data/
│   └── harmonica_maps/         # Mappings par type/tonalité
│
├── static/                     # Assets web
│   ├── css/
│   ├── js/
│   └── uploads/
│
└── templates/                  # Templates HTML
```

## Installation

### Prérequis

- **Python 3.9+**
- **Audiveris** : OCR musical
- **Lilypond** : Génération de partitions
- **Poppler** : Pour pdf2image

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/mathurinc/harpotab.git
cd harpotab

# Lancer le script d'installation
chmod +x setup.sh
./setup.sh
```

### Installation manuelle

#### 1. Dépendances système (Arch Linux / Manjaro)

```bash
# Audiveris
yay -S audiveris

# Lilypond
sudo pacman -S lilypond

# Poppler (pdf2image)
sudo pacman -S poppler

# Tesseract (optionnel)
sudo pacman -S tesseract tesseract-data-fra
```

#### 2. Environnement Python

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer Flask
python app.py
```

L'application sera accessible sur `http://localhost:5000`

### Workflow

1. **Accédez à l'interface web**
2. **Uploadez votre partition** (PDF ou image)
3. **Sélectionnez votre harmonica** (type et tonalité)
4. **Cliquez sur "Convertir"**
5. **Téléchargez le PDF** généré avec partition + tablature

## Configuration

La configuration se trouve dans `config.py`. Vous pouvez personnaliser :

- Chemins vers Audiveris et Lilypond
- Taille maximale des uploads
- Options de transposition
- Format des PDF générés

Variables d'environnement :

```bash
export AUDIVERIS_PATH=/path/to/audiveris
export LILYPOND_PATH=/path/to/lilypond
export FLASK_DEBUG=true
export SECRET_KEY=your-secret-key
```

## Développement

### Structure des modules

Chaque module a une responsabilité unique :

- **ocr_reader** : Interface avec Audiveris
- **melody_extractor** : Isolation de la mélodie
- **music_analyzer** : Détection tonalité, accords, tessiture
- **transposer** : Algorithmes de transposition
- **harmonica_mapper** : Conversion notes → tablature
- **lilypond_generator** : Création des fichiers Lilypond

### Tests

```bash
# Lancer les tests
pytest tests/

# Tests spécifiques
pytest tests/test_ocr.py
pytest tests/test_transposition.py
```

### Ajouter un nouveau type d'harmonica

1. Créer le fichier de mapping JSON dans `data/harmonica_maps/`
2. Ajouter le type dans `config.py` → `HARMONICA_TYPES`
3. Mettre à jour le mapping dans `harmonica_mapper.py`

Exemple de mapping :

```json
{
  "type": "diatonic",
  "key": "D",
  "notes": {
    "1": {
      "blow": {"note": "D", "octave": 4},
      "draw": {"note": "E", "octave": 4}
    }
  }
}
```

## Dépendances

### Python

- **flask** : Framework web
- **pillow** : Traitement d'images
- **pdf2image** : Conversion PDF
- **opencv-python** : Prétraitement images (optionnel)

### Systèmes

- **Audiveris** : OCR musical
- **Lilypond** : Génération partitions
- **Poppler** : Utilitaires PDF

## Roadmap

- [x] Cahier des charges
- [x] Structure du projet
- [x] Interface web de base
- [ ] **Intégration Audiveris**
- [ ] Extraction de mélodie
- [ ] Algorithme de transposition
- [ ] Génération Lilypond
- [ ] Tests unitaires
- [ ] Documentation complète
- [ ] Phase 2 : Audio/YouTube

## Contribuer

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Commitez (`git commit -m 'Ajout fonctionnalité'`)
4. Pushez (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## Licence

MIT License - Voir [LICENSE](LICENSE)

## Auteur

**Mathurin C.** - [GitHub](https://github.com/mathurinc)

## Remerciements

- [Audiveris](https://github.com/Audiveris/audiveris) : OCR musical open-source
- [Lilypond](https://lilypond.org/) : Gravure musicale professionnelle
- [Flask](https://flask.palletsprojects.com/) : Framework web Python
- Communauté des harmonicistes

## Support

Pour signaler un bug ou demander une fonctionnalité, ouvrez une [issue sur GitHub](https://github.com/mathurinc/harpotab/issues).

---

**Version actuelle** : 0.1.0 (Alpha)
**Statut** : En développement actif
