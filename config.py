"""
Configuration de l'application HarpoTab
"""
import os
from pathlib import Path

# Répertoire de base du projet
BASE_DIR = Path(__file__).parent.absolute()

# === Configuration Flask ===
class Config:
    """Configuration de base"""

    # Secret key pour les sessions Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Dossiers
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    OUTPUT_FOLDER = BASE_DIR / 'static' / 'outputs'
    DATA_FOLDER = BASE_DIR / 'data'
    TEMP_FOLDER = BASE_DIR / 'temp'

    # Taille maximale des uploads
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB pour PDF/images

    # Extensions autorisées (Phase 1)
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # Extensions Phase 2 (futures)
    ALLOWED_EXTENSIONS_AUDIO = {'mp3', 'wav', 'ogg'}

    # === Configuration Audiveris ===
    AUDIVERIS_PATH = os.environ.get('AUDIVERIS_PATH') or '/usr/local/bin/audiveris'
    AUDIVERIS_BATCH = True

    # === Configuration Lilypond ===
    LILYPOND_PATH = os.environ.get('LILYPOND_PATH') or 'lilypond'
    LILYPOND_VERSION = '2.24.0'

    # === Configuration des harmonicas ===
    HARMONICA_MAPS_DIR = DATA_FOLDER / 'harmonica_maps'

    # Types d'harmonica disponibles
    HARMONICA_TYPES = {
        'diatonic': {
            'name': 'Diatonique (Richter 10 trous)',
            'keys': ['C', 'D', 'E', 'F', 'G', 'A', 'Bb', 'B']
        },
        'chromatic': {
            'name': 'Chromatique',
            'keys': ['C', 'G']
        }
    }

    # === Options de traitement ===
    # OCR
    OCR_DPI = 300
    OCR_THRESHOLD = 0.8  # Confiance minimale

    # Transposition
    AUTO_TRANSPOSE = True
    PREFER_LOWER_KEYS = True  # Préférer les tonalités plus basses si possible

    # Génération PDF
    PDF_FORMAT = 'A4'
    PDF_ORIENTATION = 'portrait'

    # === Développement ===
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

    @staticmethod
    def init_app(app):
        """Initialisation de l'application"""
        # Créer les dossiers nécessaires
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    # En production, utiliser une vraie clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Log vers syslog en production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    WTF_CSRF_ENABLED = False


# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
