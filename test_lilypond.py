#!/usr/bin/env python3
"""
Test simple de génération Lilypond
"""
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from modules.lilypond_generator import generate_pdf

def test_lilypond_generation():
    """Test de génération d'un PDF simple"""

    # Créer une mélodie simple (Do Ré Mi Fa Sol)
    melody = [
        {'type': 'note', 'pitch': 'C', 'octave': 4, 'duration': 4, 'alter': 0},
        {'type': 'note', 'pitch': 'D', 'octave': 4, 'duration': 4, 'alter': 0},
        {'type': 'note', 'pitch': 'E', 'octave': 4, 'duration': 4, 'alter': 0},
        {'type': 'note', 'pitch': 'F', 'octave': 4, 'duration': 4, 'alter': 0},
        {'type': 'note', 'pitch': 'G', 'octave': 4, 'duration': 4, 'alter': 0},
    ]

    # Créer la tablature correspondante
    tabs = [
        {'hole': 4, 'direction': 'blow', 'technique': None, 'duration': 4},
        {'hole': 4, 'direction': 'draw', 'technique': None, 'duration': 4},
        {'hole': 5, 'direction': 'blow', 'technique': None, 'duration': 4},
        {'hole': 5, 'direction': 'draw', 'technique': None, 'duration': 4},
        {'hole': 6, 'direction': 'blow', 'technique': None, 'duration': 4},
    ]

    # Métadonnées
    metadata = {
        'title': 'Test Simple',
        'composer': 'HarpoTab',
        'key': 'C',
        'time_signature': '4/4',
        'tempo': 120,
        'harmonica_type': 'diatonic',
        'harmonica_key': 'C',
        'transposition': 0
    }

    # Créer le dossier de sortie
    output_dir = Path('static/output')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / 'test_simple.pdf'

    logger.info(f"Génération de {output_path}")

    success = generate_pdf(
        melody=melody,
        tabs=tabs,
        metadata=metadata,
        output_path=output_path
    )

    if success and output_path.exists():
        logger.info(f"✅ PDF généré avec succès: {output_path}")

        # Vérifier aussi le fichier .ly
        ly_file = output_path.with_suffix('.ly')
        if ly_file.exists():
            logger.info(f"✅ Fichier .ly créé: {ly_file}")
            logger.info("\nContenu du fichier .ly:")
            logger.info("=" * 60)
            with open(ly_file, 'r') as f:
                print(f.read())
            logger.info("=" * 60)

        return True
    else:
        logger.error("❌ Échec de la génération du PDF")
        return False

if __name__ == '__main__':
    success = test_lilypond_generation()
    sys.exit(0 if success else 1)
