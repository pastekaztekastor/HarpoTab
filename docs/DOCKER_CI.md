# 🐳 CI/CD Docker avec Audiveris - Guide complet

## 📋 Vue d'ensemble

Ce document explique la mise en place de la CI/CD Docker pour tester HarpoTab avec Audiveris dans un environnement isolé.

## 🎯 Objectifs

- ✅ Tester le code avec Audiveris dans un environnement reproductible
- ✅ Compléter les tests unitaires rapides avec des tests d'intégration complets
- ✅ Éviter les problèmes de dépendances entre environnements
- ✅ Permettre l'exécution locale identique à la CI

## 🏗️ Architecture

### Deux types de tests sur GitHub Actions:

| Workflow | Fichier | Durée | Fréquence | Audiveris? |
|----------|---------|-------|-----------|------------|
| **Tests unitaires** | `.github/workflows/tests.yml` | ~30s | À chaque push | ❌ Non |
| **Tests d'intégration** | `.github/workflows/docker-tests.yml` | ~5-10min | Manuel ou sur main | ✅ Oui |

### Pourquoi deux workflows?

1. **Tests unitaires (tests.yml)**:
   - Rapides (~30 secondes)
   - Ne nécessitent pas Audiveris
   - S'exécutent à chaque push
   - Détectent rapidement les régressions

2. **Tests d'intégration (docker-tests.yml)**:
   - Complets avec Audiveris
   - Plus lents (~5-10 minutes)
   - S'exécutent manuellement ou sur push vers `main`
   - Valident le pipeline complet OCR

## 📦 Fichiers créés

### 1. `Dockerfile` (150+ lignes)
Image Docker complète avec tous les outils nécessaires:

```dockerfile
FROM ubuntu:22.04

# Dépendances système
- Python 3.11
- Java 21 (pour Audiveris)
- Tesseract OCR
- Lilypond
- Poppler (pdf2image)

# Installation Audiveris 5.9.0
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.9.0/Audiveris_5.9.0.deb
RUN dpkg -i Audiveris_5.9.0.deb

# Application HarpoTab
COPY . /app/
RUN pip install -r requirements.txt

CMD ["pytest", "tests/", "-v"]
```

### 2. `.github/workflows/docker-tests.yml` (160+ lignes)
Workflow GitHub Actions pour les tests Docker:

**Déclencheurs:**
- Manuel (workflow_dispatch)
- Push vers `main` (si fichiers pertinents changent)
- Pull requests vers `main`

**Étapes:**
1. Checkout du code
2. Configuration Docker Buildx (pour cache)
3. Build de l'image Docker
4. Vérification des outils installés
5. Tests unitaires dans Docker
6. Tests d'intégration Audiveris
7. Génération rapport de couverture
8. Upload des artifacts

### 3. `tests/integration/` - Tests d'intégration
Nouveaux tests qui nécessitent Audiveris:

- `test_audiveris_integration.py` - 11 tests complets
  - Initialisation Audiveris
  - Parsing MusicXML et MXL
  - Pipeline complet (XML → Mélodie → Transposition)
  - Tests de robustesse

### 4. Documentation
- `tests/integration/README.md` - Guide des tests d'intégration
- `docs/DOCKER_CI.md` - Ce document

## 🚀 Utilisation

### Option 1: Lancer localement avec Docker

#### Build l'image:
```bash
docker build -t harpotab:latest .
```

#### Lancer les tests unitaires:
```bash
docker run --rm harpotab:latest pytest tests/ -v
```

#### Lancer les tests d'intégration uniquement:
```bash
docker run --rm harpotab:latest pytest tests/integration/ -v
```

#### Lancer avec couverture de code:
```bash
docker run --rm \
  --volume $(pwd)/htmlcov:/app/htmlcov \
  harpotab:latest \
  pytest tests/ --cov=modules --cov-report=html
```

#### Shell interactif dans le conteneur:
```bash
docker run -it harpotab:latest /bin/bash
```

### Option 2: Lancer sur GitHub Actions

#### Lancement manuel:
1. Aller sur GitHub → **Actions**
2. Sélectionner **"Docker Integration Tests"** dans la liste
3. Cliquer sur **"Run workflow"**
4. Choisir la branche
5. Cliquer sur **"Run workflow"** (bouton vert)

#### Lancement automatique:
Les tests Docker se lancent automatiquement sur push vers `main` si:
- `modules/**` change
- `tests/**` change
- `Dockerfile` change
- `requirements.txt` change
- `.github/workflows/docker-tests.yml` change

## 📊 Résultats et Artifacts

### Logs disponibles sur GitHub Actions:
- Build de l'image Docker
- Versions des outils installés (Python, Java, Audiveris, etc.)
- Résultats des tests unitaires
- Résultats des tests d'intégration
- Rapport de couverture

### Artifacts téléchargeables:
- `docker-coverage-report` - Rapport HTML de couverture de code (gardé 30 jours)

## ⚙️ Configuration avancée

### Modifier les déclencheurs

Dans `.github/workflows/docker-tests.yml`:

