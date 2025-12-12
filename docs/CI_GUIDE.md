# Guide CI/CD avec GitHub Actions pour HarpoTab

Ce document explique comment fonctionne l'intégration continue (CI) mise en place pour HarpoTab.

## 📚 Table des matières

1. [Qu'est-ce que la CI/CD?](#quest-ce-que-la-cicd)
2. [Comment ça fonctionne?](#comment-ça-fonctionne)
3. [Structure du workflow](#structure-du-workflow)
4. [Voir les résultats](#voir-les-résultats)
5. [Badges de statut](#badges-de-statut)
6. [Commandes locales](#commandes-locales)
7. [Dépannage](#dépannage)

---

## Qu'est-ce que la CI/CD?

**CI** = **Continuous Integration** (Intégration Continue)
- Teste automatiquement ton code à chaque modification
- Détecte les bugs avant qu'ils arrivent en production
- Vérifie que tout fonctionne sur différentes versions de Python

**CD** = **Continuous Deployment** (Déploiement Continu)
- Déploie automatiquement l'application (pas encore implémenté pour HarpoTab)

---

## Comment ça fonctionne?

### Vue d'ensemble

```
┌─────────────┐
│   Tu codes  │
│  localement │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│  git commit │────▶│  git push origin │
└─────────────┘     └────────┬─────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  GitHub détecte    │
                    │  .github/workflows/│
                    │     tests.yml      │
                    └────────┬───────────┘
                             │
                             ▼
           ┌─────────────────┴─────────────────┐
           │                                   │
           ▼                                   ▼
    ┌─────────────┐                    ┌─────────────┐
    │  Job Python │                    │  Job Python │
    │     3.11    │                    │     3.12    │
    └──────┬──────┘                    └──────┬──────┘
           │                                   │
           ▼                                   ▼
    ┌─────────────┐                    ┌─────────────┐
    │ Tests pass? │                    │ Tests pass? │
    │   ✅ / ❌   │                    │   ✅ / ❌   │
    └─────────────┘                    └─────────────┘
           │                                   │
           └───────────────┬───────────────────┘
                           ▼
                  ┌────────────────┐
                  │  Notification  │
                  │  email / badge │
                  └────────────────┘
```

### Étape par étape

1. **Tu fais un commit et push**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin main
   ```

2. **GitHub Actions détecte le push**
   - GitHub lit le fichier `.github/workflows/tests.yml`
   - Crée des machines virtuelles (runners) Ubuntu

3. **Exécution en parallèle**
   - 3 jobs lancés simultanément (Python 3.11, 3.12, 3.13)
   - Chaque job est indépendant

4. **Chaque job exécute:**
   ```yaml
   Checkout du code        # Clone le repo
   ↓
   Install Python 3.x      # Configure Python
   ↓
   Install dependencies    # pip install -r requirements.txt
   ↓
   Flake8 (linter)        # Vérifie qualité du code
   ↓
   Black (formatter)       # Vérifie formatage
   ↓
   Pytest                 # Exécute les tests
   ↓
   Coverage report        # Génère rapport de couverture
   ```

5. **Résultats visibles**
   - Logs détaillés dans l'onglet "Actions"
   - Email de notification si échec
   - Badge vert/rouge sur le README

---

## Structure du workflow

Le fichier `.github/workflows/tests.yml` est un fichier **YAML** qui décrit ce que GitHub doit faire.

### Anatomie d'un workflow YAML

```yaml
name: Tests                    # Nom du workflow

on:                           # Déclencheurs
  push:                       # Quand on push
    branches: ["**"]          # Sur toutes les branches
  pull_request:               # Quand on fait une PR
    branches: ["main"]        # Vers main

jobs:                         # Liste des jobs
  test:                       # Nom du job
    runs-on: ubuntu-latest    # OS de la machine virtuelle

    strategy:
      matrix:                 # Matrice = duplication du job
        python-version: ["3.11", "3.12", "3.13"]

    steps:                    # Étapes séquentielles
      - name: Checkout        # Nom de l'étape
        uses: actions/checkout@v4   # Action officielle

      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run tests
        run: pytest tests/    # Commande shell
```

### Concepts clés

#### 1. **Actions** (`uses:`)
Actions réutilisables créées par GitHub ou la communauté:
- `actions/checkout@v4` - Clone le repo
- `actions/setup-python@v5` - Installe Python
- `actions/upload-artifact@v4` - Upload des fichiers

#### 2. **Matrix** (`strategy.matrix`)
Duplique le job pour chaque valeur:
```yaml
matrix:
  python-version: ["3.11", "3.12", "3.13"]
  os: [ubuntu, windows, macos]
```
= 3 versions × 3 OS = **9 jobs en parallèle**

#### 3. **Variables** (`${{ }}`)
Accès aux variables du contexte:
```yaml
${{ matrix.python-version }}  # 3.11, 3.12 ou 3.13
${{ github.ref }}             # Branche actuelle
${{ secrets.API_KEY }}        # Secret stocké dans GitHub
```

#### 4. **Conditions** (`if:`)
Exécuter une étape conditionnellement:
```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: ./deploy.sh
```

---

## Voir les résultats

### 1. Via l'interface GitHub

1. Va sur ton repo GitHub
2. Clique sur l'onglet **"Actions"** (en haut)
3. Tu verras la liste de tous les workflows exécutés

**Exemple de vue:**
```
✅ Tests - Add new feature (#12)
   └─ test (3.11) ✅
   └─ test (3.12) ✅
   └─ test (3.13) ✅

❌ Tests - Fix bug (#11)
   └─ test (3.11) ✅
   └─ test (3.12) ❌  ← Échec ici
   └─ test (3.13) ✅
```

4. Clique sur un job pour voir les **logs détaillés**

### 2. Via les commits

Sur la page principale du repo, chaque commit a une icône:
- ✅ Vert = tous les tests passent
- ❌ Rouge = au moins un test échoue
- 🟡 Jaune = en cours d'exécution

### 3. Via les notifications

GitHub t'envoie un email si:
- Un workflow échoue
- Tu es mentionné dans une PR avec tests qui échouent

---

## Badges de statut

Tu peux ajouter un badge au README pour montrer le statut des tests:

```markdown
![Tests](https://github.com/USERNAME/HarpoTab/actions/workflows/tests.yml/badge.svg)
```

Le badge affichera:
- **passing** (vert) si tous les tests passent
- **failing** (rouge) si au moins un test échoue

---

## Commandes locales

Pour **tester localement** avant de push (simule ce que fait la CI):

### 1. Linter (flake8)
```bash
# Erreurs critiques seulement
flake8 modules/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Tous les warnings
flake8 modules/ --count --max-complexity=10 --max-line-length=127 --statistics
```

### 2. Formatage (black)
```bash
# Vérifier le formatage (ne modifie pas)
black --check --diff modules/ tests/

# Formater automatiquement
black modules/ tests/
```

### 3. Tests (pytest)
```bash
# Tests simples
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=modules --cov-report=term-missing

# Générer un rapport HTML
pytest tests/ --cov=modules --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

### 4. Tout en une commande
```bash
# Script pour tout tester avant de commit
./scripts/pre-commit-check.sh
```

*(À créer si besoin)*

---

## Dépannage

### ❌ Les tests passent localement mais échouent sur GitHub

**Causes possibles:**

1. **Dépendances manquantes dans requirements.txt**
   ```bash
   # Vérifie que toutes les dépendances sont listées
   pip freeze > requirements-full.txt
   # Compare avec requirements.txt
   ```

2. **Différence de version Python**
   - Localement: Python 3.13
   - GitHub: Python 3.11, 3.12, 3.13

   → Teste localement avec pyenv:
   ```bash
   pyenv install 3.11.0
   pyenv shell 3.11.0
   pytest tests/
   ```

3. **Chemins absolus vs relatifs**
   ```python
   # ❌ Mauvais
   with open('/home/user/data.json')

   # ✅ Bon
   with open('data/data.json')
   ```

4. **Variables d'environnement**
   - Si tu utilises des `.env` locaux
   - Sur GitHub, ajoute les dans **Settings → Secrets**

### ❌ Le workflow ne se déclenche pas

**Vérifications:**

1. Le fichier est bien à `.github/workflows/tests.yml` (avec le "s")
2. L'indentation YAML est correcte (utilise des espaces, pas de tabs)
3. Tu as bien push le fichier:
   ```bash
   git add .github/workflows/tests.yml
   git commit -m "Add CI workflow"
   git push origin main
   ```

### ❌ Timeout (le job dure trop longtemps)

Par défaut, GitHub limite les jobs à **6 heures**.

Pour HarpoTab:
- Tests unitaires: ~10 secondes ✅
- Tests OCR complets: >5 minutes ⚠️

**Solution:** Séparer les tests longs dans un workflow manuel.

### 🐛 Débugger un problème

1. **Activer le mode debug**
   - Settings → Secrets → Add: `ACTIONS_STEP_DEBUG` = `true`

2. **Ajouter des prints**
   ```yaml
   - name: Debug info
     run: |
       echo "Python version: $(python --version)"
       echo "Working directory: $(pwd)"
       echo "Files: $(ls -la)"
       pip list
   ```

3. **SSH dans le runner** (avancé)
   - Utiliser l'action `action-tmate` pour se connecter en SSH

---

## Ressources

- [Documentation officielle GitHub Actions](https://docs.github.com/en/actions)
- [Marketplace des Actions](https://github.com/marketplace?type=actions)
- [YAML Syntax](https://yaml.org/)
- [Exemples de workflows Python](https://github.com/actions/starter-workflows/blob/main/ci/python-package.yml)

---

## Prochaines étapes

Pour améliorer la CI de HarpoTab:

1. **Ajouter des tests d'intégration**
   - Workflow séparé pour tests OCR (manuel)

2. **Déploiement automatique** (CD)
   - Déployer sur Heroku/Railway quand merge sur main

3. **Matrix étendue**
   - Tester sur Windows et macOS

4. **Artifacts**
   - Garder les fichiers MXL générés pour debug

5. **Notifications Slack/Discord**
   - Webhook pour notifier l'équipe

---

**Question?** Regarde les logs dans l'onglet Actions ou demande de l'aide! 🚀
