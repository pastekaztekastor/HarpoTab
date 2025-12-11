"""
Module de conversion de notes musicales en tablature d'harmonica.

Utilise les mappings définis dans harmonica_maps.json pour convertir
les notes en notation tablature selon le type d'harmonica et la tonalité.
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TabNote:
    """Représente une note en notation tablature."""
    note_name: str        # Nom de la note originale (ex: 'C4')
    hole: int             # Numéro du trou (1-10)
    action: str           # 'blow' (souffler) ou 'draw' (aspirer)
    tab_notation: str     # Notation formatée (ex: '4↑', '5↓', '+4', '-5')
    duration: str         # Durée de la note
    measure: int          # Numéro de mesure

    def __str__(self):
        return self.tab_notation


class HarmonicaConverter:
    """Classe pour convertir des notes en tablature d'harmonica."""

    def __init__(self, harmonica_type='diatonic', tonality='C'):
        """
        Initialise le convertisseur.

        Args:
            harmonica_type (str): Type d'harmonica ('diatonic' ou 'chromatic')
            tonality (str): Tonalité de l'harmonica (ex: 'C', 'G', 'A')
        """
        self.harmonica_type = harmonica_type
        self.tonality = tonality
        self.mapping = self._load_mapping()

    def _load_mapping(self):
        """Charge le mapping depuis le fichier JSON."""
        mapping_file = os.path.join('data', 'harmonica_maps.json')

        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if self.harmonica_type not in data:
                raise ValueError(f"Type d'harmonica '{self.harmonica_type}' non supporté")

            if self.tonality not in data[self.harmonica_type]:
                raise ValueError(f"Tonalité '{self.tonality}' non supportée pour {self.harmonica_type}")

            return data[self.harmonica_type][self.tonality]

        except FileNotFoundError:
            raise Exception(f"Fichier de mapping non trouvé : {mapping_file}")
        except json.JSONDecodeError:
            raise Exception(f"Erreur de format dans le fichier de mapping")

    def find_note_mapping(self, note_name):
        """
        Trouve le mapping d'une note dans la tablature.

        Args:
            note_name (str): Nom de la note (ex: 'C4')

        Returns:
            dict: Informations de mapping ou None si non trouvé
        """
        return self.mapping.get(note_name)

    def convert_note(self, note, notation_style='arrows'):
        """
        Convertit une note en tablature.

        Args:
            note: Objet Note de music_parser
            notation_style (str): Style de notation ('arrows', 'letters', 'symbols')

        Returns:
            TabNote: Note convertie en tablature
        """
        mapping = self.find_note_mapping(note.name)

        if mapping is None:
            # Note non trouvée dans le mapping
            return TabNote(
                note_name=note.name,
                hole=0,
                action='unknown',
                tab_notation=f'[{note.name}?]',
                duration=note.duration,
                measure=note.measure
            )

        hole = mapping['hole']
        action = mapping['action']
        slide = mapping.get('slide')  # Pour harmonica chromatique

        # Formater la notation selon le style
        tab_notation = self._format_notation(hole, action, notation_style, slide)

        return TabNote(
            note_name=note.name,
            hole=hole,
            action=action,
            tab_notation=tab_notation,
            duration=note.duration,
            measure=note.measure
        )

    def _format_notation(self, hole, action, style, slide=None):
        """
        Formate la notation de tablature selon le style choisi.

        Args:
            hole (int): Numéro du trou
            action (str): 'blow' ou 'draw'
            style (str): Style de notation
            slide (str): 'in' ou 'out' pour harmonica chromatique (optionnel)

        Returns:
            str: Notation formatée
        """
        # Pour harmonica chromatique, ajouter indicateur slide
        slide_marker = ''
        if slide == 'in':
            slide_marker = '<'  # Slide poussé (note chromatique)

        if style == 'arrows':
            # Flèches : 4↑ (souffler), 5↓ (aspirer)
            arrow = '↑' if action == 'blow' else '↓'
            return f"{hole}{arrow}{slide_marker}"

        elif style == 'letters':
            # Lettres : 4B (blow), 5D (draw)
            letter = 'B' if action == 'blow' else 'D'
            return f"{hole}{letter}{slide_marker}"

        elif style == 'symbols':
            # Symboles : +4 (souffler), -5 (aspirer)
            symbol = '+' if action == 'blow' else '-'
            return f"{symbol}{hole}{slide_marker}"

        else:
            # Par défaut, utiliser les flèches
            arrow = '↑' if action == 'blow' else '↓'
            return f"{hole}{arrow}{slide_marker}"

    def get_available_notes(self):
        """
        Retourne la liste des notes disponibles sur l'harmonica.

        Returns:
            list: Liste des noms de notes disponibles
        """
        return list(self.mapping.keys())

    def get_note_range(self):
        """
        Retourne la tessiture (étendue) de l'harmonica.

        Returns:
            dict: Note la plus basse et la plus haute
        """
        notes = self.get_available_notes()
        if not notes:
            return {'lowest': None, 'highest': None}

        # Extraire les octaves
        def get_octave(note_name):
            import re
            match = re.search(r'\d+', note_name)
            return int(match.group()) if match else 0

        sorted_notes = sorted(notes, key=lambda n: (get_octave(n), n[0]))

        return {
            'lowest': sorted_notes[0] if sorted_notes else None,
            'highest': sorted_notes[-1] if sorted_notes else None
        }


