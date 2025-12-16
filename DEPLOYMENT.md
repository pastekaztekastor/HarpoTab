# 🚀 Guide de Déploiement - Raspberry Pi

Guide complet pour déployer automatiquement HarpoTab sur un Raspberry Pi avec GitHub Actions.

---

## 🎯 **Vue d'ensemble**

```
Push code → GitHub Actions → Docker Hub/GHCR → Raspberry Pi → Site déployé ! ✅
```

**Temps de déploiement :** ~5-10 minutes (après le premier build)

---

## 📋 **Prérequis**

### **Sur ton PC :**
- [x] Compte GitHub avec ce repo
- [ ] Compte Docker Hub **OU** utiliser GitHub Container Registry (gratuit)

### **Sur le Raspberry Pi :**
- [ ] Raspberry Pi 3/4/5 avec Raspbian OS
- [ ] Docker installé
- [ ] SSH activé
- [ ] Connexion Internet

---

## 🔧 **Étape 1 : Préparer le Raspberry Pi**

### **1.1 Installer Docker sur le Raspberry Pi**

```bash
# Se connecter au Raspberry Pi
ssh pi@raspberrypi.local
# (mot de passe par défaut : raspberry)

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Se déconnecter et se reconnecter pour appliquer les changements
exit
ssh pi@raspberrypi.local

# Vérifier que Docker fonctionne
docker --version
docker ps
```

### **1.2 Créer les dossiers de données**

```bash
# Créer les dossiers pour les volumes Docker
mkdir -p ~/harpotab/data
mkdir -p ~/harpotab/uploads
mkdir -p ~/harpotab/outputs

# Donner les permissions
chmod -R 755 ~/harpotab
```

### **1.3 Configurer SSH (si nécessaire)**

```bash
# Activer SSH si pas déjà fait
sudo systemctl enable ssh
sudo systemctl start ssh

# Vérifier que SSH écoute
sudo systemctl status ssh
```

---

## 🔑 **Étape 2 : Générer une clé SSH pour GitHub Actions**

### **Sur ton PC :**

```bash
# Générer une paire de clés SSH dédiée au déploiement
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/raspi_deploy

# IMPORTANT : Ne pas mettre de passphrase (appuie sur Entrée 2 fois)
```

### **Copier la clé publique sur le Raspberry Pi :**

```bash
# Méthode 1 : ssh-copy-id (automatique)
ssh-copy-id -i ~/.ssh/raspi_deploy.pub pi@raspberrypi.local

# Méthode 2 : Manuel
# Sur ton PC :
cat ~/.ssh/raspi_deploy.pub

# Sur le Raspberry Pi :
ssh pi@raspberrypi.local
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Colle la clé publique à la fin du fichier
# Ctrl+X, Y, Entrée pour sauvegarder
chmod 600 ~/.ssh/authorized_keys
exit
```

### **Tester la connexion SSH :**

```bash
# Depuis ton PC
ssh -i ~/.ssh/raspi_deploy pi@raspberrypi.local

# Tu ne devrais PAS avoir à entrer de mot de passe
# Si ça marche, tu peux te déconnecter
exit
```

---

## 🐳 **Étape 3 : Choisir Docker Hub ou GHCR**

Tu as 2 options pour stocker tes images Docker :

### **Option A : Docker Hub (plus simple)**

**Avantages :**
- ✅ Interface web simple
- ✅ 1 repo privé gratuit

**Étapes :**
1. Créer un compte sur https://hub.docker.com
2. Créer un Access Token :
   - Hub → Account Settings → Security → New Access Token
   - Nom : "github-actions"
   - Permissions : Read, Write, Delete
   - **Copier le token** (tu ne le reverras plus !)

**Secrets à configurer :**
- `DOCKER_USERNAME` : ton nom d'utilisateur Docker Hub
- `DOCKER_PASSWORD` : le token d'accès généré

### **Option B : GitHub Container Registry (recommandé)**

