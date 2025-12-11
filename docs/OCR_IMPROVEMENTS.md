# Améliorations de l'OCR Musical

## Problème Actuel

**État** : L'OCR musical actuel utilise des **données de démonstration** au lieu d'une vraie reconnaissance optique.

**Fichier** : `modules/pdf_reader.py`

Le système retourne des données hardcodées pour "Avant Toi" au lieu d'analyser réellement les partitions uploadées.

```python
def extract_music_from_image(filepath):
    # Pour le MVP : retourner des données basées sur "Avant Toi"
    demo_data = {
        'title': 'Avant Toi',
        'composer': 'VITAA & SLIMANE',
        'raw_notes': ['E4', 'E4', 'E4', ...],  # Données hardcodées
        ...
    }
    return demo_data
```

## Pourquoi c'est un Problème

1. ❌ Ne fonctionne qu'avec une seule partition (Avant Toi)
2. ❌ Ignore complètement le fichier uploadé par l'utilisateur
3. ❌ Pas de vraie reconnaissance optique des notes
4. ❌ Impossible d'utiliser avec des partitions réelles

## Solutions Possibles

### Solution 1 : Audiveris (Recommandé pour Production)

**Audiveris** est le standard open-source pour l'OCR musical.

#### Avantages
- ✅ Reconnaissance optique réelle et précise
- ✅ Support PDF et images
- ✅ Export MusicXML (standard)
- ✅ Détection automatique portées, clés, notes, accords
- ✅ Open-source et actif

#### Installation
```bash
# Ubuntu/Debian
sudo apt-get install audiveris

# ArchLinux/Manjaro
yay -S audiveris

# macOS
brew install audiveris
```

#### Intégration dans HarpoTab
```python
import subprocess
import xml.etree.ElementTree as ET

def extract_music_from_pdf_audiveris(filepath):
    """Utilise Audiveris pour extraire les notes d'une partition."""

    # 1. Lancer Audiveris en ligne de commande
    output_musicxml = filepath.replace('.pdf', '.mxl')

    result = subprocess.run([
        'audiveris',
        '-batch',
        '-export', output_musicxml,
        filepath
    ], capture_output=True)

    # 2. Parser le fichier MusicXML généré
    tree = ET.parse(output_musicxml)
    root = tree.getroot()

    # 3. Extraire les notes, accords, mesures
    notes = parse_musicxml(root)

    return notes
```

#### Complexité
- **Temps** : 1-2 jours d'implémentation
- **Difficulté** : Moyenne (nécessite parsing MusicXML)

---

### Solution 2 : music21 + OMR Externe

**music21** est une bibliothèque Python pour la théorie musicale.

#### Avantages
- ✅ Déjà en dépendances
- ✅ Excellent pour parsing MusicXML
- ✅ Support transposition, analyse harmonique
- ✅ Intégration Python native

#### Workflow
1. Utiliser un OCR externe (Audiveris, PhotoScore) pour générer MusicXML
2. Importer avec music21
3. Analyser et convertir

```python
from music21 import converter, stream

def parse_musicxml_file(musicxml_path):
    """Parse un fichier MusicXML avec music21."""
    score = converter.parse(musicxml_path)

    notes = []
    for part in score.parts:
        for note in part.flatten().notes:
            notes.append({
                'name': note.nameWithOctave,
                'duration': note.quarterLength,
                'measure': note.measureNumber
            })

    return notes
```

#### Complexité
- **Temps** : 1 jour (si MusicXML disponible)
- **Difficulté** : Facile

---

### Solution 3 : API OCR Commerciale

**Services comme** :
- **PhotoScore** (Avid)
- **SmartScore** (Musitek)
- **ABBYY FineReader** (avec plugin musique)

#### Avantages
- ✅ Très précis
- ✅ Moins de développement

#### Inconvénients
- ❌ Payant
- ❌ Dépendance externe
- ❌ Pas open-source

---

### Solution 4 : Approche Hybride (Recommandé pour MVP++)

**Combinaison de plusieurs outils selon le contexte.**

#### Workflow
```python
def extract_music_from_file(filepath):
    """Extraction intelligente selon le type de fichier."""

    # 1. Si c'est déjà du MusicXML → music21 directement
    if filepath.endswith('.musicxml') or filepath.endswith('.mxl'):
        return parse_musicxml_file(filepath)

    # 2. Si Audiveris installé → OCR automatique
    if check_audiveris_installed():
        return extract_with_audiveris(filepath)

    # 3. Sinon → Fallback sur données démo
    return extract_demo_data()
```

