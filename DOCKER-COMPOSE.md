# 🐳 Architecture Docker Compose - HarpoTab

Guide pour l'architecture microservices avec Audiveris séparé.

---

## 📊 **Architecture**

```
┌──────────────────────────────────────────────────────┐
│              Docker Compose Network                   │
│                                                        │
│  ┌───────────────────────┐  ┌──────────────────────┐ │
│  │   harpotab-app        │  │  harpotab-audiveris  │ │
│  │   (Flask Python)      │◄─┤  (Java + Audiveris) │ │
│  │                       │  │                      │ │
│  │  - Flask web UI       │  │  - Audiveris 5.9.0   │ │
│  │  - Lilypond           │  │  - Java 21           │ │
│  │  - Python modules     │  │  - Tesseract OCR     │ │
│  │                       │  │  - API HTTP:8080     │ │
│  │  Port: 5000           │  │                      │ │
│  └───────────────────────┘  └──────────────────────┘ │
│           │                            │              │
│           └────────────────────────────┘              │
│                      │                                │
│              Volumes partagés                         │
│         uploads/ outputs/ data/                       │
└──────────────────────────────────────────────────────┘
```

---

## ✅ **Avantages de cette architecture**

| Aspect | Monolithe | Docker Compose |
|--------|-----------|----------------|
| **Build app** | ~10 min | ~30 sec ⚡ |
| **Taille image app** | ~2 GB | ~500 MB |
| **Isolation** | ❌ Tout dans 1 conteneur | ✅ Services séparés |
| **Scalabilité** | ❌ Difficile | ✅ Facile (scale audiveris) |
| **Debug** | ⚠️ Rebuild complet | ✅ Rebuild seulement le service modifié |
| **Production** | ⚠️ Lourd | ✅ Optimisé |

---

## 🚀 **Utilisation**

### **Build et lancer les services**

```bash
# Première fois : build les 2 images
docker-compose up --build

# Builds suivants (si rien n'a changé)
docker-compose up

# En mode détaché (background)
docker-compose up -d
```

### **Arrêter les services**

```bash
# Arrêter proprement
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### **Rebuild un seul service**

```bash
# Rebuild seulement l'app Flask (rapide !)
docker-compose up --build app

# Rebuild seulement Audiveris
docker-compose up --build audiveris
```

---

## 📝 **Logs**

```bash
# Voir les logs de tous les services
docker-compose logs -f

# Logs de l'app seulement
docker-compose logs -f app

# Logs d'Audiveris seulement
docker-compose logs -f audiveris

# Dernières 100 lignes
docker-compose logs --tail=100 app
```

---

## 🔍 **Debugging**

### **Accéder au shell d'un conteneur**

```bash
# Shell dans l'app Flask
docker-compose exec app /bin/bash

# Shell dans Audiveris
docker-compose exec audiveris /bin/bash
```

### **Tester l'API Audiveris directement**

```bash
# Vérifier la santé du service
curl http://localhost:8080/health

# Envoyer une partition pour OCR
curl -X POST -F "file=@partition.pdf" http://localhost:8080/ocr

# Lister les fichiers générés
curl http://localhost:8080/list
```

### **Vérifier les volumes**

```bash
# Lister les volumes
docker volume ls | grep harpotab

# Inspecter un volume
docker volume inspect harpotab_uploads
```

---

## 🎯 **Workflow de développement**

### **Scénario 1 : Tu modifies le code Python (app.py, modules/)**

```bash
# Le code est monté en volume, donc les changements sont immédiats !
# Juste redémarrer Flask :
docker-compose restart app

# Ou si tu veux rebuild l'image :
docker-compose up --build app
```

**Temps : ~30 secondes** ⚡

### **Scénario 2 : Tu modifies requirements.txt**

```bash
# Rebuild l'app avec les nouvelles dépendances
docker-compose build app
docker-compose up app
```

**Temps : ~1-2 minutes**

### **Scénario 3 : Tu veux mettre à jour Audiveris**

```bash
# Rebuild seulement le service Audiveris
docker-compose build audiveris
docker-compose up audiveris
```

**Temps : ~10 minutes** (mais rare !)

---

## 🧪 **Tests**

### **Tester l'application complète**

```bash
# Lancer les tests dans le conteneur app
docker-compose exec app pytest tests/ -v

# Ou lancer un conteneur temporaire
docker-compose run --rm app pytest tests/
```

### **Tester uniquement Audiveris**

```bash
# Vérifier qu'Audiveris fonctionne
docker-compose exec audiveris audiveris --help

