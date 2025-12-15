"""
HarpoTab - Application Flask principale
Convertisseur de partitions musicales vers tablature harmonica
"""
import os
import logging
import traceback
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from config import config, Config

# Import des modules de traitement
from modules.ocr_reader import read_partition_from_pdf
from modules.melody_extractor import extract_melody_from_musicxml
from modules.music_analyzer import analyze_music
from modules.transposer import transpose_for_harmonica
from modules.harmonica_mapper import map_to_harmonica
from modules.lilypond_generator import generate_pdf

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_conversion(input_file, harmonica_type, harmonica_key, output_dir):
    """
    Pipeline complet de conversion : PDF -> MusicXML -> Mélodie -> Tablature -> PDF final

    Args:
        input_file (Path): Chemin du fichier PDF d'entrée
        harmonica_type (str): Type d'harmonica (ex: 'diatonic')
        harmonica_key (str): Tonalité de l'harmonica (ex: 'C')
        output_dir (Path): Répertoire de sortie

    Returns:
        dict: Résultat avec chemin du PDF généré et métadonnées

    Raises:
        Exception: En cas d'erreur à n'importe quelle étape
    """
    result = {
        'success': False,
        'pdf_path': None,
        'metadata': {},
        'error': None
    }

    try:
        # ============================================================
        # ÉTAPE 1: OCR Musical (Audiveris)
        # ============================================================
        logger.info(f"Étape 1/7: OCR de la partition {input_file.name}")

        try:
            musicxml_data = read_partition_from_pdf(
                pdf_path=input_file,
                output_dir=Config.TEMP_FOLDER
            )
            if not musicxml_data:
                raise Exception("Échec de la lecture de la partition")
            logger.info(f"✓ Partition lue avec succès")
        except Exception as e:
            raise Exception(f"Échec de l'OCR musical: {str(e)}")

        # ============================================================
        # ÉTAPE 2: Extraction de la mélodie
        # ============================================================
        logger.info("Étape 2/7: Extraction de la mélodie principale")

        try:
            melody_data = extract_melody_from_musicxml(
                musicxml_data=musicxml_data,
                keep_rests=True,
                simplify_chords=True
            )
            if not melody_data or not melody_data.get('notes'):
                raise Exception("Aucune mélodie détectée dans la partition")
            logger.info(f"✓ Mélodie extraite: {len(melody_data['notes'])} notes")
        except Exception as e:
            raise Exception(f"Échec de l'extraction de mélodie: {str(e)}")

        # ============================================================
        # ÉTAPE 3: Analyse musicale
        # ============================================================
        logger.info("Étape 3/7: Analyse musicale (tonalité, tessiture)")

        try:
            analysis = analyze_music(melody_data['notes'])
            logger.info(f"✓ Tonalité détectée: {analysis.get('key', 'Inconnue')}")
            logger.info(f"✓ Tessiture: {analysis.get('range', {})}")
            result['metadata']['original_key'] = analysis.get('key')
            result['metadata']['range'] = analysis.get('range')
        except Exception as e:
            raise Exception(f"Échec de l'analyse musicale: {str(e)}")

        # ============================================================
        # ÉTAPE 4: Charger le mapping de l'harmonica
        # ============================================================
        logger.info(f"Chargement mapping harmonica {harmonica_type} {harmonica_key}")

        try:
            import json
            mapping_file = Config.HARMONICA_MAPS_DIR / f"{harmonica_type}_{harmonica_key}.json"

            if not mapping_file.exists():
                raise Exception(f"Mapping non trouvé: {mapping_file}")

            with open(mapping_file, 'r', encoding='utf-8') as f:
                harmonica_map = json.load(f)

            logger.info(f"✓ Mapping chargé: {harmonica_map.get('description', '')}")
        except Exception as e:
            raise Exception(f"Échec du chargement du mapping: {str(e)}")

        # ============================================================
        # ÉTAPE 5: Transposition automatique
        # ============================================================
        logger.info(f"Étape 5/7: Vérification jouabilité sur harmonica {harmonica_type} {harmonica_key}")

        try:
            final_melody, transposed_semitones, playability = transpose_for_harmonica(
                melody_data,
                harmonica_map,
                force_transpose=None
            )

            if not playability.get('playable'):
                raise Exception(
                    f"Ce morceau n'est pas jouable sur un harmonica {harmonica_type} {harmonica_key}. "
                    f"Raison: {playability.get('reason', 'Tessiture incompatible')}"
                )

            if transposed_semitones != 0:
                logger.info(f"✓ Transposition appliquée: {transposed_semitones:+d} demi-tons")
                result['metadata']['transposition'] = transposed_semitones
            else:
                logger.info("✓ Aucune transposition nécessaire")
                result['metadata']['transposition'] = 0

        except ValueError as e:
            raise Exception(f"Impossible de transposer: {str(e)}")
        except Exception as e:
            raise Exception(f"Échec de la transposition: {str(e)}")

        # ============================================================
        # ÉTAPE 6: Génération de la tablature
        # ============================================================
        logger.info("Étape 6/7: Génération de la tablature harmonica")

        try:
            tablature = map_to_harmonica(
                melody=final_melody['notes'],
                harmonica_type=harmonica_type,
                harmonica_key=harmonica_key,
                maps_dir=Config.HARMONICA_MAPS_DIR
            )

            if not tablature:
                raise Exception("Impossible de générer la tablature")

            logger.info(f"✓ Tablature générée: {len(tablature)} positions")
        except Exception as e:
            raise Exception(f"Échec de la génération de tablature: {str(e)}")

        # ============================================================
        # ÉTAPE 7: Génération du PDF final (Lilypond)
        # ============================================================
        logger.info("Étape 7/7: Génération du PDF avec Lilypond")

        output_filename = f"{input_file.stem}_tablature.pdf"
        output_pdf = output_dir / output_filename

        try:
            # Préparer les métadonnées pour Lilypond
            metadata = {
                'title': melody_data.get('title') or input_file.stem.replace('_', ' ').title(),
                'composer': melody_data.get('composer', ''),
                'key': analysis.get('key', 'C'),
                'harmonica_type': harmonica_type,
                'harmonica_key': harmonica_key,
                'transposition': result['metadata'].get('transposition', 0),
                'time_signature': melody_data.get('time_signature', '4/4'),
                'tempo': melody_data.get('tempo', 120)
            }

            success = generate_pdf(
                melody=final_melody['notes'],
                tabs=tablature,
                metadata=metadata,
                output_path=output_pdf
            )

            if not success or not output_pdf.exists():
                raise Exception("Le fichier PDF n'a pas été créé")

            logger.info(f"✓ PDF généré: {output_pdf}")

        except NotImplementedError as e:
            # Le module Lilypond n'est pas encore complètement implémenté
            logger.warning(f"Génération PDF non implémentée: {str(e)}")
            raise Exception(
                "La génération de PDF n'est pas encore implémentée. "
                "Les étapes OCR → Mélodie → Transposition → Tablature ont réussi !"
            )
        except Exception as e:
            raise Exception(f"Échec de la génération PDF: {str(e)}")

        # ============================================================
        # SUCCÈS !
        # ============================================================
        result['success'] = True
        result['pdf_path'] = output_pdf
        result['metadata']['harmonica_type'] = harmonica_type
        result['metadata']['harmonica_key'] = harmonica_key
        result['metadata']['filename'] = output_filename

        logger.info("=" * 60)
        logger.info("✓✓✓ CONVERSION RÉUSSIE ✓✓✓")
        logger.info(f"PDF généré: {output_filename}")
        logger.info("=" * 60)

        return result

    except Exception as e:
        logger.error(f"Erreur lors de la conversion: {str(e)}")
        logger.error(traceback.format_exc())
        result['error'] = str(e)
        return result


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

        # ============================================================
        # TRAITEMENT DE LA CONVERSION
        # ============================================================
        try:
            conversion_result = process_conversion(
                input_file=upload_path,
                harmonica_type=harmonica_type,
                harmonica_key=harmonica_key,
                output_dir=Config.OUTPUT_FOLDER
            )

            if conversion_result['success']:
                # Conversion réussie
                flash('Conversion réussie !', 'success')

                # Ajouter les métadonnées au résultat
                metadata = conversion_result['metadata']
                if metadata.get('transposition', 0) != 0:
                    trans = metadata['transposition']
                    flash(
                        f"Transposition appliquée: {trans:+d} demi-tons pour adapter à votre harmonica",
                        'info'
                    )

                return redirect(url_for(
                    'result',
                    filename=conversion_result['metadata']['filename'],
                    success=True
                ))
            else:
                # Conversion échouée
                error_msg = conversion_result.get('error', 'Erreur inconnue')
                flash(f"Échec de la conversion: {error_msg}", 'error')
                logger.error(f"Conversion failed: {error_msg}")
                return redirect(url_for('convert'))

        except Exception as e:
            flash(f"Erreur inattendue: {str(e)}", 'error')
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return redirect(url_for('convert'))

    @app.route('/result/<filename>')
    def result(filename):
        """Page de résultat"""
        success = request.args.get('success', 'false').lower() == 'true'

        # Vérifier que le fichier existe
        output_path = Config.OUTPUT_FOLDER / filename
        file_exists = output_path.exists()

        return render_template(
            'result.html',
            filename=filename,
            success=success and file_exists,
            file_exists=file_exists
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
