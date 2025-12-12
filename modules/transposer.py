"""
Module de transposition automatique pour adaptation à l'harmonica

Ce module permet de transposer une mélodie pour la rendre jouable sur un harmonica donné,
en trouvant automatiquement la meilleure transposition possible.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class Transposer:
    """Gère la transposition pour adaptation harmonica"""

    # Correspondance notes → demi-tons
    NOTE_TO_SEMITONES = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    SEMITONES_TO_NOTE = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F',
        6: 'F#', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'
    }

    def __init__(self):
        """Initialise le transposeur"""
        pass

    def transpose_melody(
        self,
        melody: List[Dict[str, Any]],
        semitones: int
    ) -> List[Dict[str, Any]]:
        """
        Transpose une mélodie d'un nombre de demi-tons

        Args:
            melody: Mélodie originale (dictionnaire retourné par melody_extractor)
            semitones: Nombre de demi-tons (+ monte, - descend)

        Returns:
            Mélodie transposée
        """
        if semitones == 0:
            logger.info("Aucune transposition nécessaire (0 demi-tons)")
            return melody.copy()

        logger.info(f"Transposition de {semitones} demi-tons ({self.get_transposition_info(semitones)})")

        # Si melody est un dict avec 'notes', extraire les notes
        notes_list = melody.get('notes', melody) if isinstance(melody, dict) else melody

        transposed_notes = []
        for note in notes_list:
            transposed_note = self._transpose_note(note, semitones)
            transposed_notes.append(transposed_note)

        # Si c'était un dict, reconstruire la structure
        if isinstance(melody, dict) and 'notes' in melody:
            result = melody.copy()
            result['notes'] = transposed_notes
            return result
        else:
            return transposed_notes

    def _transpose_note(self, note: Dict[str, Any], semitones: int) -> Dict[str, Any]:
        """
        Transpose une note individuelle

        Args:
            note: Note à transposer
            semitones: Nombre de demi-tons

        Returns:
            Note transposée
        """
        transposed = note.copy()

        # Les silences ne sont pas transposés
        if note['type'] == 'rest':
            return transposed

        # Transposer le MIDI
        if 'midi' in note:
            transposed['midi'] = note['midi'] + semitones

        # Recalculer pitch et octave depuis le nouveau MIDI
        if 'midi' in transposed:
            new_pitch, new_octave = self._midi_to_note(transposed['midi'])
            transposed['pitch'] = new_pitch
            transposed['octave'] = new_octave
            transposed['alter'] = 0  # Reset alter car nouvelle note

        return transposed

    def _midi_to_note(self, midi: int) -> Tuple[str, int]:
        """
        Convertit un numéro MIDI en (note, octave)

        Args:
            midi: Numéro MIDI (C4 = 60)

        Returns:
            Tuple (note, octave)
        """
        octave = (midi // 12) - 1
        semitone = midi % 12
        note = self.SEMITONES_TO_NOTE[semitone]
        return note, octave

    def check_playability(
        self,
        melody_data: Dict[str, Any],
        harmonica_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Vérifie si une mélodie est jouable sur un harmonica donné

        Args:
            melody_data: Données de mélodie (dict avec 'notes')
            harmonica_map: Mapping notes → trous de l'harmonica

        Returns:
            Dict {
                'playable': bool,
                'coverage': float (0-1),
                'playable_notes': int,
                'total_notes': int,
                'missing_notes': List[str]
            }
        """
        # Extraire la liste des notes
        notes_list = melody_data.get('notes', melody_data) if isinstance(melody_data, dict) else melody_data

        # Construire l'ensemble des notes jouables sur l'harmonica
        playable_set = set()
        for hole_data in harmonica_map.get('notes', {}).values():
            for action, note_info in hole_data.items():
                if isinstance(note_info, dict) and 'note' in note_info and 'octave' in note_info:
                    note_name = f"{note_info['note']}{note_info['octave']}"
                    playable_set.add(note_name)

        # Vérifier chaque note de la mélodie
        total_notes = 0
        playable_notes = 0
        missing_notes = set()

        for note in notes_list:
            if note['type'] == 'rest':
                continue

            total_notes += 1
            note_name = f"{note['pitch']}{note['octave']}"

            if note_name in playable_set:
                playable_notes += 1
            else:
                missing_notes.add(note_name)

        coverage = playable_notes / total_notes if total_notes > 0 else 0
        playable = coverage == 1.0

        result = {
            'playable': playable,
            'coverage': coverage,
            'playable_notes': playable_notes,
            'total_notes': total_notes,
            'missing_notes': sorted(list(missing_notes))
        }

        if playable:
            logger.info(f"✅ Mélodie jouable à 100% ({playable_notes}/{total_notes} notes)")
        else:
            logger.info(f"⚠️ Mélodie jouable à {coverage*100:.1f}% ({playable_notes}/{total_notes} notes)")
            logger.info(f"Notes manquantes: {result['missing_notes']}")

        return result

    def find_best_transposition(
        self,
        melody_data: Dict[str, Any],
        harmonica_map: Dict[str, Any],
        min_semitones: int = -12,
        max_semitones: int = 12
    ) -> Optional[Tuple[int, Dict[str, Any]]]:
        """
        Trouve la meilleure transposition pour un harmonica donné

        Args:
            melody_data: Mélodie originale
            harmonica_map: Mapping de l'harmonica
            min_semitones: Transposition minimale à tester
            max_semitones: Transposition maximale à tester

        Returns:
            Tuple (semitones, playability_info) ou None si aucune transposition valide
        """
        logger.info(f"Recherche de la meilleure transposition ({min_semitones} à {max_semitones} demi-tons)")

        best_semitones = None
        best_coverage = 0
        best_playability = None

        # Tester chaque transposition possible
        for semitones in range(min_semitones, max_semitones + 1):
            # Transposer la mélodie
            transposed = self.transpose_melody(melody_data, semitones)

            # Vérifier la jouabilité
            playability = self.check_playability(transposed, harmonica_map)

            # Si jouable à 100%, on a trouvé une solution
            if playability['playable']:
                logger.info(f"✅ Transposition trouvée: {semitones} demi-tons ({self.get_transposition_info(semitones)})")
                return semitones, playability

            # Sinon, garder la meilleure couverture
            if playability['coverage'] > best_coverage:
                best_coverage = playability['coverage']
                best_semitones = semitones
                best_playability = playability

        # Si aucune solution parfaite, retourner la meilleure couverture
        if best_semitones is not None and best_coverage >= 0.8:  # Seuil de 80%
            logger.warning(f"⚠️ Aucune transposition parfaite trouvée. "
                         f"Meilleure option: {best_semitones} demi-tons ({best_coverage*100:.1f}% de couverture)")
            return best_semitones, best_playability

        logger.error("❌ Impossible de trouver une transposition valide (couverture < 80%)")
        return None

    def get_transposition_info(self, semitones: int) -> str:
        """
        Génère une description textuelle de la transposition

        Args:
            semitones: Nombre de demi-tons

        Returns:
            Description (ex: "1.0 ton au-dessus", "2.5 tons au-dessous")
        """
        if semitones == 0:
            return "Aucune transposition"

        direction = "au-dessus" if semitones > 0 else "au-dessous"
        tones = abs(semitones) / 2

        if tones == int(tones):
            return f"{int(tones)} ton(s) {direction}"
        else:
            return f"{tones} ton(s) {direction}"

    def get_key_from_transposition(self, original_key: str, semitones: int) -> str:
        """
        Calcule la nouvelle tonalité après transposition

        Args:
            original_key: Tonalité originale (ex: "C", "G")
            semitones: Nombre de demi-tons de transposition

        Returns:
            Nouvelle tonalité
        """
        if original_key not in self.NOTE_TO_SEMITONES:
            return "Unknown"

        original_semitone = self.NOTE_TO_SEMITONES[original_key]
        new_semitone = (original_semitone + semitones) % 12

        return self.SEMITONES_TO_NOTE[new_semitone]