# Tester l'API HTTP
docker-compose exec audiveris curl -X GET http://localhost:8080/health
```

---

## 📦 **Structure des fichiers**

```
HarpoTab/
├── Dockerfile                     # App Flask (léger)
├── Dockerfile.monolith            # Ancien monolithe (backup)
├── docker-compose.yml             # Orchestration
├── docker/
│   └── audiveris/
│       ├── Dockerfile             # Service Audiveris
│       └── server.py              # API HTTP pour Audiveris
├── modules/
│   ├── ocr_reader.py              # Ancien (subprocess)
│   └── ocr_reader_http.py         # Nouveau (HTTP API)
└── ...
```

---

## 🔧 **Configuration avancée**

### **Scaler le service Audiveris**

```bash
# Lancer 3 instances d'Audiveris (pour gérer la charge)
docker-compose up --scale audiveris=3
```

### **Variables d'environnement**

Créer un fichier `.env` :

```bash
# .env
FLASK_ENV=production
AUDIVERIS_SERVICE_URL=http://audiveris:8080
```

Puis :

```bash
docker-compose --env-file .env up
```

### **Persist les données**

Les volumes Docker persistent automatiquement :

- `uploads/` : Fichiers uploadés
- `outputs/` : Fichiers générés
- `data/` : Base de données (si tu en ajoutes une plus tard)

```bash
# Backup des volumes
docker run --rm -v harpotab_data:/data -v $(pwd):/backup ubuntu tar czf /backup/data-backup.tar.gz /data

# Restore
docker run --rm -v harpotab_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/data-backup.tar.gz -C /
```

---

## 🌐 **Déploiement sur Raspberry Pi**

### **Option 1 : Copier docker-compose.yml**

```bash
# Sur ton PC
scp docker-compose.yml pi@raspberrypi.local:~/harpotab/
scp -r docker/ pi@raspberrypi.local:~/harpotab/

# Sur le Raspberry Pi
ssh pi@raspberrypi.local
cd ~/harpotab
docker-compose up -d
```

### **Option 2 : Via GitHub Actions (recommandé)**

Le workflow `.github/workflows/deploy-raspberry-pi.yml` est déjà configuré !

Il faudra juste :
1. Pousser `docker-compose.yml` sur `main`
2. Le workflow build les images et les déploie automatiquement

---

## 🐛 **Dépannage**

### **Erreur : "Cannot connect to Audiveris service"**

```bash
# Vérifier que le service audiveris tourne
docker-compose ps

# Vérifier les logs
docker-compose logs audiveris

# Redémarrer le service
docker-compose restart audiveris
```

### **Erreur : "Port 5000 already in use"**

```bash
# Changer le port dans docker-compose.yml
ports:
  - "5001:5000"  # Utilise 5001 au lieu de 5000
```

### **Build très lent**

```bash
# Vérifier .dockerignore existe
cat .dockerignore

# Nettoyer les images/conteneurs inutilisés
docker system prune -f

# Rebuild avec cache désactivé
docker-compose build --no-cache
```

### **Volumes pleins**

```bash
# Voir l'utilisation
docker system df

# Nettoyer tout (ATTENTION : supprime TOUTES les données Docker !)
docker system prune -a --volumes
```

---

## 📊 **Comparaison des approches**

### **Monolithe (Dockerfile.monolith)**

```bash
# Build
docker build -t harpotab:latest .

# Run
docker run -p 5000:5000 harpotab:latest
```

**Avantages :**
- ✅ Simple (1 seul conteneur)
- ✅ Facile à comprendre

**Inconvénients :**
- ❌ Build long (~10 min)
- ❌ Image lourde (~2 GB)
- ❌ Rebuild complet pour chaque modif

### **Docker Compose (architecture actuelle)**

```bash
# Build + Run
docker-compose up --build
```

**Avantages :**
- ✅ Build app rapide (~30 sec)
- ✅ Services isolés
- ✅ Scalable
- ✅ Rebuild partiel

**Inconvénients :**
- ⚠️ Un peu plus complexe (2 services)

---

## 🎓 **Migration de l'ancien code**

Pour utiliser la nouvelle API HTTP au lieu de subprocess :

### **Ancien code (ocr_reader.py)**

```python
from modules.ocr_reader import AudiverisOCR

ocr = AudiverisOCR()
result = ocr.read_partition(pdf_path, output_dir)
```

### **Nouveau code (ocr_reader_http.py)**

```python
from modules.ocr_reader_http import AudiverisHTTPClient

client = AudiverisHTTPClient()
result = client.read_partition(pdf_path, output_dir)
```

**Pas besoin de changer la logique !** Les deux ont la même interface. 🎉

---

## 📚 **Ressources**

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)
- [Audiveris Documentation](https://audiveris.github.io/audiveris/)

---

**Prêt à builder ? Lance `docker-compose up --build` ! 🚀**
