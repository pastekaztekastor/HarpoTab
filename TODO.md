## FAIT ✅

- [x] **Regarde HarpoTab sur lilypond** (fait par daniel cartron) - Analysé et features récupérées
  - Système 2 lignes Draw/Blow (déjà implémenté)
  - Transposition automatique (NOUVEAU)
  - Vérification jouabilité (NOUVEAU)
  - Voir `docs/OCR_IMPROVEMENTS.md` pour détails

- [x] **Ajoute la possibilité de visualiser le PDF avant de le DL**
  - Bouton "Prévisualiser le PDF" ajouté (ouvre dans nouvel onglet)
  - Disponible en haut et en bas de la page résultat
  - Bouton téléchargement MIDI pour fichiers LilyPond

- [x] **Avant généré la partition test si elle est jouable avec l'harmo proposé**
  - Fonction `analyze_playability()` implémentée
  - Affichage du % de jouabilité sur la page résultat
  - Indication des notes manquantes
  - Badge vert si 100% jouable, jaune sinon

- [x] **Si pas possible teste en la transposant dans toutes les tonalités**
  - Fonction `find_best_tonalities()` implémentée
  - Teste automatiquement les 7 tonalités (C, G, A, D, E, F, Bb)
  - Affiche top 3 des meilleures alternatives avec barres de progression
  - Recommandation claire pour l'utilisateur

## À FAIRE 📋

- [x] **Il y a un GROS problème avec L'OCR il fait de la marde** - ✅ **RÉSOLU !**
  - ✅ Support MusicXML implémenté (import depuis MuseScore/Finale)
  - ✅ Intégration Audiveris complète (OCR RÉEL)
  - ✅ Scripts d'installation créés (`./install_audiveris.sh`, `./setup.sh`)
  - ✅ Script de vérification système (`check_system.py`)
  - ✅ Script de test OCR (`test_audiveris_ocr.py`)
  - ✅ Documentation complète (`INSTALLATION.md`)
  - ⏳ Installation utilisateur : `pip install music21` + `./install_audiveris.sh`

## AMÉLIORATIONS FUTURES 🚀

### Phase 2 - Du README (✅ TERMINÉ !)
- [x] **Support upload fichiers MusicXML** (.musicxml, .mxl)
  - Parser avec music21
  - Extraction titre, compositeur, notes, accords
  - Intégration complète workflow

- [x] **Export en formats multiples**
  - MIDI ✅ (via LilyPond)
  - LilyPond .ly ✅ (téléchargeable)
  - ABC ⏳ (future)

- [x] **Support harmonica chromatique** (12 trous)
  - Mapping complet 48 notes (C4-B7)
  - Gestion slide in/out
  - Notation avec marqueur <

- [x] **Édition manuelle de la tablature**
  - Modal d'édition avec tableau
  - Modification mesure, note, trou, action, durée
  - Suppression de notes
  - Régénération PDF instantanée

- [x] **Playback audio** (lecteur MIDI intégré)
  - Player HTML5 <audio>
  - Lecture directe MIDI
  - Astuce "boucle" pour apprentissage

- [x] **Intégration Audiveris pour OCR réel** ✅
  - OCR musical RÉEL avec Audiveris
  - Export MusicXML automatique
  - Scripts d'installation et vérification
  - Tests complets

- [ ] Annotations et métronome
- [ ] Partage de tablatures (export/import)

### Phase 3 - Long terme
- [ ] Annotations avancées (bends, ghost notes, slaps, tongue blocking)
- [ ] Export MuseScore/Guitar Pro
- [ ] Mode collaboratif (base de données tablatures)
- [ ] Application mobile (PWA)

