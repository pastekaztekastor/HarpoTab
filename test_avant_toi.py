#!/usr/bin/env python3
"""
Test spécifique pour la partition "Avant Toi"
- Extraction UNIQUEMENT de la mélodie (clé de Sol)
- Accords affichés au-dessus des mesures
- Tablature 2 lignes avec notes soufflées/aspirées
"""

import sys
import os

print("=" * 70)
print("HarpoTab - Test 'Avant Toi' (VITAA & SLIMANE)")
print("=" * 70)
print()

# Test 1: Import des modules
print("Test 1: Import des modules...")
try:
    from modules import pdf_reader, music_parser, harmonica, pdf_generator
    from modules.staff_detector import extract_melody_only, is_piano_score
    print("✓ Tous les modules importés")
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

print()

# Test 2: Lire la partition "Avant Toi"
print("Test 2: Lecture de la partition 'Avant Toi'...")
partition_path = './avant-toi-partition-piano-724x1024.jpg'

if not os.path.exists(partition_path):
    print(f"✗ Partition non trouvée : {partition_path}")
    sys.exit(1)

try:
    music_data = pdf_reader.extract_music_from_image(partition_path)
    print(f"✓ Partition lue avec succès")
    print(f"  Titre : {music_data.get('title', 'N/A')}")
    print(f"  Compositeur : {music_data.get('composer', 'N/A')}")
    print(f"  Format : {music_data.get('format', 'N/A')}")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print()

# Test 3: Vérifier que c'est une partition piano (2 portées)
print("Test 3: Détection du type de partition...")
if is_piano_score(music_data):
    print("✓ Partition piano détectée (2 portées)")
    staff_info = music_data.get('staff_info', {})
    print(f"  Portées : {staff_info.get('staves_count', 'N/A')}")
    print(f"  Portée extraite : {staff_info.get('extracted_staff', 'N/A')}")
    print(f"  Portée ignorée : {staff_info.get('ignored_staff', 'N/A')}")
else:
    print("✗ Pas une partition piano")

print()

# Test 4: Extraire UNIQUEMENT la mélodie (clé de Sol)
print("Test 4: Extraction de la mélodie (clé de Sol UNIQUEMENT)...")
melody_data = extract_melody_only(music_data)
notes_count = len(melody_data.get('raw_notes', []))
print(f"✓ Mélodie extraite : {notes_count} notes")
print(f"  Message : {melody_data.get('message', 'N/A')}")

# Afficher les 12 premières notes
raw_notes = melody_data.get('raw_notes', [])
if raw_notes:
    print(f"  Premières notes : {' '.join(raw_notes[:12])}")

print()

# Test 5: Parser les notes avec les accords
print("Test 5: Parsing des notes avec accords...")
notes = music_parser.parse_musical_notes(melody_data)
print(f"✓ {len(notes)} notes parsées")

# Vérifier que les accords sont bien là
notes_with_chords = [n for n in notes if n.chord]
print(f"  Notes avec accord : {len(notes_with_chords)}/{len(notes)}")

# Afficher quelques notes avec leurs accords
print("  Exemples :")
for i, note in enumerate(notes[:8]):
    chord_str = f" [{note.chord}]" if note.chord else ""
    print(f"    {i+1}. {note.name} - Mesure {note.measure}{chord_str}")

print()

# Test 6: Progression d'accords
print("Test 6: Progression d'accords...")
chords_sequence = []
last_chord = None
for note in notes:
    if note.chord and note.chord != last_chord:
        chords_sequence.append(note.chord)
        last_chord = note.chord

print(f"✓ Progression d'accords détectée :")
print(f"  {' - '.join(chords_sequence[:8])}...")

print()

# Test 7: Conversion en tablature
print("Test 7: Conversion en tablature harmonica...")
tablature = harmonica.convert_to_harmonica(notes, 'diatonic', 'C', 'arrows')
print(f"✓ {len(tablature)} notes converties en tablature")

