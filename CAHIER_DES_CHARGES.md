# Cahier des Charges - HarpoTab

## 1. Présentation du Projet

### 1.1 Objectif
HarpoTab est un outil de conversion automatique de partitions musicales et fichiers audio en tablatures pour harmonica. Le système extrait la mélodie principale et génère une tablature adaptée au type d'harmonica sélectionné, avec transposition automatique si nécessaire.

### 1.2 Portée
- **Phase 1** : Conversion de partitions (PDF, JPEG) vers tablature harmonica
- **Phase 2** : Extraction de mélodie depuis fichiers audio (MP3) et vidéos YouTube

---

## 2. Spécifications Fonctionnelles

### 2.1 Entrées Supportées

#### Phase 1 (Prioritaire)
- **PDF** : Partitions musicales au format PDF
- **JPEG/PNG** : Images de partitions scannées ou photographiées

#### Phase 2 (Développement ultérieur)
- **MP3** : Fichiers audio (extraction de mélodie)
- **YouTube** : Liens vers vidéos (extraction audio puis mélodie)

### 2.2 Types d'Harmonica Supportés

L'utilisateur doit pouvoir sélectionner :
- **Harmonica diatonique** (Richter 10 trous)
  - Tonalités : C, D, E, F, G, A, Bb, etc.
- **Harmonica chromatique** (12/16 trous)
- **Autres types** (selon évolution du projet)

### 2.3 Sortie Générée

Un **PDF** généré via Lilypond contenant :

1. **Portée musicale** : Mélodie en notation classique
2. **Tablature harmonica** : Positionnée sous la portée, indiquant :
   - Numéro de trou
   - Sens du souffle (aspiration/expiration)
   - Techniques (bend, overblow, etc.)
3. **Accords** : Grille d'accords au-dessus de la portée
4. **Transposition** : Information sur la transposition appliquée (si nécessaire)
5. **Métadonnées** :
   - Titre du morceau
   - Tonalité originale et finale
   - Type d'harmonica utilisé
   - Tempo

### 2.4 Traitement de la Mélodie

- **Extraction** : Isolation de la mélodie principale depuis :
  - Partitions piano (généralement main droite)
  - Partitions multi-instruments
  - Fichiers audio (Phase 2)
- **Simplification** : Réduction à une ligne mélodique monophonique
- **Adaptation** : Ajustement de la tessiture pour l'harmonica

### 2.5 Transposition Automatique

Le système doit :
1. Analyser la mélodie extraite
2. Vérifier la jouabilité sur l'harmonica sélectionné
3. Proposer une transposition optimale si nécessaire
4. Indiquer clairement la transposition appliquée sur le PDF final

---

## 3. Spécifications Techniques

### 3.1 Architecture

```
┌─────────────────┐
│  Interface Web  │ (Flask + Bootstrap)
│   (Upload)      │
└────────┬────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Module d'Analyse d'Entrée      │
    │  - Détection format              │
    │  - Prétraitement                 │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Module d'Extraction            │
    │  Phase 1: OCR Musical (Audiveris)│
    │  Phase 2: Extraction Audio       │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Module de Traitement Musical   │
    │  - Isolation mélodie             │
    │  - Analyse tessiture             │
    │  - Détection accords             │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Module de Transposition        │
    │  - Calcul jouabilité             │
    │  - Sélection tonalité optimale   │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Module de Génération Tablature │
    │  - Mapping notes → trous         │
    │  - Techniques (bend, etc.)       │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Générateur Lilypond            │
    │  - Création fichier .ly          │
    │  - Compilation PDF               │
    └────┬─────────────────────────────┘
         │
    ┌────▼────────┐
    │  PDF Final  │
    └─────────────┘
```

### 3.2 Technologies et Dépendances

#### Phase 1 : Partitions (PDF/JPEG)

**Obligatoires :**
- **Audiveris** : OCR musical pour lecture de partitions
- **Lilypond** : Génération de partitions et tablatures
- **Python 3.9+** : Langage principal
- **Flask** : Framework web
- **Bootstrap 5** : Interface utilisateur responsive