**Avantages :**
- ✅ Gratuit et illimité
- ✅ Intégré à GitHub
- ✅ Pas besoin de compte externe

**Étapes :**
1. Aller sur ton repo GitHub
2. Settings → Actions → General
3. Scroll jusqu'à "Workflow permissions"
4. Cocher "Read and write permissions"
5. Save

**Modification du workflow :**
Dans `.github/workflows/deploy-raspberry-pi.yml` :
- Commenter les lignes Docker Hub (lignes 62-66)
- Décommenter les lignes GHCR (lignes 68-73)

**Secrets à configurer :**
- Aucun ! `GITHUB_TOKEN` est automatique

---

## 🔐 **Étape 4 : Configurer les secrets GitHub**

### **Sur GitHub :**

1. Aller sur ton repo GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquer sur **"New repository secret"**

### **Ajouter ces secrets :**

#### **Obligatoires :**

| Nom | Valeur | Exemple |
|-----|--------|---------|
| `RASPI_HOST` | IP ou hostname du Raspberry Pi | `192.168.1.100` ou `raspberrypi.local` |
| `RASPI_USER` | Nom d'utilisateur SSH | `pi` |
| `RASPI_SSH_KEY` | Contenu de la clé privée | Contenu de `~/.ssh/raspi_deploy` |

#### **Si tu utilises Docker Hub (Option A) :**

| Nom | Valeur |
|-----|--------|
| `DOCKER_USERNAME` | Ton nom d'utilisateur Docker Hub |
| `DOCKER_PASSWORD` | Ton token d'accès Docker Hub |

#### **Optionnel :**

| Nom | Valeur | Défaut |
|-----|--------|--------|
| `RASPI_PORT` | Port SSH du Raspberry Pi | `22` |

### **Comment copier la clé SSH privée :**

```bash
# Sur ton PC
cat ~/.ssh/raspi_deploy

# Copier TOUT le contenu (y compris les lignes BEGIN/END)
# -----BEGIN OPENSSH PRIVATE KEY-----
# ...
# -----END OPENSSH PRIVATE KEY-----

# Coller dans le secret RASPI_SSH_KEY sur GitHub
```

---

## ✅ **Étape 5 : Tester le déploiement**

### **Méthode 1 : Push vers main**

```bash
# Sur ton PC, dans le repo HarpoTab
git add .
git commit -m "🚀 Setup CD pour Raspberry Pi"
git push origin main

# Aller sur GitHub → Actions
# Tu devrais voir le workflow "Deploy to Raspberry Pi" se lancer
```

### **Méthode 2 : Déploiement manuel**

1. Aller sur GitHub → **Actions**
2. Cliquer sur **"Deploy to Raspberry Pi"** (dans la sidebar)
3. Cliquer sur **"Run workflow"**
4. Sélectionner la branche `main`
5. Cliquer sur **"Run workflow"**

### **Vérifier le déploiement :**

```bash
# Sur le Raspberry Pi
ssh pi@raspberrypi.local

# Vérifier que le conteneur tourne
docker ps | grep harpotab

# Voir les logs
docker logs harpotab

# Tester l'app
curl http://localhost:5000

# Ou depuis ton PC (remplace par l'IP du Raspberry Pi)
curl http://192.168.1.100:5000
```

### **Accéder au site :**

Ouvre ton navigateur :
- **Depuis le Raspberry Pi :** http://localhost:5000
- **Depuis ton réseau local :** http://192.168.1.100:5000
- **Avec hostname :** http://raspberrypi.local:5000

---

## 🔍 **Dépannage**

### **Erreur : "Permission denied (publickey)"**

```bash
# Vérifier que la clé SSH est bien configurée
ssh -i ~/.ssh/raspi_deploy pi@raspberrypi.local

# Vérifier les permissions sur le Raspberry Pi
ssh pi@raspberrypi.local
ls -la ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### **Erreur : "docker: command not found" sur le Raspberry Pi**

```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Se déconnecter et reconnecter
exit
ssh pi@raspberrypi.local
```

### **Erreur : "dial tcp: lookup raspberrypi.local"**

```bash
# Utiliser l'IP directement au lieu du hostname
# Sur le Raspberry Pi :
hostname -I

