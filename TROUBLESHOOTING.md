# Dépannage HarpoTab

## Problème : Installation d'Audiveris échoue

### Erreur rencontrée
```
curl: (33) HTTP server does not seem to support byte ranges. Cannot resume.
ERREUR : Erreur lors du téléchargement de https://github.com/Audiveris/audiveris/...
```

### ⚠️ IMPORTANT : Audiveris est OPTIONNEL

**L'application HarpoTab fonctionne SANS Audiveris !**

Sans Audiveris, l'application utilise :
- ✅ Données de démonstration pour tester
- ✅ Support MusicXML direct (si music21 installé)
- ✅ Toutes les autres fonctionnalités (édition, playback, etc.)

**Audiveris n'est requis QUE pour l'OCR réel de partitions PDF/images.**

---

## Solutions pour Audiveris

### Solution 1 : Ignorer Audiveris (Recommandé)

**Utilise plutôt MusicXML :**

1. Ouvre ta partition dans MuseScore (gratuit)
2. Exporte en MusicXML (.musicxml)
3. Upload le fichier .musicxml dans HarpoTab
4. **Résultat parfait sans OCR !**

### Solution 2 : Réessayer plus tard

Les problèmes de téléchargement GitHub sont souvent temporaires.

```bash
# Nettoyer le cache yay
yay -Sc

# Réessayer
yay -S audiveris
```

### Solution 3 : Installation manuelle d'Audiveris

#### A. Via AUR (méthode alternative)
```bash
# Cloner le dépôt AUR
git clone https://aur.archlinux.org/audiveris.git
cd audiveris

# Modifier le PKGBUILD si nécessaire
nano PKGBUILD

# Compiler et installer
makepkg -si
```

#### B. Depuis les sources
```bash
# Installer les dépendances
sudo pacman -S jdk-openjdk gradle

# Cloner Audiveris
git clone https://github.com/Audiveris/audiveris.git
cd audiveris

# Compiler
gradle build

# Créer un script de lancement
echo '#!/bin/bash' > ~/bin/audiveris
echo 'java -jar /chemin/vers/audiveris/build/libs/audiveris.jar "$@"' >> ~/bin/audiveris
chmod +x ~/bin/audiveris
```

#### C. Version pré-compilée
```bash
# Télécharger la version pré-compilée depuis GitHub Releases
wget https://github.com/Audiveris/audiveris/releases/download/5.7.1/Audiveris-5.7.1.zip

# Décompresser
unzip Audiveris-5.7.1.zip

# Lancer
cd Audiveris-5.7.1
./bin/audiveris
```

---

## Problème : music21 n'installe pas

### Erreur : Timeout / Connection failed

**Solution 1 : Réessayer avec cache désactivé**
```bash
source venv/bin/activate
pip install --no-cache-dir music21
```

**Solution 2 : Installer sans dépendances optionnelles**
```bash
source venv/bin/activate
pip install --no-deps music21
pip install chardet jsonpickle more-itertools webcolors
```

**Solution 3 : Utiliser un miroir PyPI**
```bash
source venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple music21
```

**Solution 4 : Installation minimale**
```bash
# Installer uniquement les dépendances critiques
source venv/bin/activate
pip install 'music21[lite]'
```

---

## Problème : Port 5000 déjà utilisé

### Erreur
```
OSError: [Errno 98] Address already in use
```

### Solution
Modifier `app.py`, dernière ligne :
```python
# Changer le port
app.run(debug=True, host='0.0.0.0', port=8080)
```

Puis relancer :
```bash
./run.sh
# Ouvrir : http://localhost:8080
```

---

## Problème : Dossier uploads n'existe pas

### Erreur
```
FileNotFoundError: [Errno 2] No such file or directory: 'static/uploads'
```

### Solution
```bash
mkdir -p static/uploads static/output static/lilypond
chmod 755 static/uploads static/output static/lilypond
```

---

