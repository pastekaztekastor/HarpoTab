# Structure de Données du Pipeline HarpoTab

## Vue d'ensemble du flux de données

```
PDF/Image → OCR → MusicXML Dict → Mélodie Dict → Transposée Dict → Tablature List → PDF
```

---

## 1. Sortie OCR (ocr_reader.py → parse_musicxml())

**Type retourné** : `Dict[str, Any]`

```python
{
    'metadata': {
        'title': str | None,
        'composer': str | None,
        'key': str | None,           # Tonalité (ex: "C", "G")
        'time_signature': str,       # Ex: "2/4", "4/4", "3/4"
        'tempo': int | None          # BPM (ex: 120)
    },
    'parts': [                       # Liste des parties instrumentales
        {
            'id': str,               # Ex: "P1", "P2"
            'name': str | None,      # Nom de l'instrument
            'measures': [            # Liste des mesures
                {
                    'number': int,   # Numéro de mesure
                    'attributes': dict,  # Infos de mesure
                    'direction': str | None,  # Indications (tempo)
                    'notes': [       # Liste des notes de la mesure
                        {
                            'type': 'note',  # ou 'rest'
                            'pitch': {
                                'step': str,      # 'C', 'D', 'E', 'F', 'G', 'A', 'B'
                                'octave': int,    # 0-8
                                'alter': int      # -1 (bémol), 0 (naturel), 1 (dièse)
                            },
                            'duration': int,     # Durée en divisions
                            'note_type': str,    # 'whole', 'half', 'quarter', 'eighth', 'sixteenth'
                            'midi': int | None   # Numéro MIDI (optionnel)
                        },
                        # ... autres notes
                    ]
                },
                # ... autres mesures
            ]
        },
        # ... autres parties
    ],
    'source_file': str  # Chemin du fichier MusicXML
}
```

### Notes importantes :
- `duration` est en "divisions" (unité de temps définie dans attributes)
- Pour 2/4 avec divisions=2 : croche=1, noire=2, blanche=4
- `note_type` est la représentation graphique ('eighth', 'quarter', etc.)

---

## 2. Sortie Extraction Mélodie (melody_extractor.py)

**Type retourné** : `Dict[str, Any]`

```python
{
    'notes': [                       # Liste linéaire de notes
        {
            'type': 'note',          # ou 'rest'
            'pitch': str,            # 'C', 'D', 'E', etc.
            'octave': int,           # 4, 5, 6, etc.
            'alter': int,            # -1, 0, 1
            'duration': int,         # Durée en notation Lilypond (1, 2, 4, 8, 16)
            'midi': int,             # Numéro MIDI (C4=60)
            'note_type': str         # Type de note ('eighth', 'quarter', etc.)
        },
        # ... autres notes
    ],
    'metadata': dict,                # Métadonnées copiées depuis OCR
    'time_signature': str,           # Ex: "2/4"
    'tempo': int,                    # BPM (120 par défaut)
    'source_file': str,
    'part_id': str,
    'total_measures': int
}
```

---

## 3. Sortie Analyse Musicale (music_analyzer.py)

**Type retourné** : `Dict[str, Any]`

```python
{
    'key': str,                      # Tonalité détectée ('C', 'G', 'Am', etc.)
    'range': tuple,                  # (note_min, note_max) ex: ('C4', 'A4')
    'chords': list,                  # Liste d'accords détectés (future)
    'tempo': int                     # Tempo détecté ou par défaut
}
```

---

## 4. Sortie Transposition (transposer.py)

**Type retourné** : `Dict[str, Any]` (même structure que melody_extractor)

```python
{
    'notes': [                       # Notes transposées
        {
            'type': 'note',
            'pitch': str,            # Note transposée
            'octave': int,           # Octave transposée
            'alter': int,
            'duration': int,
            'midi': int,             # MIDI transposé
            'note_type': str
        },
        # ...
    ],
    'metadata': dict,
    'time_signature': str,
    'tempo': int
}
```

**Retourne aussi** : `(melody_dict, semitones_transposed, playability_dict)`

---

## 5. Sortie Mapping Harmonica (harmonica_mapper.py)

**Type retourné** : `List[Dict[str, Any]]`

