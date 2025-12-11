"""
Module d'analyse et de parsing des données musicales.

Convertit les données brutes extraites en objets Note structurés
avec toutes les informations nécessaires pour la conversion en tablature.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Note:
    """Représente une note musicale avec ses attributs."""
    name: str           # Nom de la note (ex: 'C4', 'D#5')
    pitch: str          # Hauteur sans octave (ex: 'C', 'D#')
    octave: int         # Numéro d'octave (ex: 4, 5)
    duration: str       # Durée (ex: 'quarter', 'half', 'whole')
    measure: int        # Numéro de mesure
    position: float     # Position dans la mesure (0.0 à 1.0)
    chord: str = None   # Accord de la mesure (ex: 'Am', 'F', 'C', 'G')

    def __str__(self):
        chord_str = f" [{self.chord}]" if self.chord else ""
        return f"{self.name} ({self.duration}) - Mesure {self.measure}{chord_str}"


def parse_note_name(note_str):
    """
    Parse un nom de note et extrait la hauteur et l'octave.

    Args:
        note_str (str): Nom de la note (ex: 'C4', 'D#5', 'Bb3')

    Returns:
        tuple: (pitch, octave) ou (None, None) si invalide
    """
    # Pattern pour matcher les notes
    # Exemples: C4, D#5, Bb3, F#4
    pattern = r'^([A-G][#b]?)(\d+)$'
    match = re.match(pattern, note_str)

    if match:
        pitch = match.group(1)
        octave = int(match.group(2))
        return pitch, octave

    return None, None


def parse_musical_notes(music_data):
    """
    Parse les données musicales brutes et crée des objets Note.
    Ajoute les accords si disponibles dans music_data.

    Args:
        music_data (dict): Données musicales extraites du PDF/image

    Returns:
        List[Note]: Liste d'objets Note (avec accords si disponibles)
    """
    notes = []
    raw_notes = music_data.get('raw_notes', [])

    # Récupérer les accords (si disponibles)
    chords = music_data.get('chords', [])
    chords_dict = {measure: chord for measure, chord in chords} if chords else {}

    # Calcul du nombre de mesures (4 notes par mesure par défaut)
    notes_per_measure = 4
    current_measure = 1
    position_in_measure = 0

    for i, note_str in enumerate(raw_notes):
        pitch, octave = parse_note_name(note_str)

        if pitch is None:
            # Note invalide, on passe
            continue

        # Déterminer la durée (pour le MVP, tout est en noires)
        duration = 'quarter'

        # Calculer la position dans la mesure
        position = position_in_measure / notes_per_measure

        # Récupérer l'accord de cette mesure
        current_chord = chords_dict.get(current_measure)

        # Créer l'objet Note
        note = Note(
            name=note_str,
            pitch=pitch,
            octave=octave,
            duration=duration,
            measure=current_measure,
            position=position,
            chord=current_chord
        )

        notes.append(note)

        # Avancer dans la mesure
        position_in_measure += 1
        if position_in_measure >= notes_per_measure:
            position_in_measure = 0
            current_measure += 1

    return notes


def get_duration_value(duration_str):
    """
    Convertit une durée de note en valeur numérique.

    Args:
        duration_str (str): Type de durée ('whole', 'half', 'quarter', 'eighth')

    Returns:
        float: Valeur de la durée (1.0 = ronde)
    """
    duration_map = {
        'whole': 1.0,
        'half': 0.5,
        'quarter': 0.25,
        'eighth': 0.125,
        'sixteenth': 0.0625
    }
    return duration_map.get(duration_str, 0.25)


def transpose_notes(notes, semitones):
    """
    Transpose une liste de notes d'un certain nombre de demi-tons.

    Args:
        notes (List[Note]): Liste de notes
        semitones (int): Nombre de demi-tons (+ ou -)

    Returns:
        List[Note]: Notes transposées
    """
    # Gamme chromatique
    chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    transposed_notes = []

    for note in notes:
        # Trouver l'index de la note actuelle
        try:
            current_index = chromatic_scale.index(note.pitch.replace('b', '#'))
        except ValueError:
            # Note avec bémol, convertir en dièse
            if 'b' in note.pitch:
                pitch_map = {
                    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
                }
                converted_pitch = pitch_map.get(note.pitch, note.pitch)
                current_index = chromatic_scale.index(converted_pitch)
            else:
                # Note invalide
                transposed_notes.append(note)
                continue

        # Calculer le nouvel index
        new_index = (current_index + semitones) % 12
        new_pitch = chromatic_scale[new_index]

        # Calculer le nouvel octave
        octave_change = (current_index + semitones) // 12
        new_octave = note.octave + octave_change

        # Créer la nouvelle note
        new_note = Note(
            name=f"{new_pitch}{new_octave}",
            pitch=new_pitch,
            octave=new_octave,
            duration=note.duration,
            measure=note.measure,
            position=note.position
        )

        transposed_notes.append(new_note)

    return transposed_notes


def analyze_key_signature(notes):
    """
    Analyse une liste de notes pour déterminer la tonalité probable.

    Args:
        notes (List[Note]): Liste de notes

    Returns:
        str: Tonalité détectée (ex: 'C', 'G', 'D')
    """
    # Compte les occurrences de chaque note (sans octave)
    pitch_counts = {}
    for note in notes:
        pitch = note.pitch
        pitch_counts[pitch] = pitch_counts.get(pitch, 0) + 1

    # Pour une implémentation simple, on retourne 'C' par défaut
    # Une vraie implémentation analyserait les intervalles et accords
    return 'C'


def get_note_info(note_name):
    """
    Récupère des informations détaillées sur une note.

    Args:
        note_name (str): Nom de la note (ex: 'C4')

    Returns:
        dict: Informations sur la note
    """
    pitch, octave = parse_note_name(note_name)

    if pitch is None:
        return None

    # Fréquence de base A4 = 440 Hz
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Convertir les bémols en dièses
    pitch_normalized = pitch.replace('Db', 'C#').replace('Eb', 'D#') \
                           .replace('Gb', 'F#').replace('Ab', 'G#') \
                           .replace('Bb', 'A#')

    try:
        note_index = note_names.index(pitch_normalized)
    except ValueError:
        return None

    # Calculer la fréquence
    # A4 est la note de référence (index 9, octave 4)
    semitones_from_a4 = (octave - 4) * 12 + (note_index - 9)
    frequency = 440 * (2 ** (semitones_from_a4 / 12))

    return {
        'name': note_name,
        'pitch': pitch,
        'octave': octave,
        'frequency': round(frequency, 2),
        'midi_number': 69 + semitones_from_a4
    }
