# Démarrage Rapide - HarpoTab

## Installation en 3 étapes

### 1. Créer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python app.py
```

Ou utilisez le script de lancement :
```bash
./run.sh
```

## Accès à l'application

Ouvrez votre navigateur à l'adresse :
```
http://localhost:5000
```

## Utilisation

1. **Upload** : Cliquez sur "Choisir un fichier" et sélectionnez une partition (PDF ou image)

2. **Configuration** :
   - Type d'harmonica : Diatonique 10 trous
   - Tonalité : Choisissez parmi C, G, A, D, E, F, Bb
   - Style : Flèches (4↑ 5↓), Lettres (4B 5D), ou Symboles (+4 -5)

3. **Conversion** : Cliquez sur "Lancer la conversion"

4. **Téléchargement** : Récupérez votre tablature en PDF

## Format de Tablature Pédagogique

HarpoTab génère une **tablature à 2 lignes** idéale pour l'apprentissage :

- **Ligne supérieure** = Notes SOUFFLÉES (↑)
- **Ligne inférieure** = Notes ASPIRÉES (↓)
- **Numéros de trou** affichés directement sur les notes
- **Durée des notes** visible (ronde, blanche, noire, croche)
- **Partition originale** incluse au-dessus dans le PDF

### Exemple de lecture

```
  ↑ SOUFFLÉ    1   2   4
  ↓ ASPIRÉ        1   2   4
```

Signifie : Souffler trou 1, Aspirer trou 1, Souffler trou 2, Aspirer trou 2, etc.

## Note importante (MVP)

Cette version utilise des **données de démonstration** :
- Fichiers PDF → Génèrent la gamme de Do majeur
- Fichiers images → Génèrent l'Hymne à la joie

Pour tester la conversion :
1. Uploadez n'importe quel PDF ou image
2. La conversion générera une tablature de démonstration en format 2 lignes
3. Vous verrez comment fonctionne le système de conversion
4. Le PDF contiendra la partition originale + la tablature en dessous

## Test rapide

Pour vérifier que tout fonctionne :
```bash
source venv/bin/activate
python test_modules.py
```

Vous devriez voir :
```
✓ TOUS LES TESTS RÉUSSIS!
```

## Prochaines étapes

Pour implémenter la reconnaissance réelle de partitions, vous pouvez :
- Intégrer Audiveris (OCR musical)
- Utiliser des fichiers MusicXML
- Développer un modèle ML personnalisé

Consultez le README.md pour plus de détails.

## Besoin d'aide ?

- Consultez le README.md complet
- Vérifiez que Python 3.8+ est installé
- Assurez-vous d'avoir activé l'environnement virtuel