def convert_to_harmonica(notes, harmonica_type='diatonic', tonality='C', notation_style='arrows'):
    """
    Convertit une liste de notes en tablature d'harmonica.

    Args:
        notes (List[Note]): Liste d'objets Note
        harmonica_type (str): Type d'harmonica
        tonality (str): Tonalité
        notation_style (str): Style de notation

    Returns:
        List[dict]: Liste de notes converties en tablature
    """
    converter = HarmonicaConverter(harmonica_type, tonality)

    tablature = []
    for note in notes:
        tab_note = converter.convert_note(note, notation_style)

        # Convertir en dict pour l'affichage dans les templates
        tablature.append({
            'note_name': tab_note.note_name,
            'hole': tab_note.hole,
            'action': tab_note.action,
            'tab_notation': tab_note.tab_notation,
            'duration': tab_note.duration,
            'measure': tab_note.measure,
            'chord': note.chord  # Ajouter l'accord de la note
        })

    return tablature


def get_harmonica_diagram(harmonica_type='diatonic', tonality='C'):
    """
    Génère un diagramme de l'harmonica avec toutes les notes.

    Args:
        harmonica_type (str): Type d'harmonica
        tonality (str): Tonalité

    Returns:
        dict: Diagramme de l'harmonica
    """
    converter = HarmonicaConverter(harmonica_type, tonality)

    diagram = {
        'type': harmonica_type,
        'tonality': tonality,
        'holes': {}
    }

    # Organiser par trou
    for note_name, info in converter.mapping.items():
        if isinstance(info, dict) and 'hole' in info:
            hole = info['hole']
            action = info['action']

            if hole not in diagram['holes']:
                diagram['holes'][hole] = {}

            diagram['holes'][hole][action] = note_name

    return diagram


def analyze_playability(notes, harmonica_type='diatonic', tonality='C'):
    """
    Analyse si une mélodie est jouable sur un harmonica donné.

    Args:
        notes (List[Note]): Liste de notes
        harmonica_type (str): Type d'harmonica
        tonality (str): Tonalité

    Returns:
        dict: Statistiques de jouabilité
    """
    converter = HarmonicaConverter(harmonica_type, tonality)
    available_notes = converter.get_available_notes()

    total_notes = len(notes)
    playable_notes = sum(1 for note in notes if note.name in available_notes)
    missing_notes = [note.name for note in notes if note.name not in available_notes]

    return {
        'total_notes': total_notes,
        'playable_notes': playable_notes,
        'unplayable_notes': total_notes - playable_notes,
        'playability_percentage': (playable_notes / total_notes * 100) if total_notes > 0 else 0,
        'missing_notes': list(set(missing_notes)),  # Enlever les doublons
        'is_fully_playable': (total_notes - playable_notes) == 0
    }


def find_best_tonalities(notes, harmonica_type='diatonic', min_playability=80.0):
    """
    Teste toutes les tonalités disponibles et retourne celles qui permettent
    de jouer la mélodie (avec un minimum de jouabilité).

    Inspiré de HarpoTab de Daniel Cartron qui permet la transposition automatique.

    Args:
        notes (List[Note]): Liste de notes à analyser
        harmonica_type (str): Type d'harmonica
        min_playability (float): Pourcentage minimum de jouabilité (défaut 80%)

    Returns:
        list: Liste de tonalités possibles avec leurs statistiques, triées par jouabilité
    """
    # Toutes les tonalités disponibles pour harmonica diatonique
    all_tonalities = ['C', 'G', 'A', 'D', 'E', 'F', 'Bb']

    results = []

    for tonality in all_tonalities:
        try:
            playability = analyze_playability(notes, harmonica_type, tonality)

            # Ajouter seulement si la jouabilité est au-dessus du minimum
            if playability['playability_percentage'] >= min_playability:
                results.append({
                    'tonality': tonality,
                    'playability': playability['playability_percentage'],
                    'is_fully_playable': playability['is_fully_playable'],
                    'playable_notes': playability['playable_notes'],
                    'total_notes': playability['total_notes'],
                    'missing_notes': playability['missing_notes']
                })
        except (ValueError, Exception):
            # Tonalité non supportée ou erreur
            continue

    # Trier par jouabilité décroissante
    results.sort(key=lambda x: x['playability'], reverse=True)

    return results


def transpose_melody_to_tonality(notes, target_tonality, original_tonality='C'):
    """
    Transpose une mélodie vers une nouvelle tonalité.

    Cette fonction calcule l'intervalle de transposition et ajuste toutes les notes.

    Args:
        notes (List[Note]): Liste de notes originales
        target_tonality (str): Tonalité cible
        original_tonality (str): Tonalité d'origine (défaut C)

    Returns:
        List[Note]: Liste de notes transposées
    """
    # Mapping des tonalités vers demi-tons depuis C
    tonality_semitones = {
        'C': 0,
        'Db': 1, 'C#': 1,
        'D': 2,
        'Eb': 3, 'D#': 3,
        'E': 4,
        'F': 5,
        'F#': 6, 'Gb': 6,
        'G': 7,
        'Ab': 8, 'G#': 8,
        'A': 9,
        'Bb': 10, 'A#': 10,
        'B': 11
    }

    # Note: Cette fonction est un placeholder pour la transposition
    # Dans une implémentation complète, il faudrait utiliser music21 ou une bibliothèque similaire
    # Pour l'instant, on retourne les notes originales
    # TODO: Implémenter la vraie transposition avec music21

    return notes
