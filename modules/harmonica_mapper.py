"""
Module de mapping notes → tablature harmonica
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class HarmonicaMapper:
    """Convertit des notes en tablature harmonica"""

    def __init__(self, harmonica_type: str, harmonica_key: str, maps_dir: Path):
        """
        Initialise le mapper

        Args:
            harmonica_type: Type d'harmonica (diatonic, chromatic)
            harmonica_key: Tonalité (C, D, G, etc.)
            maps_dir: Dossier contenant les fichiers de mapping JSON
        """
        self.harmonica_type = harmonica_type
        self.harmonica_key = harmonica_key
        self.maps_dir = maps_dir

        self.mapping = self._load_mapping()

    def _load_mapping(self) -> Dict[str, Any]:
        """Charge le fichier de mapping approprié"""
        filename = f"{self.harmonica_type}_{self.harmonica_key}.json"
        mapping_file = self.maps_dir / filename

        if not mapping_file.exists():
            raise FileNotFoundError(f"Mapping non trouvé: {mapping_file}")

        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def map_melody_to_tabs(self, melody: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convertit une mélodie en tablature

        Args:
            melody: Liste de notes [{note, octave, duration}, ...]

        Returns:
            Liste de tablatures [{hole, direction, technique, duration}, ...]
        """
        logger.info(f"Conversion en tablature {self.harmonica_type} {self.harmonica_key}")

        tabs = []
        for note in melody:
            tab = self._map_note_to_tab(note)
            if tab:
                tabs.append(tab)
            else:
                logger.warning(f"Note non mappable: {note}")

        return tabs

    def _map_note_to_tab(self, note: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Mappe une note individuelle vers tablature

        Args:
            note: Note musicale {note, octave, duration}

        Returns:
            Tablature {hole, direction, technique, duration}
        """
        # TODO: Implémenter mapping
        # - Chercher la note dans le mapping
        # - Déterminer le trou et la direction
        # - Identifier si bend/overblow nécessaire
        # - Choisir la position optimale (plusieurs positions possibles)

        raise NotImplementedError("Mapping note → tab - À implémenter")

    def get_technique(self, note: str, octave: int) -> Optional[str]:
        """
        Détermine la technique nécessaire pour une note

        Args:
            note: Note (ex: 'C#')
            octave: Octave

        Returns:
            Technique ('bend', 'overblow', 'overdraw', None)
        """
        # TODO: Implémenter détection technique

        raise NotImplementedError("Détection technique - À implémenter")

    def choose_optimal_position(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Choisit la meilleure position parmi plusieurs possibles

        Args:
            candidates: Liste de positions possibles

        Returns:
            Position optimale
        """
        # TODO: Heuristique de choix
        # - Préférer positions centrales (trous 4-7)
        # - Éviter les bends si possible
        # - Optimiser le mouvement (position précédente)

        raise NotImplementedError("Choix position optimale - À implémenter")


def map_to_harmonica(
    melody: List[Dict[str, Any]],
    harmonica_type: str,
    harmonica_key: str,
    maps_dir: Path
) -> List[Dict[str, Any]]:
    """
    Fonction helper pour mapper une mélodie

    Args:
        melody: Mélodie à mapper
        harmonica_type: Type d'harmonica
        harmonica_key: Tonalité
        maps_dir: Dossier de mappings

    Returns:
        Tablature
    """
    mapper = HarmonicaMapper(harmonica_type, harmonica_key, maps_dir)
    return mapper.map_melody_to_tabs(melody)
