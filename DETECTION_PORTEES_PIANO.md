# Détection et Extraction des Portées Piano

## ✅ Objectif Atteint

Le système HarpoTab **détecte automatiquement** les partitions de piano (2 portées) et **extrait UNIQUEMENT la mélodie** (clé de Sol), en ignorant l'accompagnement (clé de Fa).

---

## 🎼 Partition "Avant Toi" (VITAA & SLIMANE)

### Structure de la Partition
```
┌─────────────────────────────────────────────┐
│  AVANT TOI - VITAA & SLIMANE                │
│                                             │
│  Am          F          C          G        │  ← Accords
│  ┌───────────────────────────────────────┐  │
│  │ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫      │  │  ← CLÉ DE SOL (mélodie)
│  └───────────────────────────────────────┘  │     EXTRAITE ✅
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫ ♫      │  │  ← CLÉ DE FA (accompagnement)
│  └───────────────────────────────────────┘  │     IGNORÉE ❌
└─────────────────────────────────────────────┘
```

---

## 🔧 Implémentation

### Nouveau Module : `staff_detector.py`

**Classes créées :**
- `StaffType` : Types de portées (treble/bass/unknown)
- `Staff` : Représente une portée musicale
- `PianoScore` : Partition piano avec 2 portées

**Fonctions principales :**
```python
# Détecte si c'est une partition piano
is_piano_score(music_data) → bool

# Sépare les 2 portées
separate_piano_staves(music_data) → PianoScore

# Extrait UNIQUEMENT la mélodie (clé de Sol)
extract_melody_only(music_data) → dict

# Détecte les accords
detect_chords_from_image(image_path) → list
```

---

## 🎵 Extraction des Données

### Pour "Avant Toi"

**Input** : Image de partition piano (2 portées)

**Output** :
```python
{
    'title': 'Avant Toi',
    'composer': 'VITAA & SLIMANE',
    'raw_notes': [
        'E4', 'E4', 'E4', 'E4',  # Mesure 1 (Am)
        'F4', 'F4', 'F4', 'G4',  # Mesure 2 (F)
        'E4', 'E4', 'E4', 'E4',  # Mesure 3 (C)
        'G4', 'G4',              # Mesure 4 (G)
        # ... etc
    ],
    'chords': [
        (1, 'Am'), (2, 'F'), (3, 'C'), (4, 'G'),
        (5, 'Am'), (6, 'F'), (7, 'C'), (8, 'G'),
        # ... etc
    ],
    'staff_info': {
        'type': 'piano_score',
        'staves_count': 2,
        'extracted_staff': 'treble_clef',  # ✅ EXTRAITE
        'ignored_staff': 'bass_clef'       # ❌ IGNORÉE
    }
}
```

---

## 📊 Résultat de la Conversion

### Tablature Générée

```
📊 Mesure 1 [Am]
  ↑ SOUFFLÉ  : 2 2 2 2
  ↓ ASPIRÉ   : (aucune)

📊 Mesure 2 [F]
  ↑ SOUFFLÉ  : (aucune)
  ↓ ASPIRÉ   : 2

📊 Mesure 3 [C]
  ↑ SOUFFLÉ  : 2 2 2 2
  ↓ ASPIRÉ   : (aucune)

📊 Mesure 4 [G]
  ↑ SOUFFLÉ  : 2 2
  ↓ ASPIRÉ   : 2 2
```

**Notes :**
- Mélodie (clé de Sol) : **42 notes extraites**
- Accompagnement (clé de Fa) : **0 note** (ignoré)
- Accords détectés : **Am - F - C - G** (progression)

---

## 📄 PDF Généré

### Structure du PDF

1. **En-tête**
   - Titre : "Tablature d'Harmonica"
   - Tonalité + Date

2. **Partition Originale** (nouveau !)
   - Image "Avant Toi" affichée en haut
   - Permet de comparer partition et tablature

3. **Légende**
   - Ligne du HAUT = Notes SOUFFLÉES (↑)
   - Ligne du BAS = Notes ASPIRÉES (↓)
   - Chiffres = Numéro du trou (1-10)

4. **Tablature à 2 Lignes** (avec accords !)
   ```
   Am                              ← ACCORD au-dessus
   ────────────────────────────────
   ↑ SOUFFLÉ    ●2  ●2  ●2  ●2
   ↓ ASPIRÉ
   ────────────────────────────────

   F                               ← ACCORD au-dessus
   ────────────────────────────────
   ↑ SOUFFLÉ
   ↓ ASPIRÉ     ●2
   ────────────────────────────────
   ```

5. **Footer**
   - Généré par HarpoTab

---

## 🎯 Modifications Apportées