## Problème : LilyPond non trouvé

### Erreur
```
FileNotFoundError: [Errno 2] No such file or directory: 'lilypond'
```

### Solution
```bash
# Installer LilyPond
sudo pacman -S lilypond

# Vérifier
which lilypond
lilypond --version
```

Sans LilyPond, l'application utilise ReportLab (génération PDF basique).

---

## Problème : Module non trouvé

### Erreur
```
ModuleNotFoundError: No module named 'flask' (ou autre)
```

### Solution
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt

# Vérifier
pip list
```

---

## Vérification Complète

```bash
# 1. Vérifier l'environnement virtuel
source venv/bin/activate

# 2. Vérifier les modules Python
python check_system.py

# 3. Tester l'application
./run.sh
```

---

## Configuration Minimale Fonctionnelle

**Pour que HarpoTab fonctionne, il faut MINIMUM :**

✅ **Requis (déjà installé) :**
- Python 3.8+
- Flask
- Pillow
- ReportLab
- pdfplumber

⚠️ **Recommandé :**
- LilyPond (PDF professionnels)
- music21 (support MusicXML)

❌ **Optionnel :**
- Audiveris (OCR réel)
- OpenCV (analyse images avancée)

---

## Workflow Sans Audiveris (Recommandé)

### Méthode 1 : Via MuseScore (MEILLEUR RÉSULTAT)

1. **Obtenir la partition dans MuseScore**
   - Scanner la partition → MuseScore (OCR intégré)
   - Ou télécharger depuis MuseScore.com
   - Ou créer manuellement

2. **Exporter en MusicXML**
   - Fichier → Exporter → MusicXML (.musicxml)

3. **Upload dans HarpoTab**
   - Upload du fichier .musicxml
   - Conversion automatique parfaite !

### Méthode 2 : Édition Manuelle

1. **Upload n'importe quelle partition** (données de démo chargées)
2. **Cliquer "Éditer la tablature"**
3. **Modifier manuellement** chaque note
4. **Régénérer le PDF**

### Méthode 3 : Avec music21 uniquement

Si tu as music21 installé :
- Import MusicXML direct
- Parsing haute précision
- Pas besoin d'Audiveris

---

## Commandes Utiles

### Vérifier l'installation
```bash
python check_system.py
```

### Nettoyer et réinstaller
```bash
# Supprimer l'environnement virtuel
rm -rf venv

# Relancer l'installation
./setup.sh
```

### Tester sans lancer l'app
```bash
source venv/bin/activate
python -c "from modules.pdf_reader import extract_music_from_pdf; print('OK')"
```

### Vérifier les logs
```bash
# Lancer avec logs détaillés
source venv/bin/activate
python app.py
```

---

## FAQ

**Q : L'app fonctionne sans Audiveris ?**
✅ OUI ! Audiveris est optionnel.

**Q : L'app fonctionne sans music21 ?**
✅ OUI ! Mais tu ne pourras pas importer de fichiers MusicXML.

**Q : Quelle est la meilleure méthode sans Audiveris ?**
💡 Utiliser MuseScore pour créer/scanner ta partition, puis exporter en MusicXML.

**Q : Comment savoir ce qui est installé ?**
```bash
python check_system.py
```

**Q : L'installation a échoué, que faire ?**
1. Vérifier la connexion internet
2. Essayer `./setup.sh` à nouveau
3. Installer manuellement : `pip install -r requirements.txt`

---

## Support

Si le problème persiste :

1. **Vérifier les logs**
   ```bash
   python app.py
   # Noter les erreurs
   ```

2. **Vérifier l'environnement**
   ```bash
   python check_system.py
   ```

3. **Tester les modules**
   ```bash
   source venv/bin/activate
   python -c "import flask; print('Flask OK')"
   python -c "from modules.harmonica import convert_to_tablature; print('Modules OK')"
   ```

---

**Version :** 2.0
**Dernière mise à jour :** 2 décembre 2025