**Bibliothèques Python :**
```
flask>=2.3.0
pillow>=10.0.0          # Traitement d'images
pdf2image>=1.16.0       # Conversion PDF → images
python-dotenv>=1.0.0    # Configuration
werkzeug>=2.3.0         # Sécurité uploads
```

**Optionnelles (amélioration qualité) :**
- **OpenCV** : Prétraitement d'images (débruitage, redressement)
- **Tesseract** : OCR texte pour métadonnées

#### Phase 2 : Audio (MP3/YouTube)

**Obligatoires :**
- **yt-dlp** : Extraction vidéos YouTube
- **librosa** ou **essentia** : Analyse audio, extraction mélodie
- **aubio** : Détection de hauteur (pitch detection)

**Bibliothèques Python supplémentaires :**
```
librosa>=0.10.0         # Analyse audio
yt-dlp>=2023.0.0        # Téléchargement YouTube
pydub>=0.25.0           # Manipulation audio
numpy>=1.24.0           # Calculs scientifiques
scipy>=1.10.0           # Traitement signal
```

#### Systèmes d'exploitation supportés
- Linux (Debian/Ubuntu, Arch, Fedora)
- macOS
- Windows (via WSL recommandé)

### 3.3 Structure du Projet

```
HarpoTab/
├── app.py                      # Application Flask principale
├── config.py                   # Configuration
├── requirements.txt            # Dépendances Python
├── setup.sh                    # Script d'installation
├── README.md                   # Documentation utilisateur
├── CAHIER_DES_CHARGES.md       # Ce document
│
├── modules/
│   ├── __init__.py
│   ├── ocr_reader.py           # Lecture partitions (Audiveris)
│   ├── audio_extractor.py      # Extraction audio (Phase 2)
│   ├── melody_extractor.py     # Isolation mélodie
│   ├── music_analyzer.py       # Analyse musicale (accords, tessiture)
│   ├── transposer.py           # Transposition automatique
│   ├── harmonica_mapper.py     # Mapping notes → tablature
│   └── lilypond_generator.py   # Génération Lilypond
│
├── data/
│   ├── harmonica_maps/
│   │   ├── diatonic_C.json     # Mapping diatonique C
│   │   ├── diatonic_G.json     # Mapping diatonique G
│   │   └── chromatic.json      # Mapping chromatique
│   └── templates/
│       └── lilypond_template.ly # Template Lilypond
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/                # Fichiers uploadés (temporaire)
│
├── templates/
│   ├── base.html               # Template de base
│   ├── index.html              # Page d'accueil
│   ├── upload.html             # Formulaire upload
│   └── result.html             # Résultat + téléchargement
│
└── tests/
    ├── test_ocr.py
    ├── test_transposition.py
    └── test_lilypond_generation.py
```

---

## 4. Interface Utilisateur

### 4.1 Technologies
- **Framework** : Flask
- **CSS** : Bootstrap 5
- **Design** : Responsive, mobile-first

### 4.2 Pages Principales

#### Page d'Accueil
- Présentation du projet
- Bouton "Commencer"

#### Page de Conversion
1. **Section Upload** :
   - Glisser-déposer ou sélection fichier
   - Formats acceptés : PDF, JPEG, PNG (+ MP3, YouTube en Phase 2)

2. **Section Configuration** :
   - Sélecteur type d'harmonica
   - Sélecteur tonalité
   - Options avancées (facultatif) :
     - Forcer transposition
     - Afficher/masquer accords

3. **Bouton Conversion**

#### Page Résultat
- Aperçu du PDF généré
- Informations de transposition
- Bouton téléchargement PDF
- Bouton "Nouvelle conversion"

### 4.3 Gestion des Erreurs

Messages clairs pour :
- Format de fichier non supporté
- Partition illisible (mauvaise qualité OCR)
- Mélodie non extractible
- Morceau injouable sur l'harmonica sélectionné

---

## 5. Workflow Utilisateur

### Phase 1 : Partitions

```
1. L'utilisateur accède à l'interface web
2. Upload d'un fichier PDF ou JPEG
3. Sélection du type d'harmonica (ex: Diatonique C)
4. Clic sur "Convertir"
5. Traitement backend :
   a. OCR musical (Audiveris)
   b. Extraction de la mélodie
   c. Détection des accords
   d. Analyse de jouabilité
   e. Transposition si nécessaire
   f. Génération tablature
   g. Compilation Lilypond → PDF
6. Affichage du résultat
7. Téléchargement du PDF
```

