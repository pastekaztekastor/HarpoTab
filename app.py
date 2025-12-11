import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename
from modules.pdf_reader import extract_music_from_pdf, extract_music_from_image
from modules.music_parser import parse_musical_notes
from modules.harmonica import convert_to_harmonica
from modules.pdf_generator import generate_tablature_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre-cle-secrete-ici-changez-moi'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'musicxml', 'mxl', 'xml'}

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Page d'accueil avec formulaire d'upload"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Traite l'upload du fichier"""
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Récupérer les paramètres
        harmonica_type = request.form.get('harmonica_type', 'diatonic')
        tonality = request.form.get('tonality', 'C')
        notation_style = request.form.get('notation_style', 'arrows')

        return render_template('convert.html',
                             filename=filename,
                             harmonica_type=harmonica_type,
                             tonality=tonality,
                             notation_style=notation_style)

    flash('Type de fichier non autorisé. Utilisez PDF, PNG ou JPG.', 'danger')
    return redirect(url_for('index'))

@app.route('/convert', methods=['POST'])
def convert():
    """Convertit la partition en tablature"""
    try:
        filename = request.form.get('filename')
        harmonica_type = request.form.get('harmonica_type', 'diatonic')
        tonality = request.form.get('tonality', 'C')
        notation_style = request.form.get('notation_style', 'arrows')

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Étape 1 : Extraire les données musicales du fichier
        if filename.lower().endswith('.pdf'):
            music_data = extract_music_from_pdf(filepath)
        elif filename.lower().endswith(('.musicxml', '.mxl', '.xml')):
            # NOUVEAU : Support MusicXML
            from modules.pdf_reader import extract_music_from_musicxml
            music_data = extract_music_from_musicxml(filepath)
        else:
            music_data = extract_music_from_image(filepath)

        # Étape 2 : Parser les notes musicales
        notes = parse_musical_notes(music_data)

        # Étape 2.5 : NOUVEAU - Vérifier la jouabilité AVANT de générer
        from modules.harmonica import analyze_playability, find_best_tonalities

        # Analyser la jouabilité avec la tonalité choisie
        playability = analyze_playability(notes, harmonica_type, tonality)

        # Si pas complètement jouable, chercher des alternatives
        alternative_tonalities = []
        if not playability['is_fully_playable']:
            # Trouver les tonalités qui permettent de jouer au moins 80% de la mélodie
            alternative_tonalities = find_best_tonalities(notes, harmonica_type, min_playability=80.0)

        # Étape 3 : Convertir en tablature harmonica
        tablature = convert_to_harmonica(notes, harmonica_type, tonality, notation_style)

        # Ajouter titre et compositeur à la tablature pour LilyPond
        title = music_data.get('title', '')
        composer = music_data.get('composer', '')
        if title and tablature:
            for item in tablature:
                item['title'] = title
                item['composer'] = composer

        # Étape 4 : Générer le PDF de la tablature
        output_filename = f"tablature_{filename.rsplit('.', 1)[0]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Passer le fichier original pour l'inclure dans le PDF
        # generate_tablature_pdf retourne le chemin du fichier généré
        generated_path = generate_tablature_pdf(tablature, output_path, tonality, notation_style, original_file=filepath)

        # Extraire le nom du fichier généré (peut être différent si LilyPond)
        if generated_path:
            output_filename = os.path.basename(generated_path)

        return render_template('result.html',
                             tablature=tablature,
                             output_filename=output_filename,
                             original_filename=filename,
                             tonality=tonality,
                             notation_style=notation_style,
                             title=title,
                             composer=composer,
                             playability=playability,
                             alternative_tonalities=alternative_tonalities)

    except Exception as e:
        flash(f'Erreur lors de la conversion : {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    """Permet de télécharger le PDF généré"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

@app.route('/preview/<filename>')
def preview(filename):
    """Affiche un aperçu du fichier uploadé"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath)

@app.route('/regenerate', methods=['POST'])
def regenerate():
    """Régénère le PDF après édition manuelle de la tablature"""
    try:
        # Récupérer les paramètres
        tonality = request.form.get('tonality', 'C')
        notation_style = request.form.get('notation_style', 'arrows')
        title = request.form.get('title', '')
        composer = request.form.get('composer', '')

        # Reconstruire la tablature depuis le formulaire
        count = int(request.form.get('tablature_count', 0))
        tablature = []

        for i in range(count):
            # Vérifier si la ligne n'a pas été supprimée
            if f'measure_{i}' in request.form:
                tablature.append({
                    'measure': int(request.form.get(f'measure_{i}', 1)),
                    'note_name': request.form.get(f'note_{i}', ''),
                    'hole': int(request.form.get(f'hole_{i}', 0)),
                    'action': request.form.get(f'action_{i}', 'blow'),
                    'duration': request.form.get(f'duration_{i}', 'quarter'),
                    'tab_notation': '',  # Sera recalculé
                    'title': title,
                    'composer': composer
                })

        # Générer le nouveau PDF
        output_filename = f"tablature_edited_{len(tablature)}_notes.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        generated_path = generate_tablature_pdf(tablature, output_path, tonality, notation_style)

        if generated_path:
            output_filename = os.path.basename(generated_path)

        flash('Tablature régénérée avec succès !', 'success')

        # Retourner à la page de résultat avec la nouvelle tablature
        return render_template('result.html',
                             tablature=tablature,
                             output_filename=output_filename,
                             original_filename='',  # Pas de fichier original pour édition
                             tonality=tonality,
                             notation_style=notation_style,
                             title=title,
                             composer=composer,
                             playability=None,  # Pas de vérification pour édition manuelle
                             alternative_tonalities=[])

    except Exception as e:
        flash(f'Erreur lors de la régénération : {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
