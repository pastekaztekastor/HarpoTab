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
        # Les silences passent directement
        if note.get('type') == 'rest':
            return {
                'type': 'rest',
                'duration': note.get('duration', 4)
            }

        # Récupérer pitch et octave
        pitch = note.get('pitch')
        octave = note.get('octave')

        if not pitch or octave is None:
            logger.warning(f"Note incomplète (pas de pitch/octave): {note}")
            return None

        # Chercher toutes les positions possibles pour cette note
        candidates = []

        for hole_num, hole_data in self.mapping.get('notes', {}).items():
            for technique, note_data in hole_data.items():
                if note_data['note'] == pitch and note_data['octave'] == octave:
                    # Déterminer la direction et la technique
                    if technique == 'blow':
                        direction = 'blow'
                        bend = None
                    elif technique == 'draw':
                        direction = 'draw'
                        bend = None
                    elif 'blow_bend' in technique:
                        direction = 'blow'
                        bend = technique.replace('blow_', '')
                    elif 'draw_bend' in technique:
                        direction = 'draw'
                        bend = technique.replace('draw_', '')
                    elif 'overblow' in technique:
                        direction = 'blow'
                        bend = 'overblow'
                    elif 'overdraw' in technique:
                        direction = 'draw'
                        bend = 'overdraw'
                    else:
                        continue

                    candidates.append({
                        'hole': int(hole_num),
                        'direction': direction,
                        'technique': bend,
                        'duration': note.get('duration', 4),
                        'pitch': pitch,
                        'octave': octave
                    })

        if not candidates:
            logger.warning(f"Note non jouable: {pitch}{octave}")
            return None

        # Si plusieurs positions possibles, choisir la meilleure
        if len(candidates) > 1:
            return self.choose_optimal_position(candidates)
        else:
            return candidates[0]

    def get_technique(self, note: str, octave: int) -> Optional[str]:
        """
        Détermine la technique nécessaire pour une note

        Args:
            note: Note (ex: 'C#')
            octave: Octave

        Returns:
            Technique ('bend', 'overblow', 'overdraw', None)
        """
        # Cette fonction est maintenant gérée dans _map_note_to_tab
        # Garder pour compatibilité
        for hole_num, hole_data in self.mapping.get('notes', {}).items():
            for technique, note_data in hole_data.items():
                if note_data['note'] == note and note_data['octave'] == octave:
                    if 'bend' in technique:
                        return 'bend'
                    elif 'overblow' in technique:
                        return 'overblow'
                    elif 'overdraw' in technique:
                        return 'overdraw'
        return None

    def choose_optimal_position(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Choisit la meilleure position parmi plusieurs possibles

        Args:
            candidates: Liste de positions possibles

        Returns:
            Position optimale
        """
        # Heuristiques de choix (par ordre de priorité):
        # 1. Éviter les techniques avancées (overblow/overdraw)
        # 2. Préférer les notes naturelles (sans bend)
        # 3. Préférer les positions centrales (trous 4-7)
        # 4. Préférer les bends simples aux bends complexes

        def score_position(pos: Dict[str, Any]) -> int:
            score = 0
            hole = pos['hole']
            technique = pos.get('technique')

            # Score de base pour position centrale
            if 4 <= hole <= 7:
                score += 100
            elif 3 <= hole <= 8:
                score += 50
            elif 2 <= hole <= 9:
                score += 20

            # Pénalité pour techniques avancées
            if technique == 'overblow' or technique == 'overdraw':
                score -= 200
            elif technique and 'bend' in technique:
                # Pénalité selon complexité du bend
                if 'full_half' in technique:
                    score -= 100
                elif 'full' in technique:
                    score -= 50
                elif 'half' in technique:
                    score -= 30
            else:
                # Bonus pour note naturelle
                score += 150

            return score

        # Trier par score décroissant et retourner le meilleur
        candidates.sort(key=score_position, reverse=True)
        return candidates[0]


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
