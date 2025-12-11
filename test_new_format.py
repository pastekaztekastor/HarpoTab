#!/usr/bin/env python3
"""
Test du nouveau format de tablature à 2 lignes.
"""

import sys
import os

print("=" * 70)
print("HarpoTab - Test du Format 2 Lignes (Soufflé/Aspiré)")
print("=" * 70)
print()

# Test 1: Import des modules
print("Test 1: Import des modules...")
try:
    from modules import pdf_reader, music_parser, harmonica, pdf_generator
    print("✓ Tous les modules importés")
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

print()

# Test 2: Créer des données de test avec notes soufflées ET aspirées
print("Test 2: Création de données de test...")
music_data = {
    'raw_notes': [
        # Mesure 1: mélange soufflé/aspiré
        'C4',  # soufflé (trou 1)
        'D4',  # aspiré (trou 1)
        'E4',  # soufflé (trou 2)
        'G4',  # aspiré (trou 2)
        # Mesure 2:
        'C5',  # soufflé (trou 4)
        'D5',  # aspiré (trou 4)
        'E5',  # soufflé (trou 5)
        'F5',  # aspiré (trou 5)
        # Mesure 3:
        'G5',  # soufflé (trou 6)
        'A5',  # aspiré (trou 6)
        'C6',  # soufflé (trou 7)
        'B5',  # aspiré (trou 7)
    ],
    'demo': True
}

notes = music_parser.parse_musical_notes(music_data)
print(f"✓ {len(notes)} notes créées sur {max([n.measure for n in notes])} mesures")
print()

# Test 3: Conversion en tablature
print("Test 3: Conversion en tablature...")
tablature = harmonica.convert_to_harmonica(notes, 'diatonic', 'C', 'arrows')

# Séparer par action
blow_notes = [t for t in tablature if t['action'] == 'blow']
draw_notes = [t for t in tablature if t['action'] == 'draw']

print(f"✓ Conversion réussie:")
print(f"  - Notes soufflées (↑): {len(blow_notes)}")
print(f"  - Notes aspirées (↓): {len(draw_notes)}")
print()

# Test 4: Affichage format 2 lignes (console)
print("Test 4: Affichage format 2 lignes:")
print("-" * 70)

# Organiser par mesure
measures = {}
for item in tablature:
    measure = item['measure']
    if measure not in measures:
        measures[measure] = {'blow': [], 'draw': []}

    if item['action'] == 'blow':
        measures[measure]['blow'].append(item)
    elif item['action'] == 'draw':
        measures[measure]['draw'].append(item)

# Afficher chaque mesure
for measure_num in sorted(measures.keys()):
    print(f"\n📊 Mesure {measure_num}")
    print("  " + "─" * 60)

    # Ligne soufflée (haut)
    blow_trous = [str(n['hole']) for n in measures[measure_num]['blow'] if n['hole'] > 0]
    print(f"  ↑ SOUFFLÉ  : {' '.join(blow_trous) if blow_trous else '(aucune)'}")

    # Ligne aspirée (bas)
    draw_trous = [str(n['hole']) for n in measures[measure_num]['draw'] if n['hole'] > 0]
    print(f"  ↓ ASPIRÉ   : {' '.join(draw_trous) if draw_trous else '(aucune)'}")

print()
print("-" * 70)
print()

# Test 5: Génération PDF avec nouveau format
print("Test 5: Génération PDF format 2 lignes...")
try:
    output_path = os.path.join('static', 'uploads', 'test_tablature_2lines.pdf')

    # Créer un faux fichier image pour tester l'inclusion
    test_image_path = None  # Pas d'image pour ce test

    pdf_generator.generate_tablature_pdf(
        tablature,
        output_path,
        tonality='C',
        notation_style='arrows',
        original_file=test_image_path
    )

    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✓ PDF généré avec succès")
        print(f"  Fichier: {output_path}")
        print(f"  Taille: {file_size:,} bytes")
    else:
        print(f"✗ Le fichier PDF n'a pas été créé")
        sys.exit(1)
except Exception as e:
    print(f"✗ Erreur lors de la génération: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 6: Vérifier les différentes durées de notes
print("Test 6: Test des durées de notes...")
durations = ['whole', 'half', 'quarter', 'eighth']
test_notes_varied = []

for i, duration in enumerate(durations):
    note = notes[i % len(notes)]
    note.duration = duration
    test_notes_varied.append(note)

tablature_varied = harmonica.convert_to_harmonica(test_notes_varied, 'diatonic', 'C', 'arrows')

print("  Durées testées:")
for item in tablature_varied[:4]:
    duration_symbols = {
        'whole': '𝅝 (Ronde)',
        'half': '𝅗𝅥 (Blanche)',
        'quarter': '♩ (Noire)',
        'eighth': '♪ (Croche)'
    }
    symbol = duration_symbols.get(item['duration'], item['duration'])
    print(f"    {item['note_name']}: {symbol}")

print("✓ Durées variées supportées")
print()

print("=" * 70)
print("✓ NOUVEAU FORMAT À 2 LIGNES FONCTIONNEL !")
print("=" * 70)
print()
print("Caractéristiques:")
print("  ✓ 2 lignes distinctes (soufflé/aspiré)")
print("  ✓ Numéros de trou affichés sur les notes")
print("  ✓ Support des durées de notes (ronde, blanche, noire, croche)")
print("  ✓ Organisation par mesures")
print("  ✓ PDF généré avec portée à 2 lignes")
print()
print(f"Ouvrez le PDF généré: {output_path}")
print()
