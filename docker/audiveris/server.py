#!/usr/bin/env python3
"""
Serveur HTTP pour Audiveris OCR

API REST simple qui expose Audiveris en ligne de commande.
"""

import os
import subprocess
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = Path('/uploads')
OUTPUT_FOLDER = Path('/outputs')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({
        'status': 'healthy',
        'service': 'audiveris-ocr',
        'version': '5.9.0'
    })


@app.route('/ocr', methods=['POST'])
def process_ocr():
    """
    Traite une partition musicale avec Audiveris

    Paramètres:
        - file: Le fichier PDF ou image à traiter (multipart/form-data)

    Retourne:
        - JSON avec le chemin du fichier MusicXML généré
    """
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {ALLOWED_EXTENSIONS}'}), 400

        # Sauvegarder le fichier
        filename = secure_filename(file.filename)
        input_path = UPLOAD_FOLDER / filename
        file.save(str(input_path))

        logger.info(f"Processing file: {filename}")

        # Préparer les chemins de sortie
        output_name = input_path.stem
        output_dir = OUTPUT_FOLDER / output_name
        output_dir.mkdir(exist_ok=True)

        # Exécuter Audiveris
        cmd = [
            'audiveris',
            '-batch',
            '-export',
            '-output', str(output_dir),
            str(input_path)
        ]

        logger.info(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )

        if result.returncode != 0:
            logger.error(f"Audiveris failed: {result.stderr}")
            return jsonify({
                'error': 'Audiveris processing failed',
                'details': result.stderr
            }), 500

        # Trouver le fichier MusicXML généré
        musicxml_files = list(output_dir.glob('*.mxl')) + list(output_dir.glob('*.xml'))

        if not musicxml_files:
            logger.error("No MusicXML file generated")
            return jsonify({
                'error': 'No MusicXML file generated',
                'output': result.stdout
            }), 500

        # Prendre le premier fichier MusicXML trouvé
        musicxml_path = musicxml_files[0]

        # Retourner les informations
        relative_path = str(musicxml_path.relative_to(OUTPUT_FOLDER))

        logger.info(f"Successfully processed {filename} -> {relative_path}")

        return jsonify({
            'success': True,
            'input_file': filename,
            'output_file': relative_path,
            'output_path': f'/outputs/{relative_path}'
        })

    except subprocess.TimeoutExpired:
        logger.error("Audiveris processing timed out")
        return jsonify({'error': 'Processing timed out (max 5 minutes)'}), 500

    except Exception as e:
        logger.exception("Unexpected error during OCR processing")
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """
    Télécharge un fichier MusicXML généré

    Paramètres:
        - filename: Chemin relatif du fichier dans /outputs
    """
    try:
        file_path = OUTPUT_FOLDER / filename

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        return send_file(str(file_path), as_attachment=True)

    except Exception as e:
        logger.exception("Error downloading file")
        return jsonify({'error': str(e)}), 500


@app.route('/list', methods=['GET'])
def list_outputs():
    """Liste tous les fichiers MusicXML générés"""
    try:
        files = []
        for ext in ['*.mxl', '*.xml']:
            files.extend([
                str(f.relative_to(OUTPUT_FOLDER))
                for f in OUTPUT_FOLDER.rglob(ext)
            ])

        return jsonify({
            'files': sorted(files),
            'count': len(files)
        })

    except Exception as e:
        logger.exception("Error listing files")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Audiveris OCR Service on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)
