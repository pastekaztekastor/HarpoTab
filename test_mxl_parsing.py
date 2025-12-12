#!/usr/bin/env python3
"""
Script de test rapide pour parser un fichier MXL existant
"""
import sys
from pathlib import Path
from modules.ocr_reader import AudiverisOCR

def test_mxl_file(mxl_path: str):
    """Test le parsing d'un fichier MXL"""
    print(f"\n{'='*60}")
    print(f"Test de parsing MXL: {mxl_path}")
    print('='*60)

    mxl_file = Path(mxl_path)

    if not mxl_file.exists():
        print(f"\n❌ Erreur: Le fichier {mxl_path} n'existe pas")
        return False

    # Créer l'instance OCR et parser directement le MXL
    ocr = AudiverisOCR()
    result = ocr.parse_musicxml(mxl_file)

    if result is None:
        print("\n❌ Erreur: Le parsing a échoué")
        return False

    print("\n✅ Parsing réussi!")

    # Afficher les métadonnées
    print("\n" + "="*60)
    print("MÉTADONNÉES")
    print("="*60)
    metadata = result['metadata']
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    # Afficher les parties
    print("\n" + "="*60)
    print("PARTIES MUSICALES")
    print("="*60)
    parts = result['parts']
    print(f"Nombre de parties: {len(parts)}\n")

    for i, part in enumerate(parts, 1):
        print(f"Partie {i} (ID: {part['id']}):")
        print(f"  Nombre de mesures: {len(part['measures'])}")

        # Afficher les 3 premières mesures
        for measure in part['measures'][:3]:
            print(f"\n  Mesure {measure['number']}:")
            print(f"    Notes: {len(measure['notes'])}")

            # Afficher les 5 premières notes
            for note in measure['notes'][:5]:
                if note['type'] == 'rest':
                    print(f"      - Silence ({note.get('note_type', 'N/A')})")
                else:
                    pitch = note.get('pitch', {})
                    step = pitch.get('step', '?')
                    octave = pitch.get('octave', '?')
                    alter = pitch.get('alter', 0)
                    alter_str = {-1: '♭', 0: '', 1: '♯'}.get(alter, f'({alter})')
                    print(f"      - {step}{alter_str}{octave} ({note.get('note_type', 'N/A')})")

            if len(measure['notes']) > 5:
                print(f"      ... et {len(measure['notes']) - 5} autres notes")

        if len(part['measures']) > 3:
            print(f"\n  ... et {len(part['measures']) - 3} autres mesures")

    print("\n" + "="*60)
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_mxl_parsing.py <fichier.mxl>")
        sys.exit(1)

    mxl_path = sys.argv[1]
    success = test_mxl_file(mxl_path)
    sys.exit(0 if success else 1)