```yaml
on:
  # Lancement manuel uniquement
  workflow_dispatch:

  # Lancer sur push vers main
  push:
    branches: [ "main" ]
    paths:
      - 'modules/**'
      - 'tests/**'
      - 'Dockerfile'

  # Lancer sur tous les push
  push:
    branches: [ "**" ]
```

### Ajouter des tests d'intégration avec fichiers réels

1. **Ajouter des fixtures** dans `tests/fixtures/`:
```bash
tests/fixtures/
├── simple_melody.pdf
├── complex_score.pdf
└── test_output.mxl
```

2. **Créer un test** dans `tests/integration/`:
```python
def test_ocr_with_real_pdf(audiveris_ocr, test_fixtures_dir):
    """Test OCR avec un vrai PDF"""
    pdf_file = test_fixtures_dir / "simple_melody.pdf"
    result = audiveris_ocr.process_pdf(pdf_file)
    assert result is not None
```

3. **Modifier le Dockerfile** pour copier les fixtures:
```dockerfile
# Copier les fixtures de test
COPY tests/fixtures/ /app/tests/fixtures/
```

## 🐛 Troubleshooting

### Build Docker échoue

**Problème:** `E: Unable to locate package openjdk-21-jre-headless`
**Solution:** Ubuntu 22.04 n'a pas Java 21 par défaut
```dockerfile
# Ajouter le PPA Java
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update
RUN apt-get install -y openjdk-21-jre-headless
```

**Problème:** `dpkg: dependency problems prevent configuration of audiveris`
**Solution:** Installer les dépendances manquantes
```dockerfile
RUN dpkg -i Audiveris_5.9.0.deb || apt-get install -f -y
```

### Tests échouent dans Docker

**Problème:** `FileNotFoundError: audiveris`
**Solution:** Vérifier l'installation dans le Dockerfile
```bash
docker run -it harpotab:latest /bin/bash
# Dans le conteneur:
which audiveris
audiveris --help
```

**Problème:** Tests d'intégration sont skippés
**Solution:** C'est normal - ils sont conçus pour tourner uniquement avec Audiveris
```python
@pytest.fixture
def audiveris_ocr():
    try:
        return AudiverisOCR()
    except FileNotFoundError:
        pytest.skip("Audiveris n'est pas installé")  # ← Skip si pas dans Docker
```

### GitHub Actions timeout

**Problème:** Le workflow dépasse 6 heures (limite gratuite)
**Solution:**
- Réduire la fréquence des tests Docker
- Utiliser le cache Docker Buildx (déjà configuré)
- Lancer manuellement uniquement

## 📈 Métriques et Performance

### Temps d'exécution typiques:

| Étape | Première fois | Avec cache |
|-------|---------------|------------|
| Build Docker | ~8 minutes | ~2 minutes |
| Tests unitaires | ~30 secondes | ~30 secondes |
| Tests d'intégration | ~1 minute | ~1 minute |
| **Total** | **~10 minutes** | **~3-4 minutes** |

### Quota GitHub Actions (compte gratuit):
- **2000 minutes/mois**
- Ce workflow: ~10 minutes/exécution
- Maximum recommandé: ~200 exécutions/mois

## 🔄 Workflow de développement recommandé

### 1. Développement local
```bash
# Tests rapides (sans Audiveris)
pytest tests/test_*.py -v

# Scripts de test avec Audiveris
python scripts/test_ocr_live.py OCRtest.pdf
```

### 2. Avant de commit
```bash
# Vérifier formatage et qualité
black --check modules/ tests/
flake8 modules/

# Lancer les tests unitaires
pytest tests/ -v
```

### 3. Après commit
- Les tests unitaires tournent automatiquement (tests.yml)
- Vérifier les résultats dans l'onglet Actions

### 4. Avant une release
- Lancer manuellement les tests Docker (docker-tests.yml)
- Vérifier le rapport de couverture
- Valider que le pipeline complet fonctionne

## 📚 Ressources supplémentaires

- **Dockerfile**: `/Dockerfile`
- **Workflow tests unitaires**: `/.github/workflows/tests.yml`
- **Workflow tests Docker**: `/.github/workflows/docker-tests.yml`
- **Tests d'intégration**: `/tests/integration/`
- **Guide CI général**: `/docs/CI_GUIDE.md`

## 🎓 Concepts clés

### Docker Buildx
- Système de build moderne pour Docker
- Supporte le cache multi-layer
- Accélère les builds suivants

### GitHub Actions Cache
- Sauvegarde les layers Docker entre les builds
- Réduit le temps de build de 8min → 2min
- Se réinitialise si le Dockerfile change

### Matrix Strategy
- Permet de tester plusieurs versions en parallèle
- Utilisé dans tests.yml (Python 3.11, 3.12, 3.13)
- Pas utilisé dans docker-tests.yml (plus lent)

### Artifacts
- Fichiers générés par le workflow
- Téléchargeables depuis l'interface GitHub
- Rétention configurable (défaut: 30 jours)

---

**🎉 La CI/CD Docker est maintenant opérationnelle!**

Pour toute question, consulte:
- `/docs/CI_GUIDE.md` - Guide complet de la CI
- `/tests/integration/README.md` - Guide des tests d'intégration
- [Documentation GitHub Actions](https://docs.github.com/en/actions)
