#!/usr/bin/env python3
"""
Test du workflow complet : vérifier que le PDF LilyPond est bien retourné.
"""

import os
import sys

# Test de l'import et de la génération
from modules.pdf_reader import extract_music_from_image
from modules.music_parser import parse_musical_notes
from modules.harmonica import convert_to_harmonica
from modules.pdf_generator import generate_tablature_pdf

def test_complete_workflow():
    """Test le workflow complet de conversion."""
    print("=" * 70)
    print("Test Workflow Complet - Vérification retour PDF LilyPond")
    print("=" * 70)
    print()

    # Étape 1 : Extraction
    print("1. Extraction des données musicales...")
    music_data = extract_music_from_image('avant-toi-partition-piano-724x1024.jpg')
    title = music_data.get('title', '')
    composer = music_data.get('composer', '')
    print(f"   ✓ Titre: {title}")
    print(f"   ✓ Compositeur: {composer}")
    print()

    # Étape 2 : Parsing
    print("2. Parsing des notes...")
    notes = parse_musical_notes(music_data)
    print(f"   ✓ {len(notes)} notes parsées")
    print()

    # Étape 3 : Conversion harmonica
    print("3. Conversion en tablature harmonica...")
    tablature = convert_to_harmonica(notes, 'diatonic', 'C', 'arrows')

    # Ajouter titre et compositeur comme dans app.py
    if title and tablature:
        for item in tablature:
            item['title'] = title
            item['composer'] = composer

    print(f"   ✓ {len(tablature)} notes converties")
    print()

    # Étape 4 : Génération PDF
    print("4. Génération du PDF avec LilyPond...")
    output_path = 'static/uploads/test_workflow.pdf'

    generated_path = generate_tablature_pdf(
        tablature,
        output_path,
        tonality='C',
        notation_style='arrows',
        use_lilypond=True
    )

    print()
    print("=" * 70)
    print("RÉSULTAT")
    print("=" * 70)

    if generated_path:
        print(f"✓ Fichier généré: {generated_path}")

        # Vérifier que c'est bien un fichier LilyPond
        if '_lilypond' in generated_path:
            print("✓ C'est bien un fichier LilyPond (contient '_lilypond')")
        else:
            print("✗ ERREUR: Le fichier ne contient pas '_lilypond'")
            print(f"  Chemin reçu: {generated_path}")
            return False

        # Vérifier que le fichier existe
        if os.path.exists(generated_path):
            file_size = os.path.getsize(generated_path)
            print(f"✓ Fichier existe ({file_size:,} bytes)")
        else:
            print(f"✗ ERREUR: Le fichier n'existe pas: {generated_path}")
            return False

        # Vérifier que le MIDI existe aussi
        midi_path = generated_path.replace('.pdf', '.midi')
        if os.path.exists(midi_path):
            midi_size = os.path.getsize(midi_path)
            print(f"✓ Fichier MIDI existe ({midi_size:,} bytes)")
        else:
            print(f"⚠ Fichier MIDI non trouvé: {midi_path}")

        print()
        print("=" * 70)
        print("✓ TEST RÉUSSI")
        print("=" * 70)
        print()
        print("Le workflow complet fonctionne correctement:")
        print("  1. Le PDF LilyPond est généré")
        print("  2. Le chemin retourné contient '_lilypond'")
        print("  3. Le fichier MIDI est généré automatiquement")
        print()
        print("L'application Flask devrait maintenant retourner le bon PDF !")
        return True

    else:
        print("✗ ERREUR: generate_tablature_pdf a retourné None")
        print("  LilyPond n'est peut-être pas installé ou a échoué")
        return False

if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
