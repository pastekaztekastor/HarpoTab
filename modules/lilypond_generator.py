"""
Module de génération de partitions avec LilyPond.

LilyPond est le standard professionnel pour la notation musicale.
Il existe des extensions spécifiques pour harmonica diatonique.

Ce module génère du code LilyPond (.ly) puis le compile en PDF.
"""

import subprocess
import os
import tempfile


class LilyPondGenerator:
    """Générateur de code LilyPond pour harmonica."""

    def __init__(self, tonality='C', title='', composer=''):
        """
        Initialise le générateur.

        Args:
            tonality (str): Tonalité de l'harmonica (C, G, A, D, etc.)
            title (str): Titre de la pièce
            composer (str): Compositeur
        """
        self.tonality = tonality
        self.title = title
        self.composer = composer

    def note_to_lilypond(self, note_name, duration='4'):
        """
        Convertit une note en notation LilyPond.

        Args:
            note_name (str): Note (ex: 'C4', 'D#5', 'Bb3')
            duration (str): Durée LilyPond (1=ronde, 2=blanche, 4=noire, 8=croche)

        Returns:
            str: Note en notation LilyPond (ex: 'c4', 'd8', 'bes2')
        """
        import re

        # Parser la note
        match = re.match(r'^([A-G])([#b]?)(\d+)$', note_name)
        if not match:
            return 'r4'  # Silence si note invalide

        pitch = match.group(1).lower()
        accidental = match.group(2)
        octave = int(match.group(3))

        # Accidentals en LilyPond
        if accidental == '#':
            pitch += 'is'  # C# → cis
        elif accidental == 'b':
            if pitch == 'b':
                pitch = 'bes'  # Bb → bes
            elif pitch == 'a':
                pitch = 'aes'  # Ab → aes
            elif pitch == 'e':
                pitch = 'ees'  # Eb → ees
            elif pitch == 'd':
                pitch = 'des'  # Db → des
            elif pitch == 'g':
                pitch = 'ges'  # Gb → ges

        # Octave en LilyPond (référence = octave 3)
        # Octave 3 = pas de modificateur
        # Octave 4 = '
        # Octave 5 = ''
        # Octave 2 = ,
        # Octave 1 = ,,
        octave_markers = {
            1: ',,',
            2: ',',
            3: '',
            4: "'",
            5: "''",
            6: "'''",
        }
        octave_marker = octave_markers.get(octave, "'")

        # Duration mapping
        duration_map = {
            'whole': '1',
            'half': '2',
            'quarter': '4',
            'eighth': '8',
            'sixteenth': '16'
        }
        lily_duration = duration_map.get(duration, '4')

        return f"{pitch}{octave_marker}{lily_duration}"

    def generate_harmonica_tablature_code(self, tablature, chords=None):
        """
        Génère le code LilyPond pour tablature harmonica.

        Utilise l'extension harmonica-tab de LilyPond.

        Args:
            tablature (list): Liste de notes converties
            chords (list): Liste d'accords (optionnel)

        Returns:
            str: Code LilyPond complet
        """
        # En-tête LilyPond
        code = f'''\\version "2.24.0"

\\header {{
  title = "{self.title}"
  composer = "{self.composer}"
  tagline = "Généré par HarpoTab - LilyPond"
}}

% Configuration papier
\\paper {{
  #(set-paper-size "a4")
  top-margin = 15\\mm
  bottom-margin = 15\\mm
  left-margin = 20\\mm
  right-margin = 20\\mm
}}

% Définition des styles pour harmonica
\\layout {{
  \\context {{
    \\Voice
    \\consists "Horizontal_bracket_engraver"
  }}
}}

% Notes de la mélodie
melody = {{
  \\clef treble
  \\key c \\major
  \\time 4/4
  \\tempo 4 = 120

'''

        # Organiser les notes par mesure
        measures = {}
        for item in tablature:
            measure_num = item['measure']
            if measure_num not in measures:
                measures[measure_num] = []
            measures[measure_num].append(item)

        # Générer les notes pour chaque mesure
        for measure_num in sorted(measures.keys()):
            notes_in_measure = measures[measure_num]

            # Ajouter commentaire de mesure
            code += f"  % Mesure {measure_num}\n  "

            # Convertir chaque note
            for note_item in notes_in_measure:
                note_name = note_item['note_name']
                duration = note_item.get('duration', 'quarter')

                lily_note = self.note_to_lilypond(note_name, duration)
                code += f"{lily_note} "

            code += "\n"

        code += "}\n\n"

        # Accords (chiffrage harmonique)
        if chords:
            code += "% Accords\n"
            code += "harmony = \\chordmode {\n"

            # Organiser les accords par mesure
            chord_measures = {}
            for measure, chord in chords:
                chord_measures[measure] = chord

            for measure_num in sorted(chord_measures.keys()):
                chord_name = chord_measures[measure_num]
                # Convertir en notation LilyPond
                lily_chord = self._chord_to_lilypond(chord_name)
                code += f"  {lily_chord}1 % Mesure {measure_num}\n"

            code += "}\n\n"

        # Tablature harmonica (numéros de trou + direction)
        code += "% Tablature harmonica\n"
        code += "harmonicaTab = {\n"
        code += "  \\override TextScript.staff-padding = #2\n"
        code += "  \\override TextScript.font-size = #0\n\n"

        for measure_num in sorted(measures.keys()):
            notes_in_measure = measures[measure_num]
            code += f"  % Mesure {measure_num}\n  "

            for note_item in notes_in_measure:
                hole = note_item['hole']
                action = note_item['action']
                duration = note_item.get('duration', 'quarter')

                # Flèche pour direction
                arrow = "↑" if action == 'blow' else "↓"

                # Note invisible avec texte pour tablature
                lily_duration = {'whole': '1', 'half': '2', 'quarter': '4', 'eighth': '8'}.get(duration, '4')
                code += f's{lily_duration}^\\markup {{ \\bold "{hole}{arrow}" }} '

            code += "\n"

        code += "}\n\n"

        # Score (assemblage final)
        code += "% Score final\n"
        code += "\\score {\n"

        if chords:
            code += "  <<\n"
            code += "    \\new ChordNames \\harmony\n"
            code += "    \\new Staff {\n"
            code += "      <<\n"
            code += "        \\melody\n"
            code += "        \\harmonicaTab\n"
            code += "      >>\n"
            code += "    }\n"
            code += "  >>\n"
        else:
            code += "  \\new Staff {\n"
            code += "    <<\n"
            code += "      \\melody\n"
            code += "      \\harmonicaTab\n"
            code += "    >>\n"
            code += "  }\n"

        code += "  \\layout { }\n"
        code += "  \\midi { }\n"
        code += "}\n"

        return code

    def _chord_to_lilypond(self, chord_name):
        """
        Convertit un nom d'accord en notation LilyPond.

        Args:
            chord_name (str): Accord (ex: 'Am', 'F', 'C7', 'Gmaj7')

        Returns:
            str: Accord en notation LilyPond
        """
        import re

        # Parser l'accord
        match = re.match(r'^([A-G])([#b]?)(m|maj|dim|aug)?(\d+)?$', chord_name)
        if not match:
            return 'c'  # Défaut

        root = match.group(1).lower()
        accidental = match.group(2)
        quality = match.group(3)
        extension = match.group(4)

        # Accidental
        if accidental == '#':
            root += 'is'
        elif accidental == 'b':
            if root == 'b':
                root = 'bes'
            elif root == 'a':
                root = 'aes'
            elif root == 'e':
                root = 'ees'

        # Quality
        if quality == 'm':
            root += ':m'
        elif quality == 'maj':
            root += ':maj'
        elif quality == 'dim':
            root += ':dim'
        elif quality == 'aug':
            root += ':aug'

        # Extension
        if extension:
            root += extension

        return root

    def compile_lilypond(self, ly_code, output_path):
        """
        Compile le code LilyPond en PDF.

        Args:
            ly_code (str): Code LilyPond
            output_path (str): Chemin du PDF de sortie

        Returns:
            bool: True si succès, False sinon
        """
        # Créer un fichier temporaire .ly
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ly', delete=False) as f:
            temp_ly_path = f.name
            f.write(ly_code)

        try:
            # Compiler avec LilyPond
            output_dir = os.path.dirname(output_path)
            output_name = os.path.basename(output_path).replace('.pdf', '')

            result = subprocess.run(
                ['lilypond', '-o', os.path.join(output_dir, output_name), temp_ly_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Succès
                return True
            else:
                print(f"Erreur LilyPond : {result.stderr}")
                return False

        except FileNotFoundError:
            print("Erreur : LilyPond n'est pas installé")
            print("Installez-le avec : sudo apt-get install lilypond")
            return False

        except subprocess.TimeoutExpired:
            print("Erreur : Timeout lors de la compilation LilyPond")
            return False

        except Exception as e:
            print(f"Erreur lors de la compilation : {e}")
            return False

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_ly_path):
                os.remove(temp_ly_path)


def generate_lilypond_pdf(tablature, output_path, tonality='C', title='', composer='', chords=None):
    """
    Génère un PDF de partition avec LilyPond.

    Args:
        tablature (list): Liste de notes converties
        output_path (str): Chemin du PDF de sortie
        tonality (str): Tonalité
        title (str): Titre
        composer (str): Compositeur
        chords (list): Accords (optionnel)

    Returns:
        str: Chemin du PDF généré, ou None si échec
    """
    generator = LilyPondGenerator(tonality, title, composer)

    # Modifier le nom pour indiquer que c'est LilyPond
    # tablature_avant-toi.pdf → tablature_avant-toi_lilypond.pdf
    output_path_lily = output_path.replace('.pdf', '_lilypond.pdf')

    # Générer le code LilyPond
    ly_code = generator.generate_harmonica_tablature_code(tablature, chords)

    # Sauvegarder le code .ly (pour debug)
    ly_path = output_path_lily.replace('.pdf', '.ly')
    with open(ly_path, 'w', encoding='utf-8') as f:
        f.write(ly_code)

    print(f"Code LilyPond sauvegardé : {ly_path}")

    # Compiler en PDF
    success = generator.compile_lilypond(ly_code, output_path_lily)

    if success and os.path.exists(output_path_lily):
        return output_path_lily
    else:
        return None


def check_lilypond_installed():
    """
    Vérifie si LilyPond est installé.

    Returns:
        bool: True si installé
    """
    try:
        result = subprocess.run(['lilypond', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            # Extraire la version
            version_line = result.stdout.split('\n')[0]
            print(f"LilyPond détecté : {version_line}")
            return True
    except FileNotFoundError:
        return False

    return False
