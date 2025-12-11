"""
Module de transposition automatique pour adaptation à l'harmonica
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

    def check_playability(
        self,
        melody: List[Dict[str, Any]],
        harmonica_type: str,
        harmonica_key: str,
        harmonica_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Vérifie si une mélodie est jouable sur un harmonica donné

        Args:
            melody: Mélodie à vérifier
            harmonica_type: Type d'harmonica
            harmonica_key: Tonalité de l'harmonica
            harmonica_map: Mapping notes → trous

        Returns:
            Dict {playable: bool, issues: [...], coverage: float}
        """
        logger.info(f"Vérification jouabilité sur {harmonica_type} en {harmonica_key}")

        # TODO: Implémenter vérification
        # - Vérifier que toutes les notes sont jouables
        # - Calculer pourcentage de couverture
        # - Identifier les notes problématiques

        raise NotImplementedError("Vérification jouabilité - À implémenter")

    def find_best_transposition(
        self,
        melody: List[Dict[str, Any]],
        harmonica_type: str,
        harmonica_key: str,
        harmonica_map: Dict[str, Any]
    ) -> Optional[int]:
        """
        Trouve la meilleure transposition pour un harmonica donné

        Args:
            melody: Mélodie originale
            harmonica_type: Type d'harmonica
            harmonica_key: Tonalité harmonica
            harmonica_map: Mapping disponible

        Returns:
            Nombre de demi-tons à transposer (+ ou -) ou None si impossible
        """
        logger.info("Recherche de la meilleure transposition")

        # TODO: Algorithme de recherche
        # - Tester transpositions de -12 à +12 demi-tons
        # - Calculer score de jouabilité pour chaque
        # - Préférer les transpositions minimales
        # - Préférer les tonalités basses si option activée

        raise NotImplementedError("Recherche transposition - À implémenter")

    def transpose_melody(
        self,
        melody: List[Dict[str, Any]],
        semitones: int
    ) -> List[Dict[str, Any]]:
        """
        Transpose une mélodie d'un nombre de demi-tons

        Args:
            melody: Mélodie originale
            semitones: Nombre de demi-tons (+ monte, - descend)

        Returns:
            Mélodie transposée
        """
        logger.info(f"Transposition de {semitones} demi-tons")

        # TODO: Transposer chaque note
        transposed = []
        for note in melody:
            transposed_note = self._transpose_note(note, semitones)
            transposed.append(transposed_note)

        return transposed

    def _transpose_note(self, note: Dict[str, Any], semitones: int) -> Dict[str, Any]:
        """Transpose une note individuelle"""
        # TODO: Implémenter transposition de note
        # - Gérer octaves
        # - Gérer altérations

        raise NotImplementedError("Transposition note - À implémenter")

    def get_transposition_info(self, semitones: int) -> str:
        """
        Génère une description textuelle de la transposition

        Args:
            semitones: Nombre de demi-tons

        Returns:
            Description (ex: "Transposé 2 tons au-dessus (de C à D)")
        """
        if semitones == 0:
            return "Aucune transposition"

        direction = "au-dessus" if semitones > 0 else "au-dessous"
        tones = abs(semitones) / 2
        return f"Transposé {tones} ton(s) {direction}"


def transpose_for_harmonica(
    melody: List[Dict[str, Any]],
    harmonica_type: str,
    harmonica_key: str,
    harmonica_map: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Fonction helper pour transposer une mélodie

    Args:
        melody: Mélodie originale
        harmonica_type: Type d'harmonica
        harmonica_key: Tonalité harmonica
        harmonica_map: Mapping

    Returns:
        Tuple (melody_transposée, semitones_transposition)
    """
    transposer = Transposer()

    # Vérifier jouabilité sans transposition
    playability = transposer.check_playability(melody, harmonica_type, harmonica_key, harmonica_map)

    if playability['playable']:
        return melody, 0

    # Chercher meilleure transposition
    semitones = transposer.find_best_transposition(melody, harmonica_type, harmonica_key, harmonica_map)

    if semitones is None:
        raise ValueError("Impossible de rendre ce morceau jouable sur cet harmonica")

    transposed_melody = transposer.transpose_melody(melody, semitones)
    return transposed_melody, semitones