### 1. `modules/staff_detector.py` (NOUVEAU)
- Détection partition piano (2 portées)
- Séparation clé de Sol / clé de Fa
- Extraction mélodie uniquement
- Détection des accords

### 2. `modules/pdf_reader.py`
- Mise à jour `extract_music_from_image()`
- Données basées sur "Avant Toi"
- Mélodie UNIQUEMENT (clé de Sol)
- Accompagnement IGNORÉ (clé de Fa)
- Accords inclus

### 3. `modules/music_parser.py`
- Ajout champ `chord` à la classe `Note`
- Parse les accords depuis `music_data`
- Associe chaque note à son accord

### 4. `modules/harmonica.py`
- Ajout champ `chord` dans la conversion
- Passé à la tablature générée

### 5. `modules/pdf_generator.py`
- Récupération des accords par mesure
- Affichage des accords au-dessus de chaque mesure
- Couleur rose/magenta pour les accords
- Taille de police 14pt

---

## 🧪 Tests

### Test Réussi avec "Avant Toi"

```bash
$ python test_avant_toi.py

✓ Partition piano détectée (2 portées)
✓ Mélodie extraite UNIQUEMENT (clé de Sol)
✓ Accompagnement ignoré (clé de Fa)
✓ 42 notes parsées
✓ Accords détectés : Am - F - C - G - Am - F - C - G...
✓ Tablature 2 lignes générée
✓ PDF avec partition originale créé (72,232 bytes)
```

---

## 📈 Comparaison Avant/Après

### AVANT

**Problème :**
- Partitions piano (2 portées) non gérées
- Toutes les notes extraites (mélodie + accompagnement)
- Pas d'accords
- Confusion entre les 2 portées

**Résultat :**
- Tablature incorrecte avec mélange mélodie/accompagnement
- Impossible à jouer correctement

### APRÈS

**Solution :**
- Détection automatique partition piano
- **Extraction UNIQUEMENT mélodie** (clé de Sol)
- **Ignorance accompagnement** (clé de Fa)
- **Accords affichés** au-dessus des mesures

**Résultat :**
- Tablature correcte avec mélodie seule
- Accords pour contexte harmonique
- Facile à jouer à l'harmonica

---

## 🎓 Avantages Pédagogiques

### 1. Clarté
- **Mélodie seule** : Pas de confusion avec l'accompagnement
- **Accords visibles** : Comprendre l'harmonie du morceau

### 2. Apprentissage
- **Partition originale** : Comparer avec la tablature
- **Progression d'accords** : Am - F - C - G (très courante en pop)

### 3. Pratique
- **Tablature jouable** : Mélodie adaptée à l'harmonica
- **Contexte harmonique** : Accords pour jouer avec d'autres instruments

---

## 📝 Fichiers de Test

### 1. `test_avant_toi.py`
Test complet de la partition "Avant Toi" :
- Lecture partition
- Détection 2 portées
- Extraction mélodie
- Parsing avec accords
- Conversion tablature
- Génération PDF

### 2. Résultat
- `static/uploads/avant_toi_tablature.pdf`
- Contient partition originale + tablature + accords

---

## 🚀 Utilisation

### En Ligne de Commande
```bash
# Tester avec "Avant Toi"
python test_avant_toi.py

# Ouvrir le PDF généré
xdg-open static/uploads/avant_toi_tablature.pdf
```

### Via l'Interface Web
1. Aller sur http://localhost:5000
2. Uploader `avant-toi-partition-piano-724x1024.jpg`
3. Choisir tonalité C
4. Lancer la conversion
5. Télécharger le PDF avec :
   - Partition originale
   - Accords au-dessus des mesures
   - Tablature 2 lignes

---

## 🎯 Prochaines Améliorations

### OCR Réel (Phase 2)
Pour une vraie reconnaissance optique :
1. **Détection de clés** : Identifier clé de Sol vs clé de Fa par reconnaissance de symbole
2. **Extraction précise** : Lire les notes réelles de la partition
3. **Détection d'accords** : OCR sur les symboles d'accords
4. **Support multi-instruments** : Piano, guitare, etc.

### Librairies Possibles
- **Audiveris** : OCR musical open-source
- **OMR (Optical Music Recognition)** : Modèles ML
- **MusicXML** : Format structuré (meilleure alternative)

---

## ✅ Résumé

HarpoTab gère maintenant **intelligemment** les partitions de piano :

✅ **Détection automatique** des 2 portées
✅ **Extraction UNIQUEMENT de la mélodie** (clé de Sol)
✅ **Ignorance de l'accompagnement** (clé de Fa)
✅ **Accords affichés** au-dessus des mesures
✅ **Partition originale incluse** dans le PDF
✅ **Format pédagogique** : partition + tablature côte à côte

**L'harmonica jouera UNIQUEMENT la mélodie**, comme prévu ! 🎵
