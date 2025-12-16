#!/usr/bin/env python3
"""
Test spécifique pour Test_EndToEnd1.jpg
"""
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from app import process_conversion
from config import Config
import shutil

def test_specific_file():
    """Test avec un fichier spécifique"""

    # Fichier spécifique à tester
    test_file = Path('Test_EndToEnd1.jpg')

    if not test_file.exists():
        logger.error(f"❌ Fichier non trouvé: {test_file}")
        return False

    logger.info(f"📄 Fichier de test: {test_file}")

    # Configuration du test
    harmonica_type = 'diatonic'
    harmonica_key = 'C'

    logger.info(f"🎵 Harmonica: {harmonica_type} {harmonica_key}")
    logger.info("=" * 70)

    # Créer les dossiers nécessaires
    Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
    Config.OUTPUT_FOLDER.mkdir(exist_ok=True)
    Config.TEMP_FOLDER.mkdir(exist_ok=True)

    # Copier le fichier de test dans uploads
    upload_path = Config.UPLOAD_FOLDER / test_file.name
    shutil.copy(test_file, upload_path)

    try:
        # Lancer le pipeline
        logger.info("🚀 Démarrage du pipeline de conversion...")
        logger.info("=" * 70)

        result = process_conversion(
            input_file=upload_path,
            harmonica_type=harmonica_type,
            harmonica_key=harmonica_key,
            output_dir=Config.OUTPUT_FOLDER
        )

        logger.info("=" * 70)

        if result['success']:
            logger.info("✅ ✅ ✅ CONVERSION RÉUSSIE ✅ ✅ ✅")
            logger.info(f"📁 PDF généré: {result['pdf_path']}")
            logger.info(f"📊 Métadonnées:")
            for key, value in result['metadata'].items():
                logger.info(f"   - {key}: {value}")
            return True
        else:
            logger.error(f"❌ CONVERSION ÉCHOUÉE")
            logger.error(f"Erreur: {result.get('error', 'Erreur inconnue')}")
            return False

    except Exception as e:
        logger.error(f"❌ Exception pendant le test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🎹 TEST AVEC Test_EndToEnd1.jpg 🎹")
    logger.info("=" * 70)

    success = test_specific_file()

    logger.info("=" * 70)
    if success:
        logger.info("✅ Test terminé avec SUCCÈS")
        sys.exit(0)
    else:
        logger.info("❌ Test ÉCHOUÉ")
        sys.exit(1)
