#!/usr/bin/env python3
"""
Analyse complète du MusicXML généré par Audiveris
Pour comprendre exactement quelles données sont disponibles
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.ocr_reader import AudiverisOCR

def analyze_musicxml(mxl_path):
    """Analyse complète d'un fichier MusicXML"""

    print("=" * 80)
    print(f"ANALYSE COMPLÈTE DE: {mxl_path}")
    print("=" * 80)

    ocr = AudiverisOCR()
    data = ocr.parse_musicxml(Path(mxl_path))

    if not data:
        print("❌ Erreur de parsing")
        return

    # 1. MÉTADONNÉES GLOBALES
    print("\n" + "=" * 80)
    print("1. MÉTADONNÉES GLOBALES")
    print("=" * 80)
    print(json.dumps(data.get('metadata', {}), indent=2, ensure_ascii=False))

    # 2. INFORMATIONS DE FICHIER
    print("\n" + "=" * 80)
    print("2. INFORMATIONS DE FICHIER")
    print("=" * 80)
    print(f"Source: {data.get('source_file')}")
    print(f"Nombre de parties: {len(data.get('parts', []))}")

    # 3. STRUCTURE DES PARTIES
    print("\n" + "=" * 80)
    print("3. STRUCTURE DES PARTIES")
    print("=" * 80)
    for i, part in enumerate(data.get('parts', [])):
        print(f"\nPartie {i+1}: {part.get('id')}")
        print(f"  - Nom: {part.get('name')}")
        print(f"  - Nombre de mesures: {len(part.get('measures', []))}")

        # Analyser la première mesure en détail
        if part.get('measures'):
            first_measure = part['measures'][0]
            print(f"\n  Première mesure (détails):")
            print(f"    - Numéro: {first_measure.get('number')}")
            print(f"    - Attributs disponibles:")

            attrs = first_measure.get('attributes', {})
            for key, value in attrs.items():
                print(f"      • {key}: {value}")

            # Direction (tempo, etc.)
            if first_measure.get('direction'):
                print(f"    - Direction: {first_measure['direction']}")

            # Notes
            print(f"    - Nombre de notes: {len(first_measure.get('notes', []))}")
            if first_measure.get('notes'):
                print(f"    - Première note (détails):")
                first_note = first_measure['notes'][0]
                for key, value in first_note.items():
                    print(f"      • {key}: {value}")

    # 4. EXTRACTION DÉTAILLÉE DES NOTES
    print("\n" + "=" * 80)
    print("4. TOUTES LES NOTES DE LA PREMIÈRE PARTIE")
    print("=" * 80)

    if data.get('parts'):
        part = data['parts'][0]
        note_count = 0

        for measure in part.get('measures', []):
            print(f"\nMesure {measure.get('number')}:")

            for note in measure.get('notes', []):
                note_count += 1

                if note['type'] == 'note':
                    pitch_info = note.get('pitch', {})
                    pitch_str = f"{pitch_info.get('step', '?')}{pitch_info.get('octave', '?')}"
                    if pitch_info.get('alter'):
                        alter_str = "#" if pitch_info['alter'] > 0 else "b"
                        pitch_str += alter_str

                    duration = note.get('duration', '?')
                    note_type = note.get('note_type', '?')

                    print(f"  {note_count}. {pitch_str:5s} - durée:{duration:3} type:{note_type:10s} "
                          f"midi:{note.get('midi', '?')}")
                else:
                    print(f"  {note_count}. SILENCE - durée:{note.get('duration', '?')}")

        print(f"\nTotal: {note_count} notes/silences")

    # 5. STRUCTURE COMPLÈTE (JSON)
    print("\n" + "=" * 80)
    print("5. STRUCTURE COMPLÈTE (extrait)")
    print("=" * 80)

    # Afficher seulement les clés principales
    def show_structure(obj, indent=0):
        prefix = "  " * indent
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}: {type(value).__name__} ({len(value) if isinstance(value, (list, dict)) else 0})")
                    if indent < 2:  # Limiter la profondeur
                        show_structure(value, indent + 1)
                else:
                    print(f"{prefix}{key}: {value}")
        elif isinstance(obj, list) and obj:
            print(f"{prefix}[{len(obj)} éléments]")
            if indent < 2:
                show_structure(obj[0], indent + 1)

    show_structure(data)

    print("\n" + "=" * 80)
    print("FIN DE L'ANALYSE")
    print("=" * 80)

if __name__ == '__main__':
    mxl_file = 'temp/roi_dagobert.mxl'

    if len(sys.argv) > 1:
        mxl_file = sys.argv[1]

    if not Path(mxl_file).exists():
        print(f"❌ Fichier non trouvé: {mxl_file}")
        sys.exit(1)

    analyze_musicxml(mxl_file)
