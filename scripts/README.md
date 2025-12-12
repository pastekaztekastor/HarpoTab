# Scripts de test locaux HarpoTab

Ce dossier contient les scripts de test pour le développement local. Ces scripts ne sont **pas exécutés par la CI** car ils nécessitent Audiveris et des fichiers de test réels.

## 📜 Scripts disponibles

### 1. `test_ocr_live.py` - Test OCR avec Audiveris
Test l'OCR musical complet avec Audiveris sur de vraies partitions PDF/PNG.

**Usage:**
```bash
python scripts/test_ocr_live.py OCRtest.pdf
python scripts/test_ocr_live.py OCRtest2.png
```

**Prérequis:** Audiveris installé localement

---

### 2. `test_mxl_parsing.py` - Test parsing MXL
Test le parsing de fichiers MusicXML compressés (.mxl).

**Usage:**
```bash
python scripts/test_mxl_parsing.py temp/ocr_output/OCRtest3.mxl
```

**Prérequis:** Fichier .mxl généré par Audiveris

---

### 3. `test_melody_extractor.py` - Test extraction mélodie
Test l'extraction de mélodie depuis un fichier MXL avec affichage détaillé.

**Usage:**
```bash
python scripts/test_melody_extractor.py temp/ocr_output/OCRtest3.mxl
python scripts/test_melody_extractor.py fichier.mxl --no-rests
```

**Options:**
- `--no-rests` : Ne pas garder les silences dans la mélodie

---

### 4. `test_transposer.py` - Test transposition
Test la transposition automatique pour adaptation à l'harmonica.

**Usage:**
```bash
# Transposition automatique pour harmonica C
python scripts/test_transposer.py temp/ocr_output/OCRtest3.mxl C

# Transposition automatique pour harmonica G
python scripts/test_transposer.py temp/ocr_output/OCRtest3.mxl G

# Forcer une transposition de +2 demi-tons
python scripts/test_transposer.py temp/ocr_output/OCRtest3.mxl C 2
```

---

## 🧪 Tests automatisés (CI)

Les **tests unitaires** qui tournent sur GitHub Actions se trouvent dans `tests/`:
- `tests/test_ocr_reader.py`
- `tests/test_melody_extractor.py`
- `tests/test_transposer.py`

Ces tests ne nécessitent **pas** Audiveris et s'exécutent automatiquement à chaque push.

**Lancer les tests unitaires:**
```bash
pytest tests/ -v
```

---

## 📊 Différence entre les deux

| Type | Localisation | Nécessite Audiveris? | Exécution |
|------|--------------|---------------------|-----------|
| **Scripts de test** | `scripts/` | ✅ Oui | Manuel, local |
| **Tests unitaires** | `tests/` | ❌ Non | Auto, CI |

---

## 🎯 Workflow de développement

1. **Développement local:**
   - Utilise les scripts `scripts/test_*.py` pour tester avec de vraies données
   - Nécessite Audiveris + fichiers PDF/MXL

2. **Avant de commit:**
   - Lance les tests unitaires: `pytest tests/ -v`
   - Vérifie le formatage: `black --check modules/ tests/`
   - Vérifie la qualité: `flake8 modules/`

3. **Après push:**
   - La CI GitHub Actions lance automatiquement les tests unitaires
   - Vérifie l'onglet "Actions" sur GitHub

---

## 📝 Notes

- Ces scripts affichent des résultats détaillés (métadonnées, notes, couverture)
- Utiles pour debugger et vérifier visuellement les résultats
- Ne modifient pas les fichiers sources
- Peuvent être utilisés comme exemples pour l'intégration

---

**Besoin d'aide?** Consulte la documentation dans `docs/CI_GUIDE.md`
