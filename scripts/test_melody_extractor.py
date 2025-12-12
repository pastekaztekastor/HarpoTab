#!/usr/bin/env python3
"""
Script de test pour le module melody_extractor

Ce script teste l'extraction de mélodie depuis des fichiers MusicXML
"""
import sys
from pathlib import Path
from modules.ocr_reader import AudiverisOCR
from modules.melody_extractor import MelodyExtractor

def test_melody_extraction(mxl_path: str, keep_rests: bool = True):
    """
    Test complet: OCR + extraction de mélodie

    Args:
        mxl_path: Chemin vers le fichier MXL
        keep_rests: Garder les silences dans la mélodie
    """
    print(f"\n{'='*70}")
    print(f"TEST D'EXTRACTION DE MÉLODIE")
    print('='*70)
    print(f"Fichier: {mxl_path}")
    print(f"Options: keep_rests={keep_rests}, simplify_chords=True")
    print('='*70)

    mxl_file = Path(mxl_path)

    if not mxl_file.exists():
        print(f"\n❌ Erreur: Le fichier {mxl_path} n'existe pas")
        return False

    # Étape 1: Parser le MusicXML
    print("\n[1/2] Parsing du fichier MusicXML...")
    ocr = AudiverisOCR()
    musicxml_data = ocr.parse_musicxml(mxl_file)

    if musicxml_data is None:
        print("❌ Erreur lors du parsing MusicXML")
        return False

    print(f"✅ MusicXML parsé: {len(musicxml_data['parts'])} partie(s)")

    # Étape 2: Extraire la mélodie
    print("\n[2/2] Extraction de la mélodie principale...")
    extractor = MelodyExtractor(keep_rests=keep_rests, simplify_chords=True)
    melody_data = extractor.extract_melody(musicxml_data)

    if melody_data is None:
        print("❌ Erreur lors de l'extraction de mélodie")
        return False

    print(f"✅ Mélodie extraite: {len(melody_data['notes'])} événements")

    # Afficher les résultats
    print("\n" + "="*70)
    print("RÉSULTATS")
    print("="*70)

    # Métadonnées
    print("\nMÉTADONNÉES:")
    metadata = melody_data['metadata']
    print(f"  Compositeur: {metadata.get('composer', 'N/A')}")
    print(f"  Titre: {metadata.get('title', 'N/A')}")
    print(f"  Tonalité: {metadata.get('key', 'N/A')}")
    print(f"  Signature rythmique: {metadata.get('time_signature', 'N/A')}")
    print(f"  Tempo: {metadata.get('tempo', 'N/A')}")

    # Statistiques
    print(f"\nSTATISTIQUES:")
    print(f"  Partie sélectionnée: {melody_data['part_id']}")
    print(f"  Nombre de mesures: {melody_data['total_measures']}")
    print(f"  Nombre total d'événements: {len(melody_data['notes'])}")

    notes_only = [n for n in melody_data['notes'] if n['type'] == 'note']
    rests_only = [n for n in melody_data['notes'] if n['type'] == 'rest']
    print(f"  - Notes: {len(notes_only)}")
    print(f"  - Silences: {len(rests_only)}")

    # Tessiture (notes les plus basses/hautes)
    if notes_only:
        midi_values = [n['midi'] for n in notes_only]
        lowest_note = min(notes_only, key=lambda n: n['midi'])
        highest_note = max(notes_only, key=lambda n: n['midi'])

        print(f"\n  Tessiture:")
        print(f"    Note la plus basse: {extractor.get_note_name(lowest_note)} (MIDI {lowest_note['midi']})")
        print(f"    Note la plus haute: {extractor.get_note_name(highest_note)} (MIDI {highest_note['midi']})")
        print(f"    Étendue: {highest_note['midi'] - lowest_note['midi']} demi-tons")

    # Afficher les premières notes
    print("\n" + "="*70)
    print("APERÇU DES PREMIÈRES NOTES")
    print("="*70)

    display_count = min(30, len(melody_data['notes']))
    current_measure = None

    for i, note in enumerate(melody_data['notes'][:display_count]):
        # Afficher le numéro de mesure si changement
        if note['measure'] != current_measure:
            current_measure = note['measure']
            print(f"\n[Mesure {current_measure}]")

        # Afficher la note
        if note['type'] == 'rest':
            print(f"  {i+1:3d}. Silence ({note.get('note_type', '?')})")
        else:
            note_name = extractor.get_note_name(note)
            print(f"  {i+1:3d}. {note_name:6s} ({note.get('note_type', '?'):8s}) MIDI: {note['midi']}")

    if len(melody_data['notes']) > display_count:
        print(f"\n  ... et {len(melody_data['notes']) - display_count} autres événements")

    # Résumé par mesure
    print("\n" + "="*70)
    print("RÉSUMÉ PAR MESURE (10 premières)")
    print("="*70)

    measures_summary = {}
    for note in melody_data['notes']:
        measure_num = note['measure']
        if measure_num not in measures_summary:
            measures_summary[measure_num] = {'notes': 0, 'rests': 0}

        if note['type'] == 'note':
            measures_summary[measure_num]['notes'] += 1
        else:
            measures_summary[measure_num]['rests'] += 1

    for measure_num in sorted(measures_summary.keys())[:10]:
        stats = measures_summary[measure_num]
        print(f"  Mesure {measure_num:2d}: {stats['notes']:2d} notes, {stats['rests']:2d} silences")

    if len(measures_summary) > 10:
        print(f"  ... et {len(measures_summary) - 10} autres mesures")

    print("\n" + "="*70)
    print("✅ Test réussi!")
    print("="*70 + "\n")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_melody_extractor.py <fichier.mxl> [--no-rests]")
        print("\nOptions:")
        print("  --no-rests    Ne pas garder les silences dans la mélodie")
        sys.exit(1)

    mxl_path = sys.argv[1]
    keep_rests = '--no-rests' not in sys.argv

    success = test_melody_extraction(mxl_path, keep_rests=keep_rests)
    sys.exit(0 if success else 1)