### Phase 2 : Audio/YouTube (Futur)

```
1. Upload MP3 ou lien YouTube
2. Extraction audio (si YouTube)
3. Analyse spectrale
4. Extraction mélodie principale
5. Transcription en notes
6. Suite identique à Phase 1 (étapes 5-7)
```

---

## 6. Contraintes et Exigences

### 6.1 Performance
- Temps de traitement < 30 secondes pour une partition simple (2-3 pages)
- Temps de traitement < 2 minutes pour extraction audio (Phase 2)

### 6.2 Qualité
- Précision OCR > 90% pour partitions de qualité standard
- Extraction mélodie correcte pour 80% des cas simples

### 6.3 Sécurité
- Validation des uploads (type MIME, taille)
- Taille max : 10 Mo pour PDF/images, 50 Mo pour audio
- Nettoyage automatique des fichiers temporaires
- Pas de stockage permanent des uploads utilisateur

### 6.4 Accessibilité
- Interface accessible (WCAG 2.1 niveau AA)
- Support navigateurs modernes (Chrome, Firefox, Safari, Edge)

---

## 7. Limites et Restrictions

### 7.1 Limitations Connues

**Musique supportée :**
- Mélodie monophonique uniquement
- Pas de polyphonie complexe
- Tempo et rythmes simples à modérés

**Partitions :**
- Qualité d'image suffisante pour OCR
- Partitions standards (clé de sol/fa)
- Pas de notations manuscrites (Phase 1)

**Audio (Phase 2) :**
- Mélodie claire et audible
- Pas de polyphonie excessive
- Qualité audio correcte (> 128 kbps)

### 7.2 Cas Non Supportés (Actuellement)

- Partitions manuscrites
- Tablatures guitare en entrée
- Musique atonale ou très complexe
- Harmonisation automatique

---

## 8. Planning de Développement

### Phase 1 : Fonctionnalités de Base (Prioritaire)
- [ ] Configuration environnement (Audiveris, Lilypond)
- [ ] Interface web Flask + Bootstrap
- [ ] Upload et validation fichiers
- [ ] OCR musical (Audiveris)
- [ ] Extraction mélodie depuis partition
- [ ] Mapping notes → tablature harmonica diatonique
- [ ] Génération PDF avec Lilypond
- [ ] Système de transposition basique

**Durée estimée** : 4-6 semaines

### Phase 2 : Extraction Audio (Futur)
- [ ] Intégration yt-dlp (YouTube)
- [ ] Extraction mélodie audio (librosa/essentia)
- [ ] Transcription audio → notes
- [ ] Tests et optimisation

**Durée estimée** : 3-4 semaines

### Phase 3 : Améliorations (Évolutions)
- [ ] Support harmonica chromatique
- [ ] Détection automatique du tempo
- [ ] Export MIDI
- [ ] Mode batch (conversion multiple)
- [ ] API REST

---

## 9. Critères de Succès

### Phase 1
✅ L'application peut convertir une partition piano PDF simple en tablature harmonica
✅ La transposition automatique fonctionne
✅ Le PDF généré est lisible et bien formaté
✅ L'interface web est intuitive et responsive

### Phase 2
✅ Extraction mélodie réussie sur 70%+ des morceaux tests
✅ Intégration YouTube fonctionnelle

---

## 10. Documentation Requise

- README.md : Installation et utilisation
- INSTALLATION.md : Guide détaillé d'installation des dépendances
- API.md : Documentation API (si développée)
- CONTRIBUTING.md : Guide de contribution
- CHANGELOG.md : Historique des versions

---

## 11. Maintenance et Évolution

### Support à Long Terme
- Mises à jour des dépendances
- Corrections de bugs
- Améliorations basées sur retours utilisateurs

### Évolutions Possibles
- Application mobile
- Mode hors-ligne
- Bibliothèque de morceaux pré-convertis
- Communauté de partage

---

**Version** : 1.0
**Date** : 11 décembre 2025
**Auteur** : Mathurin C.
**Statut** : Brouillon initial
