#!/usr/bin/env python
"""Test du système de progression SSE"""
import requests
import time
import json
from modules.progress_tracker import create_tracker, get_tracker

# Créer un tracker de test
session_id = "test-session-123"
tracker = create_tracker(session_id)

print(f"✓ Tracker créé avec session_id: {session_id}")

# Simuler une progression
def simulate_progress():
    """Simule le pipeline complet"""
    time.sleep(0.5)

    # Étape 1: OCR
    tracker.start_step('ocr', 'Lecture de la partition')
    time.sleep(0.3)
    tracker.start_substep('ocr', 'ocr_init', 'Initialisation Audiveris')
    time.sleep(0.2)
    tracker.complete_substep('ocr', 'ocr_init', 'Audiveris prêt')
    time.sleep(0.2)
    tracker.start_substep('ocr', 'ocr_process', 'Analyse...')
    time.sleep(0.5)
    tracker.complete_substep('ocr', 'ocr_process', 'Partition analysée')
    time.sleep(0.2)
    tracker.start_substep('ocr', 'ocr_parse', 'Parsing MusicXML')
    time.sleep(0.3)
    tracker.complete_substep('ocr', 'ocr_parse', 'MusicXML extrait')
    tracker.complete_step('ocr', '1 partie détectée')

    # Étape 2: Mélodie
    tracker.start_step('melody', 'Extraction mélodie')
    time.sleep(0.3)
    tracker.start_substep('melody', 'melody_select', 'Sélection partie')
    time.sleep(0.2)
    tracker.complete_substep('melody', 'melody_select', 'Partie sélectionnée')
    tracker.start_substep('melody', 'melody_extract', 'Extraction notes')
    time.sleep(0.5)
    tracker.complete_substep('melody', 'melody_extract', '45 notes extraites')
    tracker.complete_step('melody', '45 notes')

    # Étape 3: Analyse
    tracker.start_step('analysis', 'Analyse musicale')
    time.sleep(0.2)
    tracker.start_substep('analysis', 'analysis_key', 'Détection tonalité')
    time.sleep(0.2)
    tracker.complete_substep('analysis', 'analysis_key', 'Tonalité: C')
    tracker.start_substep('analysis', 'analysis_range', 'Calcul tessiture')
    time.sleep(0.2)
    tracker.complete_substep('analysis', 'analysis_range', 'Tessiture: C4-G5')
    tracker.complete_step('analysis', 'Tonalité: C')

    # Étape 4: Mapping
    tracker.start_step('mapping_load', 'Chargement harmonica diatonic C')
    time.sleep(0.3)
    tracker.complete_step('mapping_load', 'Harmonica diatonique Richter 10 trous en C')

    # Étape 5: Transposition
    tracker.start_step('transpose', 'Vérification jouabilité')
    time.sleep(0.2)
    tracker.start_substep('transpose', 'transpose_check', 'Analyse jouabilité')
    time.sleep(0.3)
    tracker.complete_substep('transpose', 'transpose_check', 'Jouable')
    tracker.start_substep('transpose', 'transpose_apply', 'Transposition')
    time.sleep(0.2)
    tracker.complete_substep('transpose', 'transpose_apply', 'Aucune transposition nécessaire')
    tracker.complete_step('transpose', 'Aucune transposition nécessaire')

    # Étape 6: Tablature
    tracker.start_step('tablature', 'Génération tablature')
    time.sleep(0.2)
    tracker.start_substep('tablature', 'tablature_map', 'Mapping notes → trous')
    time.sleep(0.4)
    tracker.complete_substep('tablature', 'tablature_map', '45 positions mappées')
    tracker.start_substep('tablature', 'tablature_optimize', 'Optimisation')
    time.sleep(0.3)
    tracker.complete_substep('tablature', 'tablature_optimize', 'Positions optimisées')
    tracker.complete_step('tablature', '45 positions')

    # Étape 7: PDF
    tracker.start_step('pdf', 'Génération PDF')
    time.sleep(0.2)
    tracker.start_substep('pdf', 'pdf_format', 'Formatage Lilypond')
    time.sleep(0.3)
    tracker.complete_substep('pdf', 'pdf_format', 'Fichier .ly créé')
    tracker.start_substep('pdf', 'pdf_compile', 'Compilation Lilypond')
    time.sleep(0.8)
    tracker.complete_substep('pdf', 'pdf_compile', 'PDF compilé')
    tracker.complete_step('pdf', 'test_tablature.pdf')

    print("✓ Simulation terminée")

# Lancer la simulation dans un thread
import threading
thread = threading.Thread(target=simulate_progress, daemon=True)
thread.start()

print("\n✓ Simulation lancée en background")
print(f"\nPour tester SSE, lancez Flask et accédez à:")
print(f"  http://localhost:5000/progress/{session_id}")
print(f"\nOu testez avec curl:")
print(f"  curl http://localhost:5000/progress/{session_id}")
print("\nStatut actuel:")
status = tracker.get_status()
print(json.dumps(status, indent=2))

# Attendre la fin
thread.join()
print("\n✓ Test terminé")
print(f"\nStatut final: {tracker.get_overall_progress()}%")