# Mettre cette IP dans le secret RASPI_HOST sur GitHub
```

### **Le conteneur ne démarre pas**

```bash
# Voir les logs d'erreur
ssh pi@raspberrypi.local
docker logs harpotab

# Vérifier l'espace disque
df -h

# Vérifier la RAM
free -h

# Redémarrer le conteneur manuellement
docker restart harpotab
```

### **L'image Docker est trop grosse pour le Raspberry Pi**

```bash
# Raspberry Pi 3 : minimum 1 GB RAM recommandé
# Raspberry Pi 4/5 : 2+ GB RAM recommandé

# Vérifier la mémoire disponible
ssh pi@raspberrypi.local
free -h

# Augmenter le swap si nécessaire
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Changer CONF_SWAPSIZE à 2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 🎨 **Étape 6 : Optimisations (optionnelles)**

### **Activer HTTPS avec Let's Encrypt**

```bash
# Installer Nginx sur le Raspberry Pi
ssh pi@raspberrypi.local
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx

# Configurer Nginx comme reverse proxy
sudo nano /etc/nginx/sites-available/harpotab

# Ajouter :
server {
    listen 80;
    server_name ton-domaine.com;  # ou ton IP publique

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Activer le site
sudo ln -s /etc/nginx/sites-available/harpotab /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtenir un certificat SSL (si tu as un domaine)
sudo certbot --nginx -d ton-domaine.com
```

### **Configurer un domaine dynamique (DynDNS)**

Si ton IP publique change souvent :
- Utiliser un service comme No-IP, DuckDNS, ou DynDNS
- Configurer un client DynDNS sur le Raspberry Pi

### **Sauvegardes automatiques**

```bash
# Créer un script de backup sur le Raspberry Pi
nano ~/backup_harpotab.sh

# Ajouter :
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/backups/harpotab_$DATE.tar.gz ~/harpotab/data ~/harpotab/uploads ~/harpotab/outputs
find ~/backups -name "harpotab_*.tar.gz" -mtime +7 -delete

# Rendre exécutable
chmod +x ~/backup_harpotab.sh

# Ajouter au cron (tous les jours à 2h du matin)
crontab -e
# Ajouter : 0 2 * * * /home/pi/backup_harpotab.sh
```

---

## 📊 **Monitoring**

### **Vérifier l'état du déploiement**

```bash
# Sur le Raspberry Pi
docker ps                          # Conteneurs en cours
docker stats harpotab              # Usage CPU/RAM en temps réel
docker logs harpotab -f            # Logs en direct
docker inspect harpotab            # Infos détaillées
```

### **Webhooks de notification (optionnel)**

Ajouter un step dans le workflow pour notifier sur Discord/Slack/Email :

```yaml
- name: Notification Discord
  if: always()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
    title: "Déploiement HarpoTab"
```

---

## 🎯 **Récapitulatif**

**Configuration initiale :** ~30 minutes

**Déploiements futurs :** Automatiques ! (~5-10 min)

**Checklist :**
- [x] Docker installé sur Raspberry Pi
- [x] SSH configuré avec clé publique
- [x] Secrets GitHub configurés
- [x] Workflow testé et fonctionnel
- [x] Site accessible sur http://raspberrypi.local:5000

**Prochaines étapes :**
- [ ] Configurer HTTPS (optionnel)
- [ ] Ajouter un domaine personnalisé (optionnel)
- [ ] Mettre en place des backups automatiques
- [ ] Ajouter du monitoring

---

## 📚 **Ressources**

- [Docker sur Raspberry Pi](https://docs.docker.com/engine/install/debian/)
- [GitHub Actions SSH](https://github.com/appleboy/ssh-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)

---

**Besoin d'aide ?** Consulte les logs GitHub Actions ou les logs Docker sur le Raspberry Pi ! 🚀
