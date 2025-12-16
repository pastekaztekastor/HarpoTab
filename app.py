"""
HarpoTab - Application Flask principale
Convertisseur de partitions musicales vers tablature harmonica
"""
import os
import logging
import traceback
import threading
import uuid
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
from modules.progress_tracker import create_tracker, get_tracker, remove_tracker

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_conversion(input_file, harmonica_type, harmonica_key, output_dir, tracker=None):
    """
    Pipeline complet de conversion : PDF -> MusicXML -> Mélodie -> Tablature -> PDF final

    Args:
        input_file (Path): Chemin du fichier PDF d'entrée
        harmonica_type (str): Type d'harmonica (ex: 'diatonic')
        harmonica_key (str): Tonalité de l'harmonica (ex: 'C')
        output_dir (Path): Répertoire de sortie
        tracker (ProgressTracker, optional): Tracker de progression

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
        if tracker:
            tracker.start_step('ocr', f"Lecture de {input_file.name}")
            tracker.start_substep('ocr', 'ocr_init', "Initialisation Audiveris")

        logger.info(f"Étape 1/7: OCR de la partition {input_file.name}")

        try:
            if tracker:
                tracker.complete_substep('ocr', 'ocr_init', "Audiveris prêt")
                tracker.start_substep('ocr', 'ocr_process', "Analyse de la partition...")

            musicxml_data = read_partition_from_pdf(
                pdf_path=input_file,
                output_dir=Config.TEMP_FOLDER
            )
            if not musicxml_data:
                raise Exception("Échec de la lecture de la partition")

            if tracker:
                tracker.complete_substep('ocr', 'ocr_process', "Partition analysée")
                tracker.start_substep('ocr', 'ocr_parse', "Extraction des données MusicXML")

            logger.info(f"✓ Partition lue avec succès")

            if tracker:
                tracker.complete_substep('ocr', 'ocr_parse', "MusicXML extrait")
                tracker.complete_step('ocr', f"{len(musicxml_data.get('parts', []))} parties détectées")
        except Exception as e:
            if tracker:
                tracker.error_step('ocr', str(e))
            raise Exception(f"Échec de l'OCR musical: {str(e)}")

        # ============================================================
        # ÉTAPE 2: Extraction de la mélodie
        # ============================================================
        if tracker:
            tracker.start_step('melody', "Extraction de la ligne mélodique")
            tracker.start_substep('melody', 'melody_select', "Sélection de la partie principale")

        logger.info("Étape 2/7: Extraction de la mélodie principale")

        try:
            if tracker:
                tracker.complete_substep('melody', 'melody_select', "Partie sélectionnée")
                tracker.start_substep('melody', 'melody_extract', "Extraction des notes...")

            melody_data = extract_melody_from_musicxml(
                musicxml_data=musicxml_data,
                keep_rests=True,
                simplify_chords=True
            )
            if not melody_data or not melody_data.get('notes'):
                raise Exception("Aucune mélodie détectée dans la partition")

            logger.info(f"✓ Mélodie extraite: {len(melody_data['notes'])} notes")

            if tracker:
                tracker.complete_substep('melody', 'melody_extract', f"{len(melody_data['notes'])} notes extraites")
                tracker.complete_step('melody', f"{len(melody_data['notes'])} notes")
        except Exception as e:
            if tracker:
                tracker.error_step('melody', str(e))
            raise Exception(f"Échec de l'extraction de mélodie: {str(e)}")

        # ============================================================
        # ÉTAPE 3: Analyse musicale
        # ============================================================
        if tracker:
            tracker.start_step('analysis', "Analyse de la tessiture et tonalité")
            tracker.start_substep('analysis', 'analysis_key', "Détection de la tonalité...")

        logger.info("Étape 3/7: Analyse musicale (tonalité, tessiture)")

        try:
            analysis = analyze_music(melody_data['notes'])

            if tracker:
                tracker.complete_substep('analysis', 'analysis_key', f"Tonalité: {analysis.get('key', 'Inconnue')}")
                tracker.start_substep('analysis', 'analysis_range', "Calcul de la tessiture...")

            logger.info(f"✓ Tonalité détectée: {analysis.get('key', 'Inconnue')}")
            logger.info(f"✓ Tessiture: {analysis.get('range', {})}")
            result['metadata']['original_key'] = analysis.get('key')
            result['metadata']['range'] = analysis.get('range')

            if tracker:
                range_info = analysis.get('range', {})
                range_str = f"{range_info.get('lowest', 'N/A')} - {range_info.get('highest', 'N/A')}"
                tracker.complete_substep('analysis', 'analysis_range', f"Tessiture: {range_str}")
                tracker.complete_step('analysis', f"Tonalité: {analysis.get('key', 'Inconnue')}")
        except Exception as e:
            if tracker:
                tracker.error_step('analysis', str(e))
            raise Exception(f"Échec de l'analyse musicale: {str(e)}")

        # ============================================================
        # ÉTAPE 4: Charger le mapping de l'harmonica
        # ============================================================
        if tracker:
            tracker.start_step('mapping_load', f"Chargement harmonica {harmonica_type} {harmonica_key}")

        logger.info(f"Chargement mapping harmonica {harmonica_type} {harmonica_key}")

        try:
            import json
            mapping_file = Config.HARMONICA_MAPS_DIR / f"{harmonica_type}_{harmonica_key}.json"

            if not mapping_file.exists():
                raise Exception(f"Mapping non trouvé: {mapping_file}")

            with open(mapping_file, 'r', encoding='utf-8') as f:
                harmonica_map = json.load(f)

            logger.info(f"✓ Mapping chargé: {harmonica_map.get('description', '')}")

            if tracker:
                tracker.complete_step('mapping_load', f"{harmonica_map.get('description', 'Mapping chargé')}")
        except Exception as e:
            if tracker:
                tracker.error_step('mapping_load', str(e))
            raise Exception(f"Échec du chargement du mapping: {str(e)}")

        # ============================================================
        # ÉTAPE 5: Transposition automatique
        # ============================================================
        if tracker:
            tracker.start_step('transpose', "Vérification de la jouabilité")
            tracker.start_substep('transpose', 'transpose_check', "Analyse de la jouabilité...")

        logger.info(f"Étape 5/7: Vérification jouabilité sur harmonica {harmonica_type} {harmonica_key}")

        try:
            final_melody, transposed_semitones, playability = transpose_for_harmonica(
                melody_data,
                harmonica_map,
                force_transpose=None
            )

            if not playability.get('playable'):
                if tracker:
                    tracker.error_step('transpose', playability.get('reason', 'Tessiture incompatible'))
                raise Exception(
                    f"Ce morceau n'est pas jouable sur un harmonica {harmonica_type} {harmonica_key}. "
                    f"Raison: {playability.get('reason', 'Tessiture incompatible')}"
                )

            if tracker:
                tracker.complete_substep('transpose', 'transpose_check', "Jouable sur cet harmonica")
                tracker.start_substep('transpose', 'transpose_apply', "Application de la transposition...")

            if transposed_semitones != 0:
                logger.info(f"✓ Transposition appliquée: {transposed_semitones:+d} demi-tons")
                result['metadata']['transposition'] = transposed_semitones
                if tracker:
                    tracker.complete_substep('transpose', 'transpose_apply', f"Transposé de {transposed_semitones:+d} demi-tons")
                    tracker.complete_step('transpose', f"Transposé de {transposed_semitones:+d} demi-tons")
            else:
                logger.info("✓ Aucune transposition nécessaire")
                result['metadata']['transposition'] = 0
                if tracker:
                    tracker.complete_substep('transpose', 'transpose_apply', "Aucune transposition nécessaire")
                    tracker.complete_step('transpose', "Aucune transposition nécessaire")

        except ValueError as e:
            if tracker:
                tracker.error_step('transpose', str(e))
            raise Exception(f"Impossible de transposer: {str(e)}")
        except Exception as e:
            if tracker:
                tracker.error_step('transpose', str(e))
            raise Exception(f"Échec de la transposition: {str(e)}")

        # ============================================================
        # ÉTAPE 6: Génération de la tablature
        # ============================================================
        if tracker:
            tracker.start_step('tablature', "Génération de la tablature")
            tracker.start_substep('tablature', 'tablature_map', "Mapping notes → trous d'harmonica...")

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

            if tracker:
                tracker.complete_substep('tablature', 'tablature_map', f"{len(tablature)} positions mappées")
                tracker.start_substep('tablature', 'tablature_optimize', "Optimisation des positions...")

            logger.info(f"✓ Tablature générée: {len(tablature)} positions")

            if tracker:
                tracker.complete_substep('tablature', 'tablature_optimize', "Positions optimisées")
                tracker.complete_step('tablature', f"{len(tablature)} positions")
        except Exception as e:
            if tracker:
                tracker.error_step('tablature', str(e))
            raise Exception(f"Échec de la génération de tablature: {str(e)}")

        # ============================================================
        # ÉTAPE 7: Génération du PDF final (Lilypond)
        # ============================================================
        if tracker:
            tracker.start_step('pdf', "Génération du PDF final")
            tracker.start_substep('pdf', 'pdf_format', "Formatage Lilypond...")

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

            if tracker:
                tracker.complete_substep('pdf', 'pdf_format', "Fichier .ly créé")
                tracker.start_substep('pdf', 'pdf_compile', "Compilation Lilypond en cours...")

            success = generate_pdf(
                melody=final_melody['notes'],
                tabs=tablature,
                metadata=metadata,
                output_path=output_pdf
            )

            if not success or not output_pdf.exists():
                raise Exception("Le fichier PDF n'a pas été créé")

            logger.info(f"✓ PDF généré: {output_pdf}")

            if tracker:
                tracker.complete_substep('pdf', 'pdf_compile', "PDF compilé avec succès")
                tracker.complete_step('pdf', f"{output_filename}")

        except NotImplementedError as e:
            # Le module Lilypond n'est pas encore complètement implémenté
            logger.warning(f"Génération PDF non implémentée: {str(e)}")
            if tracker:
                tracker.error_step('pdf', "Génération PDF non implémentée")
            raise Exception(
                "La génération de PDF n'est pas encore implémentée. "
                "Les étapes OCR → Mélodie → Transposition → Tablature ont réussi !"
            )
        except Exception as e:
            if tracker:
                tracker.error_step('pdf', str(e))
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
        # TRAITEMENT DE LA CONVERSION EN ARRIÈRE-PLAN
        # ============================================================
        # Créer un tracker de progression
        session_id = str(uuid.uuid4())
        tracker = create_tracker(session_id)

        # Préparer le nom du fichier de sortie
        output_filename = f"{upload_path.stem}_tablature.pdf"

        # Fonction à exécuter dans le thread
        def conversion_thread():
            logger.info(f"🔥 Thread de conversion démarré pour session {session_id}")
            try:
                logger.info(f"Début de process_conversion pour {upload_path.name}")
                conversion_result = process_conversion(
                    input_file=upload_path,
                    harmonica_type=harmonica_type,
                    harmonica_key=harmonica_key,
                    output_dir=Config.OUTPUT_FOLDER,
                    tracker=tracker
                )
                logger.info(f"process_conversion terminé: success={conversion_result.get('success')}")

                # Nettoyer le tracker après 5 minutes
                threading.Timer(300, lambda: remove_tracker(session_id)).start()

            except Exception as e:
                logger.error(f"❌ Erreur dans le thread de conversion: {str(e)}")
                logger.error(traceback.format_exc())
                # Le tracker aura déjà l'erreur marquée via tracker.error_step()

        # Lancer la conversion dans un thread séparé
        logger.info(f"Lancement du thread de conversion pour session {session_id}")
        thread = threading.Thread(target=conversion_thread, daemon=True)
        thread.start()
        logger.info(f"Thread démarré (daemon={thread.daemon}, alive={thread.is_alive()})")

        # Rediriger immédiatement vers la page de progression
        return redirect(url_for('progress_page', session_id=session_id, filename=output_filename))

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

    @app.route('/progress')
    def progress_page():
        """Page de progression"""
        session_id = request.args.get('session_id')
        filename = request.args.get('filename', '')
        return render_template('progress.html', session_id=session_id, filename=filename)

    @app.route('/progress/<session_id>')
    def progress_stream(session_id):
        """Stream SSE de progression en temps réel"""
        from flask import Response, stream_with_context
        import json
        import time

        def generate():
            logger.info(f"SSE stream démarré pour session {session_id}")
            tracker = get_tracker(session_id)
            if not tracker:
                logger.error(f"Tracker non trouvé pour session {session_id}")
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
                return

            logger.info(f"Tracker trouvé pour session {session_id}")
            # Envoyer un message initial immédiatement
            yield f": keepalive\n\n"

            # Envoyer le status initial
            try:
                initial_status = tracker.get_status()
                logger.info(f"Status initial: {initial_status['overall_progress']}%")
                yield f"data: {json.dumps(initial_status)}\n\n"
            except Exception as e:
                logger.error(f"Erreur get_status initial: {e}")
                logger.error(traceback.format_exc())
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return

            # Polling toutes les 0.5 secondes
            last_status = initial_status
            for i in range(300):  # Max 2.5 minutes
                time.sleep(0.5)

                tracker = get_tracker(session_id)
                if not tracker:
                    logger.warning(f"Tracker disparu pour session {session_id}")
                    break

                current_status = tracker.get_status()

                # Toujours envoyer une mise à jour (même si pas de changement) toutes les 10 itérations
                # pour éviter les timeouts
                should_send = (current_status != last_status) or (i % 10 == 0)

                if should_send:
                    if current_status != last_status:
                        logger.info(f"Progress update: {current_status['overall_progress']}% (iteration {i})")
                    yield f"data: {json.dumps(current_status)}\n\n"
                    last_status = current_status

                # Arrêter si 100%
                if current_status['overall_progress'] >= 100:
                    logger.info(f"Progression terminée à 100% pour session {session_id}")
                    break

            logger.info(f"SSE stream terminé pour session {session_id}")

        response = Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        response.headers['Connection'] = 'keep-alive'
        return response

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
    # Désactiver le reloader pour éviter les problèmes avec les threads
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
