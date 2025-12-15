"""
Module d'extraction de mélodie depuis des données MusicXML

Ce module prend les données structurées retournées par ocr_reader et extrait
la mélodie principale jouable à l'harmonica.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MelodyExtractor:
    """Extracteur de mélodie principale depuis MusicXML"""

    def __init__(self, keep_rests: bool = True, simplify_chords: bool = True):
        """
        Initialise l'extracteur de mélodie

        Args:
            keep_rests: Garder les silences dans la mélodie extraite
            simplify_chords: Simplifier les accords en prenant la note la plus haute
        """
        self.keep_rests = keep_rests
        self.simplify_chords = simplify_chords

    def extract_melody(self, musicxml_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extrait la mélodie principale depuis les données MusicXML

        Args:
            musicxml_data: Données structurées retournées par AudiverisOCR.parse_musicxml()

        Returns:
            Dictionnaire contenant la mélodie extraite et les métadonnées
        """
        if not musicxml_data or 'parts' not in musicxml_data:
            logger.error("Données MusicXML invalides")
            return None

        parts = musicxml_data['parts']
        if not parts:
            logger.error("Aucune partie musicale trouvée")
            return None

        # Sélectionner la partie principale
        main_part = self._select_main_part(parts)
        logger.info(f"Partie principale sélectionnée: {main_part['id']}")

        # Extraire toutes les notes de la partie
        melody_notes = self._extract_notes_from_part(main_part)

        # Récupérer les métadonnées complètes
        metadata = musicxml_data.get('metadata', {})

        result = {
            'notes': melody_notes,
            'metadata': metadata,
            'source_file': musicxml_data.get('source_file'),
            'part_id': main_part['id'],
            'total_measures': len(main_part['measures']),
            # Ajouter time_signature et tempo au niveau racine pour faciliter l'accès
            'time_signature': metadata.get('time_signature', '4/4'),
            'tempo': metadata.get('tempo', 120),
            'key': metadata.get('key'),
            'composer': metadata.get('composer'),
            'title': metadata.get('title')
        }

        logger.info(f"Mélodie extraite: {len(melody_notes)} notes/événements")
        return result

    def _select_main_part(self, parts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sélectionne la partie contenant la mélodie principale

        Pour une partition simple (1 partie), retourne cette partie.
        Pour une partition multi-parties, choisit selon plusieurs critères:
        - La partie avec le plus de notes
        - La tessiture (notes les plus hautes en moyenne)

        Args:
            parts: Liste des parties musicales

        Returns:
            La partie sélectionnée comme mélodie principale
        """
        if len(parts) == 1:
            return parts[0]

        # Analyser chaque partie
        part_scores = []
        for part in parts:
            total_notes = sum(len(m['notes']) for m in part['measures'])
            avg_pitch = self._calculate_average_pitch(part)

            score = {
                'part': part,
                'total_notes': total_notes,
                'avg_pitch': avg_pitch,
                # Score combiné: priorité aux notes nombreuses et tessiture haute
                'combined_score': total_notes + (avg_pitch * 10)
            }
            part_scores.append(score)

        # Trier par score combiné et prendre la meilleure
        part_scores.sort(key=lambda x: x['combined_score'], reverse=True)
        selected = part_scores[0]['part']

        logger.info(f"Partie {selected['id']} sélectionnée "
                   f"({part_scores[0]['total_notes']} notes, "
                   f"hauteur moyenne: {part_scores[0]['avg_pitch']:.1f})")

        return selected

    def _calculate_average_pitch(self, part: Dict[str, Any]) -> float:
        """
        Calcule la hauteur moyenne des notes d'une partie

        Args:
            part: Partie musicale

        Returns:
            Hauteur moyenne en notation MIDI (C4 = 60)
        """
        pitches = []

        for measure in part['measures']:
            for note in measure['notes']:
                if note['type'] == 'note' and 'pitch' in note:
                    pitch_data = note['pitch']
                    if pitch_data.get('step') and pitch_data.get('octave') is not None:
                        midi_pitch = self._note_to_midi(
                            pitch_data['step'],
                            pitch_data['octave'],
                            pitch_data.get('alter', 0)
                        )
                        pitches.append(midi_pitch)

        return sum(pitches) / len(pitches) if pitches else 60.0

    def _note_to_midi(self, step: str, octave: int, alter: int = 0) -> int:
        """
        Convertit une note en numéro MIDI

        Args:
            step: Nom de la note (C, D, E, F, G, A, B)
            octave: Octave
            alter: Altération (-1 = bémol, 0 = naturel, 1 = dièse)

        Returns:
            Numéro MIDI (C4 = 60)
        """
        note_values = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        base_pitch = note_values.get(step.upper(), 0)
        midi = (octave + 1) * 12 + base_pitch + alter
        return midi

    def _extract_notes_from_part(self, part: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait toutes les notes d'une partie musicale

        Args:
            part: Partie musicale

        Returns:
            Liste de notes simplifiées
        """
        melody_notes = []
        current_time = 0

        for measure in part['measures']:
            measure_num = measure['number']
            measure_notes = measure['notes']

            # Traiter chaque note de la mesure
            for note in measure_notes:
                # Traiter l'événement (note ou silence)
                if note['type'] == 'rest':
                    if self.keep_rests:
                        melody_notes.append({
                            'type': 'rest',
                            'duration': note.get('duration'),
                            'note_type': note.get('note_type'),
                            'measure': measure_num,
                            'time': current_time
                        })
                else:
                    # Note
                    if 'pitch' in note:
                        pitch_data = note['pitch']
                        melody_notes.append({
                            'type': 'note',
                            'pitch': pitch_data.get('step'),
                            'octave': pitch_data.get('octave'),
                            'alter': pitch_data.get('alter', 0),
                            'duration': note.get('duration'),
                            'note_type': note.get('note_type'),
                            'measure': measure_num,
                            'time': current_time,
                            'midi': self._note_to_midi(
                                pitch_data.get('step', 'C'),
                                pitch_data.get('octave', 4),
                                pitch_data.get('alter', 0)
                            )
                        })

                # Avancer le temps
                if note.get('duration'):
                    current_time += note['duration']

        return melody_notes

    def _select_highest_note(self, chord_notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sélectionne la note la plus haute d'un accord

        Args:
            chord_notes: Liste de notes formant un accord

        Returns:
            La note la plus haute
        """
        notes_with_pitch = [n for n in chord_notes if 'pitch' in n]

        if not notes_with_pitch:
            return chord_notes[0]

        highest = notes_with_pitch[0]
        highest_midi = self._note_to_midi(
            highest['pitch'].get('step', 'C'),
            highest['pitch'].get('octave', 4),
            highest['pitch'].get('alter', 0)
        )

        for note in notes_with_pitch[1:]:
            pitch = note['pitch']
            midi = self._note_to_midi(
                pitch.get('step', 'C'),
                pitch.get('octave', 4),
                pitch.get('alter', 0)
            )
            if midi > highest_midi:
                highest = note
                highest_midi = midi

        return highest

    def get_note_name(self, note: Dict[str, Any]) -> str:
        """
        Retourne le nom complet d'une note

        Args:
            note: Note extraite

        Returns:
            Nom de la note (ex: "C4", "F#3", "Bb4")
        """
        if note['type'] == 'rest':
            return f"Rest({note.get('note_type', '?')})"

        pitch = note['pitch']
        alter = note.get('alter', 0)
        alter_symbol = {-1: 'b', 0: '', 1: '#'}.get(alter, f'({alter})')

        return f"{pitch}{alter_symbol}{note['octave']}"


def extract_melody_from_musicxml(musicxml_data: Dict[str, Any],
                                 keep_rests: bool = True,
                                 simplify_chords: bool = True) -> Optional[Dict[str, Any]]:
    """
    Fonction helper pour extraire la mélodie depuis des données MusicXML

    Args:
        musicxml_data: Données MusicXML parsées par ocr_reader
        keep_rests: Garder les silences
        simplify_chords: Simplifier les accords

    Returns:
        Mélodie extraite
    """
    extractor = MelodyExtractor(keep_rests=keep_rests, simplify_chords=simplify_chords)
    return extractor.extract_melody(musicxml_data)