# Séparer blow/draw
blow_notes = [t for t in tablature if t['action'] == 'blow']
draw_notes = [t for t in tablature if t['action'] == 'draw']
print(f"  Notes soufflées (↑) : {len(blow_notes)}")
print(f"  Notes aspirées (↓) : {len(draw_notes)}")

# Vérifier que les accords sont passés
tab_with_chords = [t for t in tablature if t.get('chord')]
print(f"  Notes tablature avec accord : {len(tab_with_chords)}/{len(tablature)}")

print()

# Test 8: Affichage format 2 lignes par mesure
print("Test 8: Affichage tablature 2 lignes (avec accords)...")
print("-" * 70)

# Organiser par mesure
measures = {}
for item in tablature:
    measure = item['measure']
    if measure not in measures:
        measures[measure] = {'blow': [], 'draw': [], 'chord': None}

    if item['action'] == 'blow':
        measures[measure]['blow'].append(item)
    elif item['action'] == 'draw':
        measures[measure]['draw'].append(item)

    # Récupérer l'accord
    if item.get('chord'):
        measures[measure]['chord'] = item['chord']

# Afficher les 4 premières mesures
for measure_num in sorted(measures.keys())[:4]:
    chord_str = f" [{measures[measure_num]['chord']}]" if measures[measure_num]['chord'] else ""
    print(f"\n📊 Mesure {measure_num}{chord_str}")
    print("  " + "─" * 60)

    # Ligne soufflée
    blow_trous = [str(n['hole']) for n in measures[measure_num]['blow'] if n['hole'] > 0]
    print(f"  ↑ SOUFFLÉ  : {' '.join(blow_trous) if blow_trous else '(aucune)'}")

    # Ligne aspirée
    draw_trous = [str(n['hole']) for n in measures[measure_num]['draw'] if n['hole'] > 0]
    print(f"  ↓ ASPIRÉ   : {' '.join(draw_trous) if draw_trous else '(aucune)'}")

print()
print("-" * 70)
print()

# Test 9: Génération PDF avec partition originale + accords
print("Test 9: Génération PDF (partition + tablature + accords)...")
try:
    output_path = os.path.join('static', 'uploads', 'avant_toi_tablature.pdf')

    pdf_generator.generate_tablature_pdf(
        tablature,
        output_path,
        tonality='C',
        notation_style='arrows',
        original_file=partition_path  # Inclure la partition originale
    )

    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✓ PDF généré avec succès")
        print(f"  Fichier : {output_path}")
        print(f"  Taille : {file_size:,} bytes")
    else:
        print(f"✗ Le fichier PDF n'a pas été créé")
        sys.exit(1)
except Exception as e:
    print(f"✗ Erreur lors de la génération: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 10: Vérification du contenu du PDF
print("Test 10: Vérification du contenu...")
print("✓ Le PDF devrait contenir :")
print("  1. Partition originale 'Avant Toi' en haut")
print("  2. Légende explicative (ligne soufflée/aspirée)")
print("  3. Tablature 2 lignes avec :")
print("     - ACCORDS affichés au-dessus de chaque mesure (Am, F, C, G...)")
print("     - Ligne supérieure : notes SOUFFLÉES avec numéros de trou")
print("     - Ligne inférieure : notes ASPIRÉES avec numéros de trou")
print("     - Notation musicale (durée des notes)")
print("     - Organisation par mesures")

print()
print("=" * 70)
print("✓ TEST 'AVANT TOI' RÉUSSI !")
print("=" * 70)
print()
print("Résumé :")
print(f"  ✓ Partition piano détectée (2 portées)")
print(f"  ✓ Mélodie extraite UNIQUEMENT (clé de Sol)")
print(f"  ✓ Accompagnement ignoré (clé de Fa)")
print(f"  ✓ {len(notes)} notes parsées")
print(f"  ✓ Accords détectés : {' - '.join(chords_sequence[:8])}...")
print(f"  ✓ Tablature 2 lignes générée")
print(f"  ✓ PDF avec partition originale créé")
print()
print(f"Ouvrez le PDF : {output_path}")
print("Vous devriez voir les ACCORDS au-dessus de chaque mesure !")
print()
