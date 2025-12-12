# Tests d'intégration HarpoTab avec Audiveris

Ce dossier contient les **tests d'intégration** qui nécessitent Audiveris et sont exécutés dans l'environnement Docker.

## 🎯 Différence avec les tests unitaires

| Type | Localisation | Audiveris requis? | Environnement | Durée |
|------|--------------|-------------------|---------------|-------|
| **Tests unitaires** | `tests/test_*.py` | ❌ Non | GitHub Actions direct | ~30s |
| **Tests d'intégration** | `tests/integration/` | ✅ Oui | Docker uniquement | ~5-10min |

## 📦 Tests disponibles

### `test_audiveris_integration.py`
Tests complets du pipeline OCR avec Audiveris:

1. **Tests d'initialisation**
   - Vérifier qu'Audiveris est installé
   - Tester la commande `audiveris --help`

2. **Tests de parsing**
   - Parser des fichiers MusicXML (.xml)
   - Parser des fichiers MusicXML compressés (.mxl)

3. **Tests de pipeline complet**
   - XML → Mélodie (extraction)
   - XML → Mélodie → Transposition

4. **Tests de robustesse**
   - Fichiers XML vides
   - Fichiers XML invalides

## 🐳 Exécution dans Docker

### Lancer les tests d'intégration localement:

```bash
# 1. Build l'image Docker
docker build -t harpotab:latest .

# 2. Lancer les tests d'intégration uniquement
docker run --rm harpotab:latest pytest tests/integration/ -v

# 3. Lancer tous les tests (unitaires + intégration)
docker run --rm harpotab:latest pytest tests/ -v
```

### Lancer les tests avec couverture:

```bash
docker run --rm \
  --volume $(pwd)/htmlcov:/app/htmlcov \
  harpotab:latest \
  pytest tests/integration/ --cov=modules --cov-report=html
```

## 🤖 Exécution sur GitHub Actions

Les tests d'intégration sont lancés par le workflow `.github/workflows/docker-tests.yml`.

### Lancement manuel:
1. Aller sur GitHub → **Actions**
2. Sélectionner **"Docker Integration Tests"**
3. Cliquer sur **"Run workflow"**

### Lancement automatique:
- Sur push vers la branche `main` (si activé)
- Seulement si des fichiers pertinents changent (`modules/`, `Dockerfile`, etc.)

## 📊 Fichiers de test (fixtures)

Le dossier `tests/fixtures/` peut contenir:
- Partitions PDF pour test OCR complet
- Fichiers MusicXML de référence
- Fichiers MXL compressés

**Note:** Ces fichiers ne sont PAS commités dans le repo (trop lourds). Les tests d'intégration génèrent des fichiers temporaires pour les tests.

## 🧪 Ajouter un nouveau test d'intégration

1. **Créer un nouveau fichier** dans `tests/integration/test_*.py`

2. **Utiliser les fixtures** pour initialiser Audiveris:
```python
import pytest
from modules.ocr_reader import AudiverisOCR

@pytest.fixture
def audiveris_ocr():
    """Initialise Audiveris OCR"""
    try:
        return AudiverisOCR()
    except FileNotFoundError:
        pytest.skip("Audiveris n'est pas installé")

def test_my_integration(audiveris_ocr):
    """Mon test d'intégration"""
    # Ton code ici
    pass
```

3. **Tester localement** dans Docker:
```bash
docker build -t harpotab:latest .
docker run --rm harpotab:latest pytest tests/integration/test_my_test.py -v
```

## 🚨 Troubleshooting

### "Audiveris n'est pas installé"
- Normal si tu lances hors Docker
- Les tests d'intégration doivent tourner dans Docker uniquement

### "FileNotFoundError: audiveris"
- L'image Docker n'a pas été buildée correctement
- Relancer `docker build -t harpotab:latest .`

### Tests trop longs
- C'est normal, l'installation d'Audiveris prend du temps
- Le cache Docker accélère les builds suivants

## 📚 Documentation

- **Dockerfile**: `/Dockerfile`
- **Workflow CI**: `/.github/workflows/docker-tests.yml`
- **Guide CI complet**: `/docs/CI_GUIDE.md`

---

**Besoin d'aide?** Consulte la documentation complète dans `docs/CI_GUIDE.md`
