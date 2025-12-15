# Système de Progression en Temps Réel

## Vue d'ensemble

Le système de progression permet de suivre en temps réel l'avancement de la conversion d'une partition en tablature.

## Architecture

```
Client (JS) ←→ SSE ←→ Flask Route ←→ ProgressTracker ←→ Pipeline
```

### Composants

1. **ProgressTracker** (`modules/progress_tracker.py`)
   - Classe de suivi centralisée
   - Gère 7 étapes principales + sous-étapes
   - Thread-safe avec lock
   - Stockage en mémoire (session_id → tracker)

2. **Route SSE** (`/progress/<session_id>`)
   - Server-Sent Events pour push en temps réel
   - Polling toutes les 0.5s
   - Envoie uniquement les changements

3. **Client JavaScript** (`static/js/progress.js`)
   - Classe `ProgressTracker`
   - Connexion EventSource
   - Mise à jour DOM en temps réel
   - Gestion erreurs

4. **Page HTML** (`templates/progress.html`)
   - Barre de progression globale
   - Liste des étapes avec sous-étapes
   - Animations et icônes Bootstrap
   - Redirection automatique à 100%

## Utilisation

### Backend

```python
from modules.progress_tracker import create_tracker, get_tracker

# Créer un tracker
session_id = str(uuid.uuid4())
tracker = create_tracker(session_id)

# Démarrer une étape
tracker.start_step('ocr', "Lecture de la partition")

# Démarrer une sous-étape
tracker.start_substep('ocr', 'ocr_init', "Initialisation Audiveris")

# Compléter une sous-étape
tracker.complete_substep('ocr', 'ocr_init', "Audiveris prêt")

# Compléter une étape
tracker.complete_step('ocr', "OCR terminé")

# En cas d'erreur
tracker.error_step('ocr', "Échec OCR: fichier corrompu")
```

### Frontend

```javascript
// Démarrer le suivi
const tracker = new ProgressTracker(sessionId, 'progress-container');
tracker.start();
```

## Étapes du Pipeline

| ID | Nom | Sous-étapes |
|----|-----|-------------|
| `ocr` | OCR Musical | `ocr_init`, `ocr_process`, `ocr_parse` |
| `melody` | Extraction Mélodie | `melody_select`, `melody_extract` |
| `analysis` | Analyse Musicale | `analysis_key`, `analysis_range` |
| `mapping_load` | Chargement Mapping | - |
| `transpose` | Transposition | `transpose_check`, `transpose_apply` |
| `tablature` | Génération Tablature | `tablature_map`, `tablature_optimize` |
| `pdf` | Génération PDF | `pdf_format`, `pdf_compile` |

## Structure des Données

### Status JSON

```json
{
  "session_id": "uuid",
  "overall_progress": 45,
  "elapsed_time": 23,
  "current_step": "transpose",
  "steps": [
    {
      "id": "ocr",
      "name": "OCR Musical",
      "status": "completed",
      "progress": 100,
      "message": "47 notes extraites",
      "substeps": [
        {
          "id": "ocr_init",
          "name": "Initialisation Audiveris",
          "status": "completed",
          "progress": 100,
          "message": ""
        }
      ]
    }
  ]
}
```

### États possibles

- `pending` : En attente
- `in_progress` : En cours
- `completed` : Terminé ✓
- `error` : Erreur ✗

## TODO : Intégration au Pipeline

Pour intégrer complètement le tracker au pipeline, il faut :

1. Modifier `app.py` route `/convert` :
   ```python
   session_id = str(uuid.uuid4())
   tracker = create_tracker(session_id)

   # Lancer conversion en thread
   thread = threading.Thread(
       target=process_conversion,
       args=(upload_path, harmonica_type, harmonica_key, Config.OUTPUT_FOLDER, tracker)
   )
   thread.start()

   # Rediriger vers la page de progression
   return redirect(url_for('progress', session_id=session_id))
   ```

2. Ajouter des appels au tracker dans `process_conversion()` :
   ```python
   # Étape 1
   tracker.start_step('ocr')
   tracker.start_substep('ocr', 'ocr_init')
   # ... code OCR ...
   tracker.complete_substep('ocr', 'ocr_init')
   tracker.start_substep('ocr', 'ocr_process')
   # ... etc
   ```

3. Nettoyer les trackers après usage :
   ```python
   # À la fin de process_conversion
   finally:
       # Garder le tracker 5 minutes pour que le client puisse le lire
       threading.Timer(300, lambda: remove_tracker(session_id)).start()
   ```

## Avantages

- ✅ Feedback en temps réel pour l'utilisateur
- ✅ Visibilité sur chaque étape et sous-étape
- ✅ Temps écoulé
- ✅ Gestion d'erreurs
- ✅ Expérience utilisateur améliorée
- ✅ Pas de blocage du navigateur

## Limitations actuelles

- ⚠️ Stockage en mémoire (perdu au redémarrage)
- ⚠️ Pas de persistance
- ⚠️ Intégration partielle au pipeline
- ⚠️ 1 seule conversion à la fois par session

## Améliorations futures

- Utiliser Redis pour le stockage distribué
- Websockets au lieu de SSE
- File d'attente de conversions (Celery)
- Historique des conversions
- Annulation en cours de route
