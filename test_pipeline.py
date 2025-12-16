#!/usr/bin/env python3
"""
Script de test pour valider le pipeline end-to-end de HarpoTab
"""
import sys
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from app import process_conversion
from config import Config


def test_pipeline():
    """Test du pipeline complet de conversion"""

    # Chercher un fichier PDF de test
    test_pdfs = list(Path('.').glob('*.pdf'))

    if not test_pdfs:
        logger.error("❌ Aucun fichier PDF de test trouvé dans le dossier courant")
        logger.info("Créez un fichier PDF de partition pour tester le pipeline")
        return False

    test_pdf = test_pdfs[0]
    logger.info(f"📄 Fichier de test: {test_pdf}")

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
    import shutil
    upload_path = Config.UPLOAD_FOLDER / test_pdf.name
    shutil.copy(test_pdf, upload_path)

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
    logger.info("🎹 TEST DU PIPELINE HARPOTAB 🎹")
    logger.info("=" * 70)

    success = test_pipeline()

    logger.info("=" * 70)
    if success:
        logger.info("✅ Test terminé avec SUCCÈS")
        sys.exit(0)
    else:
        logger.info("❌ Test ÉCHOUÉ")
        sys.exit(1)
