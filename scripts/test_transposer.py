#!/usr/bin/env python3
"""
Script de test pour le module transposer

Ce script teste la transposition automatique d'une partition pour harmonica
"""
import sys
import json
from pathlib import Path
from modules.ocr_reader import AudiverisOCR
from modules.melody_extractor import MelodyExtractor
from modules.transposer import Transposer, transpose_for_harmonica


def load_harmonica_map(harmonica_key: str = 'C') -> dict:
    """
    Charge le mapping d'harmonica depuis un fichier JSON

    Args:
        harmonica_key: Tonalité de l'harmonica (C, G, etc.)

    Returns:
        Mapping de l'harmonica
    """
    map_file = Path(f"data/harmonica_maps/diatonic_{harmonica_key}.json")

    if not map_file.exists():
        print(f"❌ Erreur: Fichier de mapping non trouvé: {map_file}")
        sys.exit(1)

    with open(map_file, 'r') as f:
        return json.load(f)


def test_transposition(mxl_path: str, harmonica_key: str = 'C', force_transpose: int = None):
    """
    Test complet: OCR + extraction + transposition

    Args:
        mxl_path: Chemin vers le fichier MXL
        harmonica_key: Tonalité de l'harmonica
        force_transpose: Si spécifié, force cette transposition (en demi-tons)
    """
    print(f"\n{'='*70}")
    print(f"TEST DE TRANSPOSITION POUR HARMONICA")
    print('='*70)
    print(f"Fichier: {mxl_path}")
    print(f"Harmonica: Diatonique en {harmonica_key}")
    if force_transpose is not None:
        print(f"Transposition forcée: {force_transpose} demi-tons")
    print('='*70)

    mxl_file = Path(mxl_path)

    if not mxl_file.exists():
        print(f"\n❌ Erreur: Le fichier {mxl_path} n'existe pas")
        return False

    # Étape 1: Parser le MusicXML
    print("\n[1/4] Parsing du fichier MusicXML...")
    ocr = AudiverisOCR()
    musicxml_data = ocr.parse_musicxml(mxl_file)

    if musicxml_data is None:
        print("❌ Erreur lors du parsing MusicXML")
        return False

    print(f"✅ MusicXML parsé: {len(musicxml_data['parts'])} partie(s)")

    # Étape 2: Extraire la mélodie
    print("\n[2/4] Extraction de la mélodie principale...")
    extractor = MelodyExtractor(keep_rests=False, simplify_chords=True)
    melody_data = extractor.extract_melody(musicxml_data)

    if melody_data is None:
        print("❌ Erreur lors de l'extraction de mélodie")
        return False

    notes_only = [n for n in melody_data['notes'] if n['type'] == 'note']
    print(f"✅ Mélodie extraite: {len(notes_only)} notes")

    # Tessiture originale
    if notes_only:
        lowest = min(notes_only, key=lambda n: n['midi'])
        highest = max(notes_only, key=lambda n: n['midi'])
        print(f"   Tessiture originale: {extractor.get_note_name(lowest)} à {extractor.get_note_name(highest)}")

    # Étape 3: Charger le mapping d'harmonica
    print(f"\n[3/4] Chargement du mapping harmonica {harmonica_key}...")
    harmonica_map = load_harmonica_map(harmonica_key)
    print(f"✅ Mapping chargé: {len(harmonica_map['notes'])} trous")

    # Afficher les notes jouables
    playable_notes = set()
    for hole_data in harmonica_map['notes'].values():
        for action, note_info in hole_data.items():
            if isinstance(note_info, dict) and 'note' in note_info:
                note_name = f"{note_info['note']}{note_info['octave']}"
                playable_notes.add(note_name)

    print(f"   Notes jouables: {len(playable_notes)} notes différentes")
    print(f"   Exemple: {', '.join(sorted(list(playable_notes))[:8])}, ...")

    # Étape 4: Transposer
    print(f"\n[4/4] Transposition automatique...")
    try:
        transposed_melody, semitones, playability = transpose_for_harmonica(
            melody_data,
            harmonica_map,
            force_transpose=force_transpose
        )

        print(f"✅ Transposition réussie!")

    except ValueError as e:
        print(f"❌ Erreur: {e}")
        return False

    # Afficher les résultats
    print("\n" + "="*70)
    print("RÉSULTATS DE LA TRANSPOSITION")
    print("="*70)

    transposer = Transposer()

    print(f"\nTRANSPOSITION:")
    print(f"  Demi-tons: {semitones:+d}")
    print(f"  Description: {transposer.get_transposition_info(semitones)}")

    if semitones != 0:
        # Calculer tonalité d'origine (estimation)
        print(f"  Direction: {'↑ Plus aigu' if semitones > 0 else '↓ Plus grave'}")

    print(f"\nJOUABILITÉ:")
    print(f"  Jouable: {'✅ Oui' if playability['playable'] else '⚠️ Partiellement'}")
    print(f"  Couverture: {playability['coverage']*100:.1f}%")
    print(f"  Notes jouables: {playability['playable_notes']}/{playability['total_notes']}")

    if playability['missing_notes']:
        print(f"  Notes manquantes: {', '.join(playability['missing_notes'])}")

    # Tessiture transposée
    transposed_notes = [n for n in transposed_melody['notes'] if n['type'] == 'note']
    if transposed_notes:
        lowest = min(transposed_notes, key=lambda n: n['midi'])
        highest = max(transposed_notes, key=lambda n: n['midi'])
        print(f"\nTESSITURE TRANSPOSÉE:")
        print(f"  Note la plus basse: {extractor.get_note_name(lowest)} (MIDI {lowest['midi']})")
        print(f"  Note la plus haute: {extractor.get_note_name(highest)} (MIDI {highest['midi']})")
        print(f"  Étendue: {highest['midi'] - lowest['midi']} demi-tons")

    # Afficher quelques notes transposées
    print("\n" + "="*70)
    print("APERÇU DES NOTES TRANSPOSÉES (10 premières)")
    print("="*70)

    display_count = min(10, len(transposed_notes))
    for i, note in enumerate(transposed_notes[:display_count]):
        original_note = notes_only[i]
        original_name = extractor.get_note_name(original_note)
        transposed_name = extractor.get_note_name(note)

        if semitones != 0:
            print(f"  {i+1:2d}. {original_name:6s} -> {transposed_name:6s} "
                  f"(MIDI {note['midi']}) [{note.get('note_type', '?')}]")
        else:
            print(f"  {i+1:2d}. {transposed_name:6s} (MIDI {note['midi']}) [{note.get('note_type', '?')}]")

    if len(transposed_notes) > display_count:
        print(f"\n  ... et {len(transposed_notes) - display_count} autres notes")

    print("\n" + "="*70)
    print("✅ Test réussi!")
    print("="*70 + "\n")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_transposer.py <fichier.mxl> [harmonica_key] [force_transpose]")
        print("\nArguments:")
        print("  fichier.mxl       Fichier MusicXML à transposer")
        print("  harmonica_key     Tonalité de l'harmonica (C, G, etc.) [défaut: C]")
        print("  force_transpose   Forcer une transposition en demi-tons (optionnel)")
        print("\nExemples:")
        print("  python test_transposer.py temp/ocr_output/OCRtest3.mxl")
        print("  python test_transposer.py temp/ocr_output/OCRtest3.mxl G")
        print("  python test_transposer.py temp/ocr_output/OCRtest3.mxl C 2")
        sys.exit(1)

    mxl_path = sys.argv[1]
    harmonica_key = sys.argv[2] if len(sys.argv) > 2 else 'C'
    force_transpose = int(sys.argv[3]) if len(sys.argv) > 3 else None

    success = test_transposition(mxl_path, harmonica_key, force_transpose)
    sys.exit(0 if success else 1)
