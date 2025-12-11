#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les modules HarpoTab fonctionnent.
"""

import sys
import os

print("=" * 60)
print("HarpoTab - Test des Modules")
print("=" * 60)
print()

# Test 1: Import des modules
print("Test 1: Import des modules...")
try:
    from modules import pdf_reader, music_parser, harmonica, pdf_generator
    print("✓ Tous les modules importés avec succès")
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

print()

# Test 2: Chargement du mapping harmonica
print("Test 2: Chargement du mapping harmonica...")
try:
    converter = harmonica.HarmonicaConverter('diatonic', 'C')
    print(f"✓ Mapping chargé pour harmonica diatonique en C")
    print(f"  Notes disponibles: {len(converter.get_available_notes())}")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 3: Parsing de notes
print("Test 3: Parsing de notes musicales...")
try:
    music_data = {
        'raw_notes': ['C4', 'D4', 'E4', 'F4', 'G4'],
        'demo': True
    }
    notes = music_parser.parse_musical_notes(music_data)
    print(f"✓ Parsing réussi: {len(notes)} notes parsées")
    print(f"  Exemple: {notes[0].name} (mesure {notes[0].measure})")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 4: Conversion en tablature
print("Test 4: Conversion en tablature...")
try:
    tablature = harmonica.convert_to_harmonica(notes, 'diatonic', 'C', 'arrows')
    print(f"✓ Conversion réussie: {len(tablature)} notes converties")
    print(f"  Exemple: {tablature[0]['note_name']} → {tablature[0]['tab_notation']}")

    # Afficher toute la tablature
    print(f"  Tablature complète: {' '.join([t['tab_notation'] for t in tablature])}")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 5: Génération PDF
print("Test 5: Génération de PDF...")
try:
    output_path = os.path.join('static', 'uploads', 'test_tablature.pdf')
    pdf_generator.generate_tablature_pdf(tablature, output_path, 'C', 'arrows')

    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✓ PDF généré avec succès")
        print(f"  Fichier: {output_path}")
        print(f"  Taille: {file_size} bytes")
    else:
        print(f"✗ Le fichier PDF n'a pas été créé")
        sys.exit(1)
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 6: Analyse de jouabilité
print("Test 6: Analyse de jouabilité...")
try:
    analysis = harmonica.analyze_playability(notes, 'diatonic', 'C')
    print(f"✓ Analyse complétée")
    print(f"  Notes jouables: {analysis['playable_notes']}/{analysis['total_notes']}")
    print(f"  Pourcentage: {analysis['playability_percentage']:.1f}%")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 7: Différents styles de notation
print("Test 7: Test des styles de notation...")
try:
    styles = ['arrows', 'letters', 'symbols']
    for style in styles:
        tab = harmonica.convert_to_harmonica(notes[:3], 'diatonic', 'C', style)
        result = ' '.join([t['tab_notation'] for t in tab])
        print(f"  {style:8s}: {result}")
    print("✓ Tous les styles fonctionnent")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 8: Différentes tonalités
print("Test 8: Test des tonalités...")
try:
    tonalities = ['C', 'G', 'A', 'D']
    for tonality in tonalities:
        conv = harmonica.HarmonicaConverter('diatonic', tonality)
        notes_count = len(conv.get_available_notes())
        print(f"  {tonality}: {notes_count} notes disponibles")
    print("✓ Toutes les tonalités fonctionnent")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✓ TOUS LES TESTS RÉUSSIS!")
print("=" * 60)
print()
print("L'application est prête à être utilisée.")
print("Lancez: python app.py")
print("Ou utilisez: ./run.sh")
print()
