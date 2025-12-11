# HarpoTab - Convertisseur Partition → Tablature Harmonica

Application web Flask pour convertir des partitions musicales en tablatures d'harmonica diatonique.

## Fonctionnalités

### Format Pédagogique Innovant
- **Tablature à 2 lignes** : Format visuel clair avec ligne soufflée (↑) et ligne aspirée (↓)
- **Notation musicale** : Affiche la durée des notes (ronde, blanche, noire, croche)
- **Numéros de trou** : Indiqués directement sur les notes pour faciliter l'apprentissage
- **Partition originale incluse** : Affichée au-dessus de la tablature dans le PDF

### Autres fonctionnalités
- Upload de partitions PDF ou images (PNG, JPG)
- Support de l'harmonica diatonique 10 trous
- Multiples tonalités : C, G, A, D, E, F, Bb
- 3 styles de notation :
  - Flèches : `4↑ 5↓`
  - Lettres : `4B 5D`
  - Symboles : `+4 -5`
- Génération de PDF professionnel de la tablature
- Interface responsive avec Bootstrap 5
- Visualisation web interactive avant téléchargement

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner ou télécharger le projet

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python app.py
```

4. Ouvrir votre navigateur à l'adresse :
```
http://localhost:5000
```

## Utilisation

1. **Upload** : Sélectionnez votre partition (PDF ou image)
2. **Configuration** :
   - Choisissez le type d'harmonica (Diatonique 10 trous)
   - Sélectionnez la tonalité (C, G, A, D, E, F, Bb)
   - Choisissez le style de notation (flèches, lettres, symboles)
3. **Conversion** : Cliquez sur "Continuer" puis "Lancer la conversion"
4. **Téléchargement** : Récupérez votre tablature en PDF

## Structure du Projet

```
HarpoTab/
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
│
├── data/
│   └── harmonica_maps.json    # Mappings notes → tablature
│
├── modules/
│   ├── pdf_reader.py          # Extraction données musicales
│   ├── music_parser.py        # Parsing des notes
│   ├── harmonica.py           # Conversion en tablature
│   └── pdf_generator.py       # Génération PDF
│
├── static/
│   ├── css/
│   │   └── style.css          # Styles personnalisés
│   ├── js/
│   │   └── main.js            # Scripts JavaScript
│   └── uploads/               # Fichiers uploadés (créé automatiquement)
│
└── templates/
    ├── base.html              # Template de base
    ├── index.html             # Page d'accueil
    ├── convert.html           # Page de conversion
    └── result.html            # Page de résultat
```

## Technologies Utilisées

### Backend
- **Flask 3.0** : Framework web Python
- **music21 9.1** : Analyse musicale
- **ReportLab 4.0** : Génération de PDF
- **PyPDF2 3.0** : Lecture de PDF
- **Pillow 10.1** : Traitement d'images
- **OpenCV 4.8** : Analyse d'images

### Frontend
- **Bootstrap 5.3** : Framework CSS
- **Bootstrap Icons** : Icônes
- **JavaScript ES6** : Interactions client

## OCR Musical - Reconnaissance Automatique ✨

**HarpoTab intègre maintenant un VRAI OCR musical avec Audiveris !**

### Méthodes de reconnaissance (par ordre de priorité)

1. **MusicXML direct** (.musicxml, .mxl, .xml)
   - ✅ Import parfait depuis MuseScore, Finale, Sibelius
   - ✅ Zéro perte de données
   - ✅ Métadonnées complètes (titre, compositeur, tempo)

2. **Audiveris OCR** (PDF et images) - **NOUVEAU !**
   - ✅ Reconnaissance optique RÉELLE des partitions
   - ✅ Standard open-source professionnel
   - ✅ Export MusicXML automatique
   - ✅ Haute précision
   - ⚙️ Installation : `./install_audiveris.sh`

3. **Données de démonstration** (fallback)
   - Utilisé si Audiveris n'est pas installé
   - Permet de tester l'application

### Installation d'Audiveris

```bash
# Installation automatique
./install_audiveris.sh

# Ou manuellement selon votre système :
# Manjaro/Arch
yay -S audiveris

# Ubuntu/Debian
sudo apt-get install audiveris

