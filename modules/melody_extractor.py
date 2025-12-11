"""
Module d'extraction de la mélodie principale depuis une partition
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MelodyExtractor:
    """Extracteur de mélodie depuis données MusicXML"""

    def __init__(self):
        """Initialise l'extracteur de mélodie"""
        pass

    def extract_melody(self, music_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait la mélodie principale depuis les données musicales

        Args:
            music_data: Données musicales (depuis OCR)

        Returns:
            Liste de notes de la mélodie [{note, duration, octave}, ...]
        """
        logger.info("Extraction de la mélodie principale")

        # TODO: Implémenter l'extraction de mélodie
        # - Identifier la portée contenant la mélodie (généralement main droite pour piano)
        # - Extraire les notes, durées, hauteurs
        # - Simplifier en ligne mélodique monophonique

        raise NotImplementedError("Extraction mélodie - À implémenter")

    def identify_melody_staff(self, music_data: Dict[str, Any]) -> Optional[int]:
        """
        Identifie quelle portée contient la mélodie

        Args:
            music_data: Données musicales complètes

        Returns:
            Index de la portée de mélodie
        """
        # TODO: Heuristique pour identifier la mélodie
        # - Pour piano: généralement clé de sol (staff 1)
        # - Note la plus aiguë en moyenne
        # - Portée supérieure

        raise NotImplementedError("Identification portée mélodie - À implémenter")

    def simplify_to_monophonic(self, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simplifie une ligne potentiellement polyphonique en monophonique

        Args:
            notes: Liste de notes (peut contenir des accords)

        Returns:
            Liste de notes simples (une seule note par temps)
        """
        # TODO: Simplification
        # - Si accord: prendre la note la plus aiguë
        # - Supprimer les ornements
        # - Garder la ligne mélodique principale

        raise NotImplementedError("Simplification monophonique - À implémenter")


def extract_melody_from_musicxml(music_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fonction helper pour extraire la mélodie

    Args:
        music_data: Données MusicXML parsées

    Returns:
        Mélodie extraite
    """
    extractor = MelodyExtractor()
    return extractor.extract_melody(music_data)
