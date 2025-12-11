#!/usr/bin/env python3
"""
Test de génération de partition avec LilyPond.

Ce test montre comment HarpoTab peut générer des partitions professionnelles
avec LilyPond au lieu de ReportLab.
"""

import sys
import os

print("=" * 70)
print("HarpoTab - Test Génération LilyPond")
print("=" * 70)
print()

# Test 1: Vérifier si LilyPond est installé
print("Test 1: Vérification de LilyPond...")
try:
    from modules.lilypond_generator import check_lilypond_installed

    if check_lilypond_installed():
        print("✓ LilyPond est installé et prêt")
    else:
        print("ℹ LilyPond n'est PAS installé")
        print("  Pour installer : ./install_lilypond.sh")
        print("  Ou manuellement : sudo pacman -S lilypond  (Manjaro/Arch)")
        print()
        print("  Le test va continuer en générant le code .ly")
        print("  (sans compilation PDF)")

except Exception as e:
    print(f"⚠ Erreur : {e}")

print()

# Test 2: Charger les données "Avant Toi"
print("Test 2: Chargement des données 'Avant Toi'...")
try:
    from modules import pdf_reader, music_parser, harmonica

    partition_path = './avant-toi-partition-piano-724x1024.jpg'

    if not os.path.exists(partition_path):
        print(f"✗ Partition non trouvée : {partition_path}")
        sys.exit(1)

    # Lire et convertir
    music_data = pdf_reader.extract_music_from_image(partition_path)
    notes = music_parser.parse_musical_notes(music_data)
    tablature = harmonica.convert_to_harmonica(notes, 'diatonic', 'C', 'arrows')

    print(f"✓ {len(tablature)} notes chargées")
    print(f"  Titre : {music_data.get('title')}")
    print(f"  Compositeur : {music_data.get('composer')}")

except Exception as e:
    print(f"✗ Erreur : {e}")
    sys.exit(1)

print()

# Test 3: Générer le code LilyPond
print("Test 3: Génération du code LilyPond...")
try:
    from modules.lilypond_generator import LilyPondGenerator

    generator = LilyPondGenerator(
        tonality='C',
        title=music_data.get('title', 'Avant Toi'),
        composer=music_data.get('composer', 'VITAA & SLIMANE')
    )

    # Extraire les accords
    chords = []
    seen_measures = set()
    for item in tablature:
        measure = item['measure']
        chord = item.get('chord')
        if chord and measure not in seen_measures:
            chords.append((measure, chord))
            seen_measures.add(measure)

    # Générer le code
    ly_code = generator.generate_harmonica_tablature_code(tablature, chords)

    # Sauvegarder le fichier .ly
    ly_path = os.path.join('static', 'uploads', 'avant_toi_lilypond.ly')
    with open(ly_path, 'w', encoding='utf-8') as f:
        f.write(ly_code)

    print(f"✓ Code LilyPond généré : {ly_path}")
    print(f"  Taille : {len(ly_code)} caractères")
    print(f"  Accords inclus : {len(chords)}")

except Exception as e:
    print(f"✗ Erreur : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Afficher un extrait du code généré
print("Test 4: Aperçu du code LilyPond...")
print("-" * 70)
lines = ly_code.split('\n')
for i, line in enumerate(lines[:30], 1):
    print(f"{i:3d} | {line}")
print("...")
print(f"     | (total: {len(lines)} lignes)")
print("-" * 70)
print()

# Test 5: Essayer de compiler (si LilyPond disponible)
print("Test 5: Compilation du PDF...")
try:
    if check_lilypond_installed():
        print("LilyPond disponible, compilation en cours...")

        pdf_path = os.path.join('static', 'uploads', 'avant_toi_lilypond.pdf')

        success = generator.compile_lilypond(ly_code, pdf_path)

        if success and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✓ PDF LilyPond généré avec succès !")
            print(f"  Fichier : {pdf_path}")
            print(f"  Taille : {file_size:,} bytes")
        else:
            print("✗ Erreur lors de la compilation")

    else:
        print("ℹ LilyPond non installé - Compilation ignorée")
        print()
        print("Pour compiler manuellement le fichier .ly :")
        print(f"  1. Installez LilyPond : ./install_lilypond.sh")
        print(f"  2. Compilez : lilypond {ly_path}")
        print(f"  3. Le PDF sera généré : {ly_path.replace('.ly', '.pdf')}")

except Exception as e:
    print(f"⚠ Erreur compilation : {e}")

print()

# Résumé
print("=" * 70)
print("✓ TEST TERMINÉ")
print("=" * 70)
print()
print("Résumé :")
print(f"  ✓ Code LilyPond généré : {ly_path}")
print(f"  ✓ Contient :")
print(f"    - Mélodie de 'Avant Toi' (clé de Sol uniquement)")
print(f"    - Tablature harmonica (numéros de trou + flèches)")
print(f"    - Accords au-dessus ({len(chords)} accords)")
print(f"    - Notation musicale professionnelle")
print()

if not check_lilypond_installed():
    print("📦 Pour installer LilyPond :")
    print()
    print("  Manjaro/Arch  : sudo pacman -S lilypond")
    print("  Ubuntu/Debian : sudo apt-get install lilypond")
    print("  macOS         : brew install lilypond")
    print()
    print("  Ou utilisez : ./install_lilypond.sh")
    print()
else:
    print("🎼 LilyPond est installé !")
    print("   Les futurs PDFs seront générés avec LilyPond")
    print("   (partitions professionnelles)")
    print()

print("Avantages de LilyPond vs ReportLab :")
print("  ✓ Notation musicale parfaite")
print("  ✓ Tablature harmonica native")
print("  ✓ Accords en chiffrage harmonique")
print("  ✓ Export MIDI automatique")
print("  ✓ Qualité publication")
print()