def transpose_for_harmonica(
    melody_data: Dict[str, Any],
    harmonica_map: Dict[str, Any],
    force_transpose: Optional[int] = None
) -> Tuple[Dict[str, Any], int, Dict[str, Any]]:
    """
    Fonction helper pour transposer une mélodie automatiquement

    Args:
        melody_data: Mélodie extraite (par melody_extractor)
        harmonica_map: Mapping de l'harmonica cible
        force_transpose: Si spécifié, force cette transposition (en demi-tons)

    Returns:
        Tuple (melody_transposée, semitones_utilisés, playability_info)

    Raises:
        ValueError: Si impossible de rendre la mélodie jouable
    """
    transposer = Transposer()

    # Si transposition forcée
    if force_transpose is not None:
        logger.info(f"Transposition forcée: {force_transpose} demi-tons")
        transposed = transposer.transpose_melody(melody_data, force_transpose)
        playability = transposer.check_playability(transposed, harmonica_map)
        return transposed, force_transpose, playability

    # Vérifier jouabilité sans transposition
    logger.info("Vérification de la jouabilité sans transposition...")
    playability = transposer.check_playability(melody_data, harmonica_map)

    if playability['playable']:
        logger.info("✅ Mélodie jouable sans transposition")
        return melody_data, 0, playability

    # Chercher la meilleure transposition
    logger.info("Mélodie non jouable, recherche d'une transposition...")
    result = transposer.find_best_transposition(melody_data, harmonica_map)

    if result is None:
        raise ValueError(
            "Impossible de rendre ce morceau jouable sur cet harmonica. "
            "Essayez un harmonica dans une autre tonalité."
        )

    semitones, playability = result
    transposed_melody = transposer.transpose_melody(melody_data, semitones)

    return transposed_melody, semitones, playability
