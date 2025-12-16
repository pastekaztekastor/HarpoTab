#!/usr/bin/env python3
"""
Test spécifique pour Le Roi Dagobert
"""
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from app import process_conversion
from config import Config

def test_roi_dagobert():
    """Test avec la partition du Roi Dagobert"""

    test_pdf = Path('roi_dagobert.pdf')

    if not test_pdf.exists():
        logger.error(f"❌ Fichier {test_pdf} introuvable")
        return False

    logger.info(f"📄 Test avec: {test_pdf}")
    logger.info(f"🎵 Harmonica: diatonic C")
    logger.info("=" * 70)

    # Créer les dossiers
    Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
    Config.OUTPUT_FOLDER.mkdir(exist_ok=True)
    Config.TEMP_FOLDER.mkdir(exist_ok=True)

    # Copier dans uploads
    import shutil
    upload_path = Config.UPLOAD_FOLDER / test_pdf.name
    shutil.copy(test_pdf, upload_path)

    try:
        result = process_conversion(
            input_file=upload_path,
            harmonica_type='diatonic',
            harmonica_key='C',
            output_dir=Config.OUTPUT_FOLDER
        )

        logger.info("=" * 70)

        if result['success']:
            logger.info("✅ ✅ ✅ CONVERSION RÉUSSIE ✅ ✅ ✅")
            logger.info(f"📁 PDF: {result['pdf_path']}")
            logger.info(f"📊 Métadonnées:")
            for key, value in result['metadata'].items():
                logger.info(f"   - {key}: {value}")

            # Afficher le contenu du fichier .ly généré
            ly_file = result['pdf_path'].with_suffix('.ly')
            if ly_file.exists():
                logger.info("\n" + "=" * 70)
                logger.info("Contenu Lilypond généré:")
                logger.info("=" * 70)
                with open(ly_file, 'r') as f:
                    print(f.read())
                logger.info("=" * 70)

            return True
        else:
            logger.error(f"❌ ÉCHEC: {result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_roi_dagobert()
    sys.exit(0 if success else 1)