#### Avantages
- ✅ Flexible
- ✅ Graceful degradation
- ✅ Permet upload MusicXML direct

---

## Plan d'Implémentation Recommandé

### Phase 1 : Support MusicXML (Facile)
1. Ajouter upload de fichiers `.musicxml` / `.mxl`
2. Parser avec music21
3. Tester avec partitions exportées de MuseScore/Finale

**Temps** : 1 jour

---

### Phase 2 : Intégration Audiveris (Moyen)
1. Installer Audiveris sur le serveur
2. Créer wrapper Python pour appel CLI
3. Parser les MusicXML générés
4. Gérer les erreurs de reconnaissance

**Temps** : 2-3 jours

---

### Phase 3 : Amélioration Détection (Avancé)
1. Détecter clé de Sol vs clé de Fa automatiquement
2. Extraire accords depuis harmonie
3. Identifier tempo, mesure, armature
4. Support partitions multi-instruments

**Temps** : 1 semaine

---

## État Actuel vs Futur

### Maintenant (MVP)
```
Partition PDF/Image → [DONNÉES DÉMO] → Notes hardcodées → Tablature
```

### Après Phase 1 (Support MusicXML)
```
Partition MusicXML → [music21 Parser] → Notes réelles → Tablature
```

### Après Phase 2 (OCR Complet)
```
Partition PDF/Image → [Audiveris OCR] → MusicXML → [music21] → Tablature
```

---

## Fichiers à Modifier

### 1. `modules/pdf_reader.py`
```python
# Ajouter :
- extract_musicxml()
- extract_with_audiveris()
- check_audiveris_installed()

# Modifier :
- extract_music_from_image() → vraie extraction
- extract_music_from_pdf() → vraie extraction
```

### 2. `app.py`
```python
# Ajouter support .musicxml dans allowed extensions
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'musicxml', 'mxl'}
```

### 3. `requirements.txt`
```
# Déjà présent :
music21>=9.1.0

# À ajouter si OCR externe :
# audiveris (installation système)
```

---

## Tests Nécessaires

### Test 1 : Upload MusicXML
```python
def test_musicxml_upload():
    """Test upload d'un fichier MusicXML direct."""
    musicxml_file = 'tests/fixtures/test_partition.musicxml'
    notes = extract_music_from_file(musicxml_file)
    assert len(notes) > 0
    assert notes[0]['name'] in ['C4', 'D4', 'E4', ...]
```

### Test 2 : Audiveris OCR
```python
def test_audiveris_ocr():
    """Test reconnaissance avec Audiveris (si installé)."""
    if not check_audiveris_installed():
        pytest.skip("Audiveris non installé")

    pdf_file = 'tests/fixtures/partition_simple.pdf'
    notes = extract_with_audiveris(pdf_file)
    assert len(notes) > 0
```

---

## Conclusion

**Recommandation** :

1. **Court terme** (1 jour) : Ajouter support MusicXML
   - Permet aux utilisateurs d'uploader des fichiers depuis MuseScore
   - Contourne complètement le problème OCR

2. **Moyen terme** (1 semaine) : Intégrer Audiveris
   - OCR réel pour PDF/images
   - Fonctionne avec partitions scannées

3. **Long terme** (1 mois+) : Entraîner modèle IA custom
   - Deep learning pour reconnaissance optique
   - Spécialisé harmonica si nécessaire

---

## Ressources

### Documentation
- **Audiveris** : https://audiveris.github.io/audiveris/
- **music21** : https://web.mit.edu/music21/
- **MusicXML** : https://www.w3.org/2021/06/musicxml40/

### Alternatives Open-Source
- **OpenOMR** : https://github.com/openomr/openomr
- **SheetVision** : https://github.com/cal-pratt/SheetVision (IA)

### Formats de Partition
- **MusicXML** : Standard interchange (MuseScore, Finale, Sibelius)
- **MIDI** : Notes + timing, mais pas de notation visuelle
- **LilyPond (.ly)** : Code source textuel

---

**Prochaine étape** : Implémenter support MusicXML (Phase 1)