# macOS
brew install audiveris
```

### Test de l'OCR

```bash
python test_audiveris_ocr.py
```

## Format de Tablature Pédagogique

### Portée à 2 Lignes

HarpoTab utilise un **format innovant à 2 lignes** conçu pour l'apprentissage :

```
Partition originale (en haut du PDF)
↓

  ↑ SOUFFLÉ    ○   ○       ○
             1   2       4
  ─────────────────────────────────  (Ligne supérieure)

  ↓ ASPIRÉ         ○   ○       ○
                 1   2       4
  ─────────────────────────────────  (Ligne inférieure)
```

### Avantages Pédagogiques

1. **Clarté visuelle** : Séparation immédiate entre notes soufflées et aspirées
2. **Apprentissage facilité** : Les numéros de trou sont directement sur les notes
3. **Notation musicale** : Les formes de notes indiquent la durée (ronde, blanche, noire, croche)
4. **Partition intégrée** : La partition originale est au-dessus pour apprendre en comparant
5. **Organisation par mesures** : Même structure que la partition traditionnelle

### Comment Lire la Tablature

- **Ligne du HAUT** = Notes à **SOUFFLER** (↑)
- **Ligne du BAS** = Notes à **ASPIRER** (↓)
- **Chiffres** = Numéro du trou (1 à 10)
- **Forme des notes** :
  - ○ vide = Ronde ou Blanche (notes longues)
  - ● pleine = Noire ou Croche (notes courtes)
  - ♪ avec crochet = Croche ou Double-croche

### Exemple : Gamme de Do

```
Mesure 1:
  ↑ SOUFFLÉ    1       2
  ↓ ASPIRÉ         1       2

Mesure 2:
  ↑ SOUFFLÉ    4       5
  ↓ ASPIRÉ         4       5

Mesure 3:
  ↑ SOUFFLÉ    6       7
  ↓ ASPIRÉ         6       7
```

Traduction : Trou 1 soufflé (Do), trou 1 aspiré (Ré), trou 2 soufflé (Mi), etc.

## Exemples de Mapping

### Harmonica Diatonique en C

| Trou | Soufflé (↑) | Aspiré (↓) |
|------|-------------|------------|
| 1    | C4          | D4         |
| 2    | E4          | G4         |
| 3    | G3          | B4         |
| 4    | C5          | D5         |
| 5    | E5          | F5         |
| 6    | G5          | A5         |
| 7    | C6          | B5         |
| 8    | E6          | D6         |
| 9    | G6          | F6         |
| 10   | C7          | A6         |

## Styles de Notation

### Flèches (arrows)
- `4↑` : Souffler dans le trou 4
- `5↓` : Aspirer dans le trou 5

### Lettres (letters)
- `4B` : Blow (souffler) dans le trou 4
- `5D` : Draw (aspirer) dans le trou 5

### Symboles (symbols)
- `+4` : Souffler dans le trou 4
- `-5` : Aspirer dans le trou 5

## Configuration

### Modifier la clé secrète Flask
Dans `app.py`, ligne 13 :
```python
app.config['SECRET_KEY'] = 'votre-cle-secrete-ici-changez-moi'
```

### Modifier la taille maximale des fichiers
Dans `app.py`, ligne 15 :
```python
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
```

## Développement Futur

### Phase 2 - Améliorations prévues
- [ ] OCR musical réel (Audiveris)
- [ ] Support harmonica chromatique
- [ ] Édition manuelle de la tablature
- [ ] Support MusicXML
- [ ] Export en formats multiples (MIDI, ABC, etc.)
- [ ] Playback audio
- [ ] Annotations et métronome
- [ ] Partage de tablatures

## Dépannage

### Erreur : Module non trouvé
```bash
pip install -r requirements.txt
```

### Port 5000 déjà utilisé
Modifier dans `app.py`, dernière ligne :
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Erreur lors de l'upload
Vérifier que le dossier `static/uploads` existe et a les bonnes permissions :
```bash
mkdir -p static/uploads
chmod 755 static/uploads
```

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push sur la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## Licence

Ce projet est open-source et disponible sous licence MIT.

## Auteur

Créé avec Flask et Bootstrap

## Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation Flask : https://flask.palletsprojects.com/

## Remerciements

- Bootstrap pour le framework CSS
- ReportLab pour la génération de PDF
- La communauté Python pour les excellentes bibliothèques
