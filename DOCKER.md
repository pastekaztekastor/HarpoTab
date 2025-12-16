# 🐳 Guide Docker - HarpoTab

Guide complet pour utiliser HarpoTab avec Docker (incluant Audiveris OCR).

---

## 📦 **Image Docker**

L'image `harpotab:latest` contient :
- ✅ Ubuntu 22.04
- ✅ Python 3.11
- ✅ Java 21
- ✅ **Audiveris 5.9.0** (OCR partitions musicales)
- ✅ Tesseract OCR (FR + EN)
- ✅ Lilypond (génération partitions)
- ✅ Toutes les dépendances HarpoTab

**Taille totale :** ~2 GB
**Temps de build :** ~25-30 min (première fois)

---

## 🚀 **Utilisation rapide**

### **1. Builder l'image**

```bash
# Build initial (~25-30 min)
docker build -t harpotab:latest .

# Les builds suivants sont plus rapides grâce au cache (~2-5 min)
```

### **2. Lancer les tests**

```bash
# Lancer tous les tests (mode par défaut)
docker run --rm harpotab:latest

# Lancer les tests avec plus de verbosité
docker run --rm harpotab:latest pytest tests/ -vv

# Lancer un test spécifique
docker run --rm harpotab:latest pytest tests/test_ocr_reader.py -v
```

### **3. Lancer l'application Flask**

```bash
# Lancer le serveur Flask (mode développement)
docker run --rm -p 5000:5000 harpotab:latest python app.py

# Accéder à l'app : http://localhost:5000
```

### **4. Shell interactif (debug)**

```bash
# Entrer dans le conteneur
docker run -it --rm harpotab:latest /bin/bash

# Une fois à l'intérieur :
python --version   # Python 3.11
java --version     # Java 21
audiveris --help   # Audiveris 5.9.0
tesseract --version
lilypond --version
```

---

## 🧪 **Tests avec Audiveris**

### **Tester l'OCR sur une partition**

```bash
# Copier un PDF dans le conteneur et lancer l'OCR
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  harpotab:latest \
  python -c "
from modules.ocr_reader import AudiverisOCR
ocr = AudiverisOCR()
result = ocr.extract_musicxml('/app/data/partition.pdf')
print(result)
"
```

### **Monter un volume pour accéder aux fichiers**

```bash
# Monter le dossier actuel dans /app/data
docker run -it --rm \
  -v $(pwd):/app/workspace \
  harpotab:latest /bin/bash

# Maintenant tu peux accéder à tes fichiers dans /app/workspace
```

---

## 📊 **GitHub Actions CI/CD**

### **Workflow standard (tests rapides)**

`.github/workflows/tests.yml` :
- ✅ Tests unitaires (~30s)
- ✅ Linting + formatage
- ✅ Multi-versions Python (3.11, 3.12, 3.13)
- ❌ **Sans** Audiveris (plus rapide)

```bash
# Se déclenche automatiquement sur push/PR
```

### **Workflow Docker (tests d'intégration)**

`.github/workflows/docker-tests.yml` :
- ✅ Tests d'intégration complets (~10 min)
- ✅ **Avec** Audiveris
- ✅ Build de l'image Docker
- ✅ Rapport de couverture

```bash
# Lancement manuel uniquement (pour économiser les minutes CI)
# GitHub → Actions → "Docker Integration Tests" → "Run workflow"
```

---

## 🔧 **Optimisations**

### **Réduire la taille de l'image**

L'image est déjà optimisée :
- ✅ `apt-get clean` après installation
- ✅ Suppression des fichiers `.deb` après install
- ✅ `--no-cache-dir` pour pip
- ✅ `.dockerignore` exclut les fichiers inutiles

### **Accélérer les builds**

```bash
# Le cache Docker est automatique
# Si tu modifies uniquement le code Python, seules les dernières layers sont rebuild

# Pour forcer un rebuild complet (sans cache) :
docker build --no-cache -t harpotab:latest .
```

---

## 🐛 **Dépannage**

### **Erreur "dpkg: error processing Audiveris"**

```bash
# Vérifier que l'URL Audiveris est correcte
wget --spider https://github.com/Audiveris/audiveris/releases/download/5.9.0/Audiveris-5.9.0-ubuntu22.04-x86_64.deb

# Si 404, mettre à jour l'URL dans le Dockerfile (ligne 58)
```

### **Build très lent**

```bash
# Vérifier que .dockerignore existe
ls -la .dockerignore

# Vérifier la taille du contexte Docker
docker build --no-cache -t harpotab:latest . 2>&1 | grep "Sending build context"

# Devrait être ~10 MB (pas 300+ MB)
```

### **Tests échouent dans Docker mais passent localement**

```bash
# Vérifier les versions des outils
docker run --rm harpotab:latest python --version
docker run --rm harpotab:latest java --version

# Comparer avec ta version locale
python --version
java --version
```

---

## 📝 **Commandes utiles**

```bash
# Voir les images Docker
docker images

# Supprimer l'image
docker rmi harpotab:latest

# Nettoyer les conteneurs/images inutilisés
docker system prune -f

# Voir les layers de l'image
docker history harpotab:latest

# Inspecter l'image
docker inspect harpotab:latest
```

---

## 🎯 **Prochaines étapes**

- [ ] Tester l'image Docker localement
- [ ] Lancer le workflow GitHub Actions
- [ ] Ajouter des tests d'intégration avec de vraies partitions
- [ ] Optimiser encore la taille de l'image (multi-stage build ?)
- [ ] Publier l'image sur Docker Hub (optionnel)

---

## 📚 **Ressources**

- [Audiveris Documentation](https://audiveris.github.io/audiveris/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
