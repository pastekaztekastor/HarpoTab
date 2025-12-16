"""
Module d'analyse musicale (accords, tessiture, tonalité)
"""
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class MusicAnalyzer:
    """Analyseur de données musicales"""

    def __init__(self):
        """Initialise l'analyseur musical"""
        pass

    def analyze_melody(self, melody: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse complète d'une mélodie

        Args:
            melody: Liste de notes de la mélodie

        Returns:
            Dictionnaire d'analyse {key, range, chords, tempo, ...}
        """
        logger.info("Analyse de la mélodie")

        analysis = {
            'key': self.detect_key(melody),
            'range': self.get_range(melody),
            'chords': self.detect_chords(melody),
            'tempo': self.detect_tempo(melody),
            'time_signature': self.detect_time_signature(melody)
        }

        return analysis

    def detect_key(self, melody: List[Dict[str, Any]]) -> str:
        """
        Détecte la tonalité de la mélodie

        Args:
            melody: Liste de notes

        Returns:
            Tonalité (ex: 'C', 'G', 'Am', etc.)
        """
        # Implémentation basique : analyse de la première et dernière note
        # TODO: Améliorer avec analyse harmonique complète

        if not melody:
            return 'C'  # Par défaut

        # Filtrer les silences
        notes_only = [n for n in melody if n.get('type') == 'note']

        if not notes_only:
            return 'C'

        # Prendre la première note comme tonique (très basique)
        first_note = notes_only[0]
        pitch = first_note.get('pitch', 'C')

        # Retourner la note sans l'octave
        logger.info(f"Tonalité détectée (basique): {pitch}")
        return pitch

    def get_range(self, melody: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Calcule la tessiture (étendue) de la mélodie

        Args:
            melody: Liste de notes

        Returns:
            Dict {'lowest': note_min, 'highest': note_max} ex: {'lowest': 'C4', 'highest': 'G5'}
        """
        # Filtrer les silences
        notes_only = [n for n in melody if n.get('type') == 'note']

        if not notes_only:
            return {'lowest': 'C4', 'highest': 'C4'}

        # Calculer min et max
        min_note = min(notes_only, key=lambda n: (n.get('octave', 4), self._pitch_to_semitone(n.get('pitch', 'C'))))
        max_note = max(notes_only, key=lambda n: (n.get('octave', 4), self._pitch_to_semitone(n.get('pitch', 'C'))))

        min_str = f"{min_note.get('pitch', 'C')}{min_note.get('octave', 4)}"
        max_str = f"{max_note.get('pitch', 'C')}{max_note.get('octave', 4)}"

        logger.info(f"Tessiture: {min_str} - {max_str}")
        return {'lowest': min_str, 'highest': max_str}

    def _pitch_to_semitone(self, pitch: str) -> int:
        """Convertit une note en demi-tons (C=0)"""
        notes = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        base_note = pitch[0]
        semitone = notes.get(base_note, 0)

        # Gérer les altérations
        if len(pitch) > 1:
            if '#' in pitch:
                semitone += 1
            elif 'b' in pitch:
                semitone -= 1

        return semitone

    def detect_chords(self, music_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Détecte les accords depuis la partition complète

        Args:
            music_data: Données musicales complètes

        Returns:
            Liste d'accords [{name, position, duration}, ...]
        """
        # Pour l'instant, retourner une liste vide
        # TODO: Analyser les parties d'accompagnement (main gauche piano, etc.)
        logger.info("Détection d'accords désactivée (optionnel)")
        return []

    def detect_tempo(self, music_data: Dict[str, Any]) -> int:
        """
        Détecte le tempo

        Args:
            music_data: Données musicales

        Returns:
            Tempo en BPM
        """
        # TODO: Extraire tempo depuis métadonnées MusicXML

        return 120  # Valeur par défaut

    def detect_time_signature(self, music_data: Dict[str, Any]) -> str:
        """
        Détecte la signature rythmique

        Args:
            music_data: Données musicales

        Returns:
            Signature (ex: '4/4', '3/4', '6/8')
        """
        # TODO: Extraire depuis métadonnées

        return '4/4'  # Valeur par défaut


def analyze_music(melody: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fonction helper pour l'analyse musicale

    Args:
        melody: Mélodie extraite

    Returns:
        Analyse complète
    """
    analyzer = MusicAnalyzer()
    return analyzer.analyze_melody(melody)