```python
[
    {
        'type': 'note',              # ou 'rest'
        'hole': int,                 # 1-10 (numéro de trou)
        'direction': str,            # 'blow' ou 'draw'
        'technique': str | None,     # None, 'bend_half', 'bend_full', 'overblow', 'overdraw'
        'duration': int,             # Durée en notation Lilypond
        'pitch': str,                # Note originale
        'octave': int                # Octave originale
    },
    # ... autres positions
]
```

---

## 6. Entrée Génération Lilypond (lilypond_generator.py)

**Paramètres attendus** :
- `melody`: `List[Dict]` - Liste de notes (format melody_extractor)
- `tabs`: `List[Dict]` - Liste de tablatures (format harmonica_mapper)
- `metadata`: `Dict` - Métadonnées complètes

```python
metadata = {
    'title': str,
    'composer': str,
    'key': str,                      # Tonalité (ex: 'C')
    'time_signature': str,           # Ex: '2/4'
    'tempo': int,                    # BPM
    'harmonica_type': str,           # 'diatonic' ou 'chromatic'
    'harmonica_key': str,            # 'C', 'G', etc.
    'transposition': int             # Demi-tons de transposition (ex: 0, +2, -3)
}
```

---

## Problèmes actuels identifiés

### ❌ PROBLÈME 1 : Perte de time_signature et tempo
- **Où** : Entre `ocr_reader` et `melody_extractor`
- **Cause** : `melody_extractor` ne copie pas `time_signature` et `tempo` depuis metadata
- **Impact** : Lilypond utilise des valeurs par défaut (4/4, 120 BPM)

### ❌ PROBLÈME 2 : Durées incorrectes
- **Où** : `lilypond_generator._format_melody()`
- **Cause** : Utilise `note.get('duration', 4)` qui est en "divisions", pas en notation Lilypond
- **Impact** : Toutes les notes sont des blanches au lieu de croches/noires

### ❌ PROBLÈME 3 : Conversion durée divisions → Lilypond
- **Où** : `melody_extractor` ne convertit pas correctement
- **Cause** : Pas de conversion duration (divisions) → note_type (Lilypond)
- **Impact** : Rythme incorrect

---

## Solutions à implémenter

### 1. Enrichir melody_extractor.extract_melody()
```python
# Ajouter dans le résultat :
result = {
    'notes': melody_notes,
    'time_signature': musicxml_data['metadata'].get('time_signature', '4/4'),
    'tempo': musicxml_data['metadata'].get('tempo', 120),
    'key': musicxml_data['metadata'].get('key'),
    # ...
}
```

### 2. Convertir duration correctement
```python
# Dans _extract_notes_from_part(), calculer la durée Lilypond :
def duration_to_lilypond(duration, divisions, time_sig):
    # divisions = unités par noire
    # duration = unités de la note
    # Retourne : 1 (ronde), 2 (blanche), 4 (noire), 8 (croche), 16 (double)

    # Exemple : duration=1, divisions=2 → croche (8)
    quarter_note = divisions
    ratio = duration / quarter_note

    if ratio >= 4: return 1      # ronde
    elif ratio >= 2: return 2    # blanche
    elif ratio >= 1: return 4    # noire
    elif ratio >= 0.5: return 8  # croche
    else: return 16              # double croche
```

### 3. Transmettre metadata complète à Lilypond
```python
# Dans app.py, process_conversion() :
metadata = {
    'title': input_file.stem.replace('_', ' ').title(),
    'composer': melody_data.get('composer', ''),
    'key': analysis.get('key', 'C'),
    'time_signature': final_melody.get('time_signature', '4/4'),  # ← AJOUTER
    'tempo': final_melody.get('tempo', 120),                      # ← AJOUTER
    'harmonica_type': harmonica_type,
    'harmonica_key': harmonica_key,
    'transposition': result['metadata'].get('transposition', 0)
}
```

---

## Résumé des types

| Étape | Fonction | Type retour |
|-------|----------|-------------|
| OCR | `parse_musicxml()` | `Dict` (structure complète) |
| Extraction | `extract_melody()` | `Dict` (notes + metadata) |
| Analyse | `analyze_music()` | `Dict` (key, range, chords) |
| Transposition | `transpose_for_harmonica()` | `(Dict, int, Dict)` |
| Mapping | `map_to_harmonica()` | `List[Dict]` (tablature) |
| PDF | `generate_pdf()` | `bool` (succès) |
