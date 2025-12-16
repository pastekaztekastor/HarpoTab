"""
Module de génération de partitions avec Lilypond
"""
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LilypondGenerator:
    """Génère des partitions PDF avec Lilypond"""

    def __init__(self, lilypond_path: str = 'lilypond'):
        """
        Initialise le générateur

        Args:
            lilypond_path: Chemin vers l'exécutable lilypond
        """
        self.lilypond_path = lilypond_path
        self._check_lilypond()

    def _check_lilypond(self) -> bool:
        """Vérifie que Lilypond est installé"""
        try:
            result = subprocess.run(
                [self.lilypond_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            logger.info(f"Lilypond trouvé: {result.stdout.split()[0:3]}")
            return True
        except Exception as e:
            logger.warning(f"Lilypond non trouvé: {e}")
            return False

    def generate_score(
        self,
        melody: List[Dict[str, Any]],
        tabs: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        output_path: Path
    ) -> bool:
        """
        Génère une partition complète (mélodie + tablature)

        Args:
            melody: Mélodie en notation standard
            tabs: Tablature harmonica
            metadata: Métadonnées (titre, tonalité, etc.)
            output_path: Chemin du PDF de sortie

        Returns:
            True si succès, False sinon
        """
        logger.info(f"Génération de la partition: {output_path}")

        # Créer le fichier .ly
        ly_content = self._create_lilypond_file(melody, tabs, metadata)

        ly_file = output_path.with_suffix('.ly')
        with open(ly_file, 'w', encoding='utf-8') as f:
            f.write(ly_content)

        # Compiler avec Lilypond
        success = self._compile_lilypond(ly_file, output_path.parent)

        return success

    def _create_lilypond_file(
        self,
        melody: List[Dict[str, Any]],
        tabs: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Crée le contenu du fichier Lilypond

        Args:
            melody: Notes de la mélodie
            tabs: Tablature
            metadata: Informations du morceau

        Returns:
            Contenu du fichier .ly
        """
        # Formater les notes et la tablature
        melody_notes = self._format_melody(melody)
        tablature_lyrics = self._format_tablature(tabs)

        # Extraire les métadonnées
        title = metadata.get('title', 'Sans titre')
        composer = metadata.get('composer', '')
        key = metadata.get('key', 'C').lower() if metadata.get('key') else 'c'
        time_sig = metadata.get('time_signature', '4/4')
        tempo = metadata.get('tempo') or 120  # Gérer None
        harmonica_type = metadata.get('harmonica_type', 'diatonic')
        harmonica_key = metadata.get('harmonica_key', 'C')
        transposition = metadata.get('transposition', 0)

        # Construire le fichier Lilypond
        ly_content = f'''\\version "2.24.0"

\\header {{
  title = "{title}"
  composer = "{composer}"
  subtitle = "Harmonica {harmonica_type.capitalize()} en {harmonica_key}"
  tagline = "Généré par HarpoTab - https://github.com/mathurinc/harpotab"
}}

\\paper {{
  #(set-paper-size "a4")
}}

melody = {{
  \\key {key} \\major
  \\time {time_sig}
  \\tempo 4 = {tempo}

  {melody_notes}
}}

harmonicaTabs = \\lyricmode {{
  {tablature_lyrics}
}}

\\score {{
  \\new Staff = "melody" <<
    \\new Voice = "melodySinger" {{
      \\melody
    }}
    \\new Lyrics \\lyricsto "melodySinger" {{
      \\harmonicaTabs
    }}
  >>
  \\layout {{
    \\context {{
      \\Lyrics
      \\override LyricText.font-name = "monospace"
      \\override LyricText.font-size = #-1
    }}
  }}
  \\midi {{ }}
}}
'''

        if transposition != 0:
            transp_text = f"Transposé de {transposition:+d} demi-tons"
            if abs(transposition) >= 7:
                transp_text += " (importante transposition)"
            ly_content = ly_content.replace(
                '\\header {',
                f'\\header {{\n  instrument = "{transp_text}"'
            )

        return ly_content

    def _get_lilypond_template(self) -> str:
        """Retourne le template de base Lilypond"""
        return '''\\version "2.24.0"

\\header {
  title = "{{ title }}"
  composer = "{{ composer }}"
  tagline = "Généré par HarpoTab"
}

melody = \\relative c' {
  \\key {{ key }} \\major
  \\time {{ time_signature }}
  \\tempo {{ tempo }}

  {{ melody_notes }}
}

harmonicaTabs = \\lyricmode {
  {{ tablature }}
}

\\score {
  <<
    \\new Staff {
      \\melody
    }
    \\new Lyrics \\lyricsto "melody" {
      \\harmonicaTabs
    }
  >>
  \\layout { }
}
'''

    def _compile_lilypond(self, ly_file: Path, output_dir: Path) -> bool:
        """
        Compile un fichier .ly en PDF

        Args:
            ly_file: Fichier source .ly
            output_dir: Dossier de sortie

        Returns:
            True si succès
        """
        try:
            result = subprocess.run(
                [
                    self.lilypond_path,
                    '--output', str(output_dir),
                    str(ly_file)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("Compilation Lilypond réussie")
                return True
            else:
                logger.error(f"Erreur Lilypond: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Échec compilation Lilypond: {e}")
            return False

    def _format_melody(self, melody: List[Dict[str, Any]]) -> str:
        """Formate la mélodie en syntaxe Lilypond"""
        notes = []

        for note in melody:
            # Gérer les silences
            if note.get('type') == 'rest':
                duration = self._convert_duration_to_lilypond(note)
                notes.append(f"r{duration}")
                continue

            # Convertir la note en notation Lilypond
            pitch = note.get('pitch', 'C')
            octave = note.get('octave', 4)
            duration = self._convert_duration_to_lilypond(note)
            alter = note.get('alter', 0)

            # Gérer les altérations déjà présentes dans le nom de la note (ex: Bb, C#)
            if 'b' in pitch and len(pitch) > 1:  # Bémol déjà dans le nom
                # Ex: "Bb" -> "bes", "Eb" -> "es", "Ab" -> "as"
                base_note = pitch[0].lower()
                if base_note == 'b':
                    pitch = 'bes'
                elif base_note == 'e':
                    pitch = 'es'
                elif base_note == 'a':
                    pitch = 'as'
                else:
                    pitch = base_note + 'es'
            elif '#' in pitch:  # Dièse déjà dans le nom
                # Ex: "C#" -> "cis", "F#" -> "fis"
                base_note = pitch[0].lower()
                pitch = base_note + 'is'
            else:
                # Note simple, convertir en minuscule
                pitch = pitch.lower()

                # Appliquer les altérations si présentes via 'alter'
                if alter == 1:
                    pitch += 'is'  # dièse
                elif alter == -1:
                    # Pour les bémols en Lilypond
                    if pitch == 'b':
                        pitch = 'bes'
                    elif pitch == 'e':
                        pitch = 'es'
                    elif pitch == 'a':
                        pitch = 'as'
                    else:
                        pitch += 'es'

            # Gestion des octaves en mode absolu (Lilypond: c = C3, c' = C4, c'' = C5)
            octave_mark = ''
            if octave > 3:
                octave_mark = "'" * (octave - 3)
            elif octave < 3:
                octave_mark = "," * (3 - octave)
            # Si octave == 3, pas de marque (c = C3)

            # Assembler la note
            note_str = f"{pitch}{octave_mark}{duration}"
            notes.append(note_str)

        return ' '.join(notes)

    def _convert_duration_to_lilypond(self, note: Dict[str, Any]) -> int:
        """
        Convertit la durée de note en notation Lilypond

        Args:
            note: Dictionnaire contenant 'note_type' ou 'duration'

        Returns:
            Durée Lilypond: 1 (ronde), 2 (blanche), 4 (noire), 8 (croche), 16 (double croche)
        """
        note_type = note.get('note_type', '')

        # Mapping des types MusicXML vers Lilypond
        type_mapping = {
            'whole': 1,
            'half': 2,
            'quarter': 4,
            'eighth': 8,
            '16th': 16,
            'sixteenth': 16,
            '32nd': 32,
            'thirty-second': 32
        }

        if note_type in type_mapping:
            return type_mapping[note_type]

        # Fallback: utiliser duration (ancienne méthode)
        # Supposer divisions=2 pour convertir
        duration = note.get('duration', 2)
        if duration >= 8:
            return 1  # ronde
        elif duration >= 4:
            return 2  # blanche
        elif duration >= 2:
            return 4  # noire
        elif duration >= 1:
            return 8  # croche
        else:
            return 16  # double croche

    def _format_tablature(self, tabs: List[Dict[str, Any]]) -> str:
        """Formate la tablature en lyrics Lilypond"""
        lyrics = []

        for tab in tabs:
            # Gérer les silences
            if tab.get('type') == 'rest':
                lyrics.append('_')
                continue

            hole = tab.get('hole', '?')
            direction = tab.get('direction', 'blow')
            technique = tab.get('technique')

            # Symboles pour direction (utiliser des lettres ASCII pour Lilypond)
            if direction == 'blow':
                arrow = 'B'  # Blow
            elif direction == 'draw':
                arrow = 'D'  # Draw
            else:
                arrow = '.'

            # Construire le texte de la tablature
            tab_text = f'"{hole}{arrow}'

            # Ajouter indication de technique si nécessaire
            if technique:
                if technique == 'overblow':
                    tab_text += ' ob'
                elif technique == 'overdraw':
                    tab_text += ' od'
                elif 'bend' in technique:
                    # Notation bend plus visible avec des symboles
                    if 'full_half' in technique:
                        tab_text += '↓↓↓'  # Bend 1.5 tons
                    elif 'full' in technique:
                        tab_text += '↓↓'   # Bend 1 ton
                    elif 'half' in technique:
                        tab_text += '↓'     # Bend 1/2 ton

            tab_text += '"'
            lyrics.append(tab_text)

        return ' '.join(lyrics)


def generate_pdf(
    melody: List[Dict[str, Any]],
    tabs: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_path: Path
) -> bool:
    """
    Fonction helper pour générer un PDF

    Args:
        melody: Mélodie
        tabs: Tablature
        metadata: Métadonnées
        output_path: Chemin de sortie

    Returns:
        True si succès
    """
    generator = LilypondGenerator()
    return generator.generate_score(melody, tabs, metadata, output_path)
