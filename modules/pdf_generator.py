"""
Module de génération de PDF pour les tablatures d'harmonica.

Utilise ReportLab pour créer des PDF professionnels avec :
- Partition originale en haut
- Tablature à 2 lignes (soufflé/aspiré) en dessous
- Notation musicale (durée des notes)
- Numéros de trou
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os


# Constantes pour le dessin de la portée
STAFF_LINE_HEIGHT = 8 * mm  # Espacement entre lignes
NOTE_WIDTH = 15 * mm        # Largeur d'une note
MEASURE_WIDTH = 60 * mm     # Largeur d'une mesure


def draw_staff_lines(c, x, y, width, num_lines=2):
    """
    Dessine les lignes de la portée (2 lignes pour harmonica).

    Args:
        c: Canvas ReportLab
        x, y: Position de départ
        width: Largeur des lignes
        num_lines: Nombre de lignes (2 pour harmonica)
    """
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)

    for i in range(num_lines):
        line_y = y - (i * STAFF_LINE_HEIGHT)
        c.line(x, line_y, x + width, line_y)


def draw_note_head(c, x, y, duration='quarter', filled=True):
    """
    Dessine la tête d'une note.

    Args:
        c: Canvas
        x, y: Position
        duration: Type de durée (whole, half, quarter, eighth)
        filled: Si True, note pleine (noire), sinon vide (blanche)
    """
    note_size = 3 * mm

    if duration in ['quarter', 'eighth', 'sixteenth']:
        # Note pleine (noire, croche, etc.)
        c.setFillColor(colors.black)
        c.ellipse(x - note_size/2, y - note_size/3,
                  x + note_size/2, y + note_size/3,
                  fill=1, stroke=0)
    else:
        # Note vide (blanche, ronde)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.5)
        c.ellipse(x - note_size/2, y - note_size/3,
                  x + note_size/2, y + note_size/3,
                  fill=0, stroke=1)


def draw_stem(c, x, y, up=True):
    """
    Dessine la hampe d'une note.

    Args:
        c: Canvas
        x, y: Position de la tête de note
        up: Si True, hampe vers le haut, sinon vers le bas
    """
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)

    stem_length = 20 * mm
    if up:
        c.line(x + 2.5*mm, y, x + 2.5*mm, y + stem_length)
    else:
        c.line(x - 2.5*mm, y, x - 2.5*mm, y - stem_length)


def draw_flag(c, x, y, duration, up=True):
    """
    Dessine le crochet pour les croches et double-croches.

    Args:
        c: Canvas
        x, y: Position
        duration: Type de durée
        up: Direction de la hampe
    """
    if duration not in ['eighth', 'sixteenth']:
        return

    c.setStrokeColor(colors.black)
    c.setLineWidth(2)

    if up:
        stem_top = y + 20*mm
        # Dessiner un crochet simplifié
        c.line(x + 2.5*mm, stem_top, x + 5*mm, stem_top - 5*mm)
        if duration == 'sixteenth':
            c.line(x + 2.5*mm, stem_top - 3*mm, x + 5*mm, stem_top - 8*mm)
    else:
        stem_bottom = y - 20*mm
        c.line(x - 2.5*mm, stem_bottom, x - 5*mm, stem_bottom + 5*mm)
        if duration == 'sixteenth':
            c.line(x - 2.5*mm, stem_bottom + 3*mm, x - 5*mm, stem_bottom + 8*mm)


def draw_hole_number(c, x, y, hole_number):
    """
    Dessine le numéro de trou sur/dans la note.

    Args:
        c: Canvas
        x, y: Position
        hole_number: Numéro du trou (1-10)
    """
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)

    # Centrer le numéro dans la note
    text_width = c.stringWidth(str(hole_number), "Helvetica-Bold", 10)
    c.drawString(x - text_width/2, y - 3*mm, str(hole_number))


def generate_tablature_pdf(tablature, output_path, tonality='C', notation_style='arrows', original_file=None, use_lilypond=True):
    """
    Génère un PDF avec tablature à 2 lignes (soufflé/aspiré) avec notation musicale.

    Méthode 1 (recommandée) : LilyPond - Partition professionnelle
    Méthode 2 (fallback) : ReportLab - Tablature basique

    Args:
        tablature (list): Liste de dictionnaires représentant les notes
        output_path (str): Chemin de sortie du PDF
        tonality (str): Tonalité de l'harmonica
        notation_style (str): Style de notation utilisé
        original_file (str): Chemin vers la partition originale (optionnel)
        use_lilypond (bool): Utiliser LilyPond si disponible (recommandé)

    Returns:
        str: Chemin du fichier généré
    """
    # Essayer LilyPond d'abord si demandé
    if use_lilypond:
        try:
            from modules.lilypond_generator import generate_lilypond_pdf, check_lilypond_installed

            if check_lilypond_installed():
                print("🎼 Génération avec LilyPond (partition professionnelle)...")

                # Extraire titre et compositeur si disponibles
                title = ''
                composer = ''
                if tablature:
                    # Chercher dans les métadonnées
                    for item in tablature:
                        if 'title' in item:
                            title = item['title']
                        if 'composer' in item:
                            composer = item['composer']

                # Extraire les accords
                chords = []
                seen_measures = set()
                for item in tablature:
                    measure = item['measure']
                    chord = item.get('chord')
                    if chord and measure not in seen_measures:
                        chords.append((measure, chord))
                        seen_measures.add(measure)

                # Générer avec LilyPond
                generated_path = generate_lilypond_pdf(
                    tablature,
                    output_path,
                    tonality=tonality,
                    title=title or 'Tablature Harmonica',
                    composer=composer or '',
                    chords=chords if chords else None
                )

                if generated_path:
                    print(f"✓ PDF LilyPond généré : {generated_path}")
                    return generated_path
                else:
                    print("⚠ Échec LilyPond, fallback sur ReportLab...")

            else:
                print("ℹ LilyPond non installé, utilisation de ReportLab")
                print("  Pour des partitions professionnelles, installez LilyPond :")
                print("  ./install_lilypond.sh")

        except Exception as e:
            print(f"⚠ Erreur LilyPond : {e}")
            print("  Fallback sur ReportLab...")

    # Fallback : ReportLab (méthode originale)
    print("📄 Génération avec ReportLab (tablature basique)...")
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Marges
    margin_left = 2*cm
    margin_top = height - 2*cm
    margin_bottom = 2*cm

    y_position = margin_top

    # ===== TITRE =====
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor('#0066cc'))
    title = "Tablature d'Harmonica"
    c.drawCentredString(width/2, y_position, title)

    y_position -= 1*cm

    # Informations
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    info = f"Tonalité : {tonality} | Date : {datetime.now().strftime('%d/%m/%Y')}"
    c.drawCentredString(width/2, y_position, info)

    y_position -= 1.5*cm

    # ===== PARTITION ORIGINALE (si disponible) =====
    if original_file and os.path.exists(original_file):
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(margin_left, y_position, "Partition originale :")
        y_position -= 0.5*cm

        # Dessiner un cadre pour indiquer où serait la partition
        box_height = 8*cm
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        c.rect(margin_left, y_position - box_height, width - 4*cm, box_height, fill=0)

        # Essayer d'inclure l'image de la partition
        try:
            if original_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                c.drawImage(original_file, margin_left, y_position - box_height,
                           width - 4*cm, box_height, preserveAspectRatio=True)
        except:
            c.setFont("Helvetica-Italic", 10)
            c.setFillColor(colors.grey)
            c.drawCentredString(width/2, y_position - box_height/2,
                              "(Partition originale ici)")

        y_position -= box_height + 1*cm

    # ===== LÉGENDE =====
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor('#0066cc'))
    c.drawString(margin_left, y_position, "Légende :")
    y_position -= 0.5*cm

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(margin_left, y_position, "• Ligne du haut = Notes SOUFFLÉES (↑)")
    y_position -= 0.4*cm
    c.drawString(margin_left, y_position, "• Ligne du bas = Notes ASPIRÉES (↓)")
    y_position -= 0.4*cm
    c.drawString(margin_left, y_position, "• Les chiffres indiquent le numéro du trou (1-10)")
    y_position -= 0.4*cm
    c.drawString(margin_left, y_position, "• La forme des notes indique la durée (ronde, blanche, noire, croche)")

    y_position -= 1.5*cm

    # ===== TABLATURE À 2 LIGNES =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor('#0066cc'))
    c.drawString(margin_left, y_position, "Tablature :")
    y_position -= 0.8*cm

    # Séparer les notes par mesure et récupérer les accords
    measures = {}
    measure_chords = {}  # Accords par mesure
    for note in tablature:
        measure_num = note['measure']
        if measure_num not in measures:
            measures[measure_num] = {'blow': [], 'draw': []}

        if note['action'] == 'blow':
            measures[measure_num]['blow'].append(note)
        elif note['action'] == 'draw':
            measures[measure_num]['draw'].append(note)

        # Récupérer l'accord de cette mesure (si disponible)
        if 'chord' in note and note['chord']:
            measure_chords[measure_num] = note['chord']

    # Dessiner chaque mesure
    staff_y = y_position

    for measure_num in sorted(measures.keys()):
        if staff_y < margin_bottom + 5*cm:
            # Nouvelle page si nécessaire
            c.showPage()
            staff_y = margin_top

        # Numéro de mesure
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin_left - 1*cm, staff_y - STAFF_LINE_HEIGHT/2, f"M{measure_num}")

        # ACCORD au-dessus de la mesure (si disponible)
        if measure_num in measure_chords:
            chord_name = measure_chords[measure_num]
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.HexColor('#CC0066'))  # Rose/magenta
            c.drawString(margin_left, staff_y + 1.2*cm, chord_name)

        # Dessiner les 2 lignes de portée
        staff_width = min(MEASURE_WIDTH, width - margin_left - 2*cm)
        draw_staff_lines(c, margin_left, staff_y, staff_width, num_lines=2)

        # Ligne supérieure : notes soufflées
        blow_notes = measures[measure_num]['blow']
        x_pos = margin_left + 0.5*cm

        for note in blow_notes:
            duration = note['duration']
            hole = note['hole']

            if hole > 0:  # Ignorer les notes non trouvées
                # Dessiner la note sur la ligne du haut
                note_y = staff_y
                draw_note_head(c, x_pos, note_y, duration)

                # Hampe vers le haut
                if duration not in ['whole']:
                    draw_stem(c, x_pos, note_y, up=True)
                    draw_flag(c, x_pos, note_y, duration, up=True)

                # Numéro de trou
                draw_hole_number(c, x_pos, note_y, hole)

                x_pos += NOTE_WIDTH

        # Ligne inférieure : notes aspirées
        draw_notes = measures[measure_num]['draw']
        x_pos = margin_left + 0.5*cm

        for note in draw_notes:
            duration = note['duration']
            hole = note['hole']

            if hole > 0:
                # Dessiner la note sur la ligne du bas
                note_y = staff_y - STAFF_LINE_HEIGHT
                draw_note_head(c, x_pos, note_y, duration)

                # Hampe vers le bas
                if duration not in ['whole']:
                    draw_stem(c, x_pos, note_y, up=False)
                    draw_flag(c, x_pos, note_y, duration, up=False)

                # Numéro de trou
                draw_hole_number(c, x_pos, note_y, hole)

                x_pos += NOTE_WIDTH

        # Barre de mesure
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.5)
        c.line(margin_left + staff_width, staff_y + 0.5*cm,
               margin_left + staff_width, staff_y - STAFF_LINE_HEIGHT - 0.5*cm)

        staff_y -= 3*cm  # Espace avant la mesure suivante

    # ===== FOOTER =====
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    footer_text = "Généré par HarpoTab - Convertisseur Partition → Tablature Harmonica"
    c.drawCentredString(width/2, 1*cm, footer_text)

    # Sauvegarder le PDF
    c.save()

    return output_path


def _get_duration_symbol(duration):
    """Retourne le symbole Unicode pour la durée."""
    symbols = {
        'whole': '𝅝',      # Ronde
        'half': '𝅗𝅥',       # Blanche
        'quarter': '♩',    # Noire
        'eighth': '♪',     # Croche
        'sixteenth': '𝅘𝅥𝅯'  # Double-croche
    }
    return symbols.get(duration, '♩')


def create_harmonica_diagram_pdf(output_path, harmonica_type='diatonic', tonality='C'):
    """
    Génère un PDF avec le diagramme de l'harmonica.

    Args:
        output_path (str): Chemin de sortie
        harmonica_type (str): Type d'harmonica
        tonality (str): Tonalité

    Returns:
        str: Chemin du fichier généré
    """
    from modules.harmonica import get_harmonica_diagram

    diagram = get_harmonica_diagram(harmonica_type, tonality)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y_position = height - 3*cm

    # Titre
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, y_position,
                        f"Diagramme Harmonica {harmonica_type.title()} - Tonalité {tonality}")

    y_position -= 2*cm

    # Dessiner le diagramme
    hole_width = 4*cm
    x_start = 2*cm

    # En-têtes
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_start, y_position, "Trou")
    c.drawString(x_start + 2*cm, y_position, "Soufflé ↑")
    c.drawString(x_start + 6*cm, y_position, "Aspiré ↓")

    y_position -= 0.5*cm
    c.setLineWidth(1)
    c.line(x_start, y_position, x_start + 10*cm, y_position)
    y_position -= 0.5*cm

    # Données
    c.setFont("Helvetica", 10)
    for hole in sorted(diagram['holes'].keys()):
        blow = diagram['holes'][hole].get('blow', '-')
        draw = diagram['holes'][hole].get('draw', '-')

        c.drawString(x_start + 0.5*cm, y_position, str(hole))
        c.drawString(x_start + 2*cm, y_position, blow)
        c.drawString(x_start + 6*cm, y_position, draw)

        y_position -= 0.6*cm

    c.save()
    return output_path
