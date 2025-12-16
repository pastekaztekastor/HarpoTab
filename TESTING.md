# Guide de Test End-to-End - HarpoTab

Ce guide explique comment tester le pipeline complet de HarpoTab.

## 🎯 État Actuel du Pipeline

### ✅ Modules Fonctionnels
1. **OCR Musical** (Audiveris) - ✅ Lecture PDF → MusicXML
2. **Extraction Mélodie** - ✅ MusicXML → Notes
3. **Analyse Musicale** - ✅ Détection tonalité & tessiture
4. **Transposition** - ✅ Algorithme intelligent
5. **Mapping Tablature** - ⚠️ Partiellement implémenté
6. **Génération PDF** - ❌ À implémenter

### ⚠️ Limitations Connues
- **Audiveris OCR** : Peut mal interpréter les partitions simples
- **Générat PDF Lilypond** : Module non terminé (`NotImplementedError`)

---

## 📝 Méthode 1 : Test avec le script de test intégré

Le projet inclut un script de test qui teste le pipeline complet :

```bash
# Depuis le dossier racine du projet
python test_pipeline.py
```

**Ce que fait ce script :**
- Cherche un fichier PDF dans le dossier courant
- Lance le pipeline complet de conversion
- Affiche les logs détaillés de chaque étape
- Indique succès ou échec

**Résultat attendu :**
```
🎹 TEST DU PIPELINE HARPOTAB
📄 Fichier de test: votre_partition.pdf
🎵 Harmonica: diatonic C
```

---

## 📝 Méthode 2 : Test Manuel via Python

```python
from pathlib import Path
from app import process_conversion
from config import Config
import shutil

# 1. Préparer un fichier PDF de partition
test_pdf = Path('ma_partition.pdf')
upload_path = Config.UPLOAD_FOLDER / test_pdf.name
shutil.copy(test_pdf, upload_path)

# 2. Lancer la conversion
result = process_conversion(
    input_file=upload_path,
    harmonica_type='diatonic',  # ou 'chromatic'
    harmonica_key='C',          # C, D, G, etc.
    output_dir=Config.OUTPUT_FOLDER
)

# 3. Vérifier le résultat
if result['success']:
    print(f"✅ Succès ! PDF généré: {result['pdf_path']}")
    print(f"Métadonnées: {result['metadata']}")
else:
    print(f"❌ Échec: {result['error']}")
```

---

## 📝 Méthode 3 : Test via l'application Flask

```bash
# 1. Lancer l'application
python app.py

# 2. Ouvrir le navigateur
http://localhost:5000

# 3. Utiliser l'interface web
- Uploader une partition PDF
- Sélectionner type d'harmonica
- Cliquer "Convertir"
- Télécharger le résultat
```

---

## 🎵 Créer une Partition de Test Simple

Pour tester avec une partition garantie de fonctionner, créez un fichier Lilypond :

### test_gamme.ly
```lilypond
\\version "2.24.0"

\\header {
  title = "Gamme de Do"
}

{
  \\clef treble
  \\key c \\major
  \\time 4/4

  c'4 d' e' f' | g' a' b' c'' |
  c'' b' a' g' | f' e' d' c' |

  \\bar "|."
}
```

### Générer le PDF :
```bash
lilypond -o test_gamme test_gamme.ly
```

### Tester avec HarpoTab :
```bash
python test_pipeline.py
# Le script détectera automatiquement test_gamme.pdf
```

---

## 🐛 Résolution de Problèmes

### Erreur : "Audiveris not found"
```bash
# Vérifier installation
which audiveris

# Arch/Manjaro
yay -S audiveris

# Ou définir le chemin
export AUDIVERIS_PATH=/chemin/vers/audiveris
```

###  Erreur : "Aucun fichier MusicXML généré"
- La partition n'est pas reconnue par Audiveris
- Essayez avec une partition plus claire
- Vérifiez que c'est bien une partition musicale (pas du texte)

### Erreur : "Mélodie non jouable sur harmonica"
- C'est **normal** ! L'algorithme de transposition est strict
- Essayez un autre type d'harmonica (diatonic D, G, chromatic)
- Ou une mélodie plus simple dans une tessiture adaptée

### Erreur : "NotImplementedError: Format tablature Lilypond"
- Le module de génération PDF n'est pas terminé
- C'est attendu ! Les étapes 1-6 doivent fonctionner jusqu'à la tablature

---

## ✅ Exemple de Test Réussi

Voici à quoi ressemble un test réussi (jusqu'à l'étape 6/7) :

```
Étape 1/7: OCR de la partition
✓ Partition lue avec succès

Étape 2/7: Extraction de la mélodie principale
✓ Mélodie extraite: 16 notes

Étape 3/7: Analyse musicale
✓ Tonalité détectée: C
✓ Tessiture: C4 - C5

Étape 4/7: Chargement mapping harmonica
✓ Mapping chargé: Harmonica diatonique Richter 10 trous en C

Étape 5/7: Vérification jouabilité
✓ Transposition appliquée: +0 demi-tons
✓ Jouabilité: 100%

Étape 6/7: Génération de la tablature harmonica
✓ Tablature générée: 16 positions

Étape 7/7: Génération du PDF avec Lilypond
❌ La génération de PDF n'est pas encore implémentée
```

---

## 📊 Tester Individuellement Chaque Module

### Test OCR seulement
```python
from modules.ocr_reader import read_partition_from_pdf
from pathlib import Path
from config import Config

result = read_partition_from_pdf(
    pdf_path=Path('ma_partition.pdf'),
    output_dir=Config.TEMP_FOLDER
)
print(result)
```

### Test Extraction Mélodie
```python
from modules.melody_extractor import extract_melody_from_musicxml
melody = extract_melody_from_musicxml(musicxml_data)
print(f"Notes extraites: {len(melody['notes'])}")
```

### Test Transposition
```python
from modules.transposer import transpose_for_harmonica
import json

# Charger le mapping
with open('data/harmonica_maps/diatonic_C.json') as f:
    mapping = json.load(f)

final_melody, semitones, playability = transpose_for_harmonica(
    melody_data,
    mapping
)
print(f"Transposition: {semitones} demi-tons")
print(f"Jouable: {playability['playable']}")
```

---

## 🎯 Prochaines Étapes pour Finaliser les Tests

1. **Implémenter le générateur Lilypond complet**
2. **Créer une suite de partitions de test** (gammes, mélodies simples)
3. **Ajouter tests unitaires** pour chaque module
4. **Tester avec différents harmonicas** (D, G, chromatic)

---

**Version** : 0.1.0 (Alpha)
**Dernière mise à jour** : 14 décembre 2025
