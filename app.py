"""
HarpoTab - Application Flask principale
Convertisseur de partitions musicales vers tablature harmonica
"""
import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from config import config, Config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Factory pour créer l'application Flask"""

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Routes
    @app.route('/')
    def index():
        """Page d'accueil"""
        return render_template('index.html')

    @app.route('/convert', methods=['GET', 'POST'])
    def convert():
        """Page de conversion"""
        if request.method == 'GET':
            # Afficher le formulaire
            return render_template('convert.html', harmonica_types=Config.HARMONICA_TYPES)

        # POST: traiter l'upload
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Format de fichier non supporté', 'error')
            return redirect(request.url)

        # Récupérer les paramètres
        harmonica_type = request.form.get('harmonica_type', 'diatonic')
        harmonica_key = request.form.get('harmonica_key', 'C')

        # Sauvegarder le fichier
        filename = secure_filename(file.filename)
        upload_path = Config.UPLOAD_FOLDER / filename
        file.save(str(upload_path))

        logger.info(f"Fichier uploadé: {filename}")
        logger.info(f"Harmonica: {harmonica_type} en {harmonica_key}")

        # TODO: Traitement de la conversion
        # 1. OCR de la partition
        # 2. Extraction mélodie
        # 3. Analyse musicale
        # 4. Transposition si nécessaire
        # 5. Génération tablature
        # 6. Génération PDF

        flash('Conversion en cours... (fonctionnalité à implémenter)', 'info')

        # Pour l'instant, redirection vers page de résultat fictive
        return redirect(url_for('result', filename=filename))

    @app.route('/result/<filename>')
    def result(filename):
        """Page de résultat"""
        # TODO: Afficher le résultat réel
        return render_template(
            'result.html',
            filename=filename,
            status='pending',
            message='Conversion à implémenter'
        )

    @app.route('/download/<filename>')
    def download(filename):
        """Téléchargement du PDF généré"""
        # TODO: Implémenter téléchargement
        output_path = Config.OUTPUT_FOLDER / filename

        if not output_path.exists():
            flash('Fichier non trouvé', 'error')
            return redirect(url_for('index'))

        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=filename
        )

    @app.route('/about')
    def about():
        """Page À propos"""
        return render_template('about.html')

    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Erreur serveur: {error}")
        return render_template('500.html'), 500

    return app


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


if __name__ == '__main__':
    # Mode développement
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
