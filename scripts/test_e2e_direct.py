#!/usr/bin/env python3
"""
Test end-to-end avec MusicXML direct (bypass OCR)
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.melody_extractor import extract_melody_from_musicxml
from modules.music_analyzer import analyze_music
from modules.transposer import transpose_for_harmonica
from modules.harmonica_mapper import map_to_harmonica
from modules.lilypond_generator import generate_pdf
from config import Config
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_simple_musicxml_data():
    """Crée une mélodie simple C D E F G A B C directement"""
    return {
        'parts': {
            'P1': {
                'name': 'Melody',
                'measures': [
                    {
                        'number': 1,
                        'notes': [
                            {'type': 'note', 'pitch': 'C', 'octave': 4, 'duration': 4, 'alter': 0},
                            {'type': 'note', 'pitch': 'D', 'octave': 4, 'duration': 4, 'alter': 0},
                            {'type': 'note', 'pitch': 'E', 'octave': 4, 'duration': 4, 'alter': 0},
                            {'type': 'note', 'pitch': 'F', 'octave': 4, 'duration': 4, 'alter': 0},
                        ]
                    },
                    {
                        'number': 2,
                        'notes': [
                            {'type': 'note', 'pitch': 'G', 'octave': 4, 'duration': 4, 'alter': 0},
                            {'type': 'note', 'pitch': 'A', 'octave': 4, 'duration': 4, 'alter': 0},
                            {'type': 'note', 'pitch': 'B', 'octave': 4, 'duration': 4, 'alter': 0},
                            {'type': 'note', 'pitch': 'C', 'octave': 5, 'duration': 4, 'alter': 0},
                        ]
                    }
                ]
            }
        },
        'time_signature': '4/4',
        'key_signature': {'fifths': 0, 'mode': 'major'},  # C major
        'tempo': 120
    }


def main():
    print("=" * 70)
    print("🎵 TEST END-TO-END HARPOTAB (MusicXML Direct)")
    print("=" * 70)

    # Créer les dossiers nécessaires
    Config.OUTPUT_FOLDER.mkdir(exist_ok=True)
    Config.TEMP_FOLDER.mkdir(exist_ok=True)

    try:
        # ÉTAPE 1: Créer les données MusicXML
        logger.info("Étape 1/6: Création MusicXML simple")
        musicxml_data = create_simple_musicxml_data()
        logger.info("✓ MusicXML créé: Gamme de Do majeur (C D E F G A B C)")

        # ÉTAPE 2: Extraction mélodie
        logger.info("Étape 2/6: Extraction de la mélodie")
        melody_data = extract_melody_from_musicxml(musicxml_data)
        logger.info(f"✓ Mélodie extraite: {len(melody_data['notes'])} notes")

        # ÉTAPE 3: Analyse musicale
        logger.info("Étape 3/6: Analyse musicale")
        analysis = analyze_music(melody_data['notes'])
        logger.info(f"✓ Tonalité: {analysis['key']}, Tessiture: {analysis['range']}")

        # ÉTAPE 4: Charger mapping harmonica
        logger.info("Étape 4/6: Chargement mapping harmonica")
        mapping_file = Config.HARMONICA_MAPS_DIR / 'diatonic_C.json'
        with open(mapping_file, 'r') as f:
            harmonica_map = json.load(f)
        logger.info(f"✓ Mapping chargé: {harmonica_map['description']}")

        # ÉTAPE 5: Transposition
        logger.info("Étape 5/6: Vérification jouabilité et transposition")
        final_melody, transposed, playability = transpose_for_harmonica(
            melody_data,
            harmonica_map
        )

        if not playability['playable']:
            logger.error(f"❌ Morceau injouable: {playability.get('reason')}")
            return False

        logger.info(f"✓ Transposition: {transposed:+d} demi-tons")
        logger.info(f"✓ Jouabilité: {playability['coverage']:.1%}")

        # ÉTAPE 6: Génération tablature
        logger.info("Étape 6/6: Génération tablature")
        tablature = map_to_harmonica(
            melody=final_melody['notes'],
            harmonica_type='diatonic',
            harmonica_key='C',
            maps_dir=Config.HARMONICA_MAPS_DIR
        )
        logger.info(f"✓ Tablature générée: {len(tablature)} positions")

        # Afficher la tablature
        print()
        print("=" * 70)
        print("📝 TABLATURE GÉNÉRÉE")
        print("=" * 70)
        for i, tab in enumerate(tablature[:10]):  # Afficher les 10 premières
            note = final_melody['notes'][i]
            direction = "↑" if tab['direction'] == 'blow' else "↓"
            bend = f" (bend: {tab['technique']})" if tab.get('technique') else ""
            print(f"{i+1}. {note['pitch']}{note['octave']} → Trou {tab['hole']}{direction}{bend}")

        print()
        print("=" * 70)
        print("✅ ✅ ✅ TEST RÉUSSI ✅ ✅ ✅")
        print("=" * 70)
        print("Le pipeline fonctionne de bout en bout !")
        print("Note: La génération PDF Lilypond n'est pas encore implémentée")
        print("=" * 70)

        return True

    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
