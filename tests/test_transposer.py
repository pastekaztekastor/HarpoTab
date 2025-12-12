"""
Tests unitaires pour le module transposer
"""
import pytest
from modules.transposer import Transposer, transpose_for_harmonica


def create_test_melody():
    """Crée une mélodie de test simple"""
    return {
        'notes': [
            {
                'type': 'note',
                'pitch': 'C',
                'octave': 4,
                'alter': 0,
                'duration': 4,
                'note_type': 'quarter',
                'midi': 60,
                'measure': 1,
                'time': 0
            },
            {
                'type': 'note',
                'pitch': 'D',
                'octave': 4,
                'alter': 0,
                'duration': 4,
                'note_type': 'quarter',
                'midi': 62,
                'measure': 1,
                'time': 4
            },
            {
                'type': 'rest',
                'duration': 2,
                'note_type': 'eighth',
                'measure': 1,
                'time': 8
            },
            {
                'type': 'note',
                'pitch': 'E',
                'octave': 4,
                'alter': 0,
                'duration': 4,
                'note_type': 'quarter',
                'midi': 64,
                'measure': 1,
                'time': 10
            }
        ],
        'metadata': {},
        'part_id': 'P1',
        'total_measures': 1
    }


def create_test_harmonica_map():
    """Crée un mapping d'harmonica de test simplifié"""
    return {
        'type': 'diatonic',
        'key': 'C',
        'notes': {
            '1': {
                'blow': {'note': 'C', 'octave': 4},
                'draw': {'note': 'D', 'octave': 4}
            },
            '2': {
                'blow': {'note': 'E', 'octave': 4},
                'draw': {'note': 'G', 'octave': 4}
            },
            '3': {
                'blow': {'note': 'G', 'octave': 4},
                'draw': {'note': 'B', 'octave': 4}
            },
            '4': {
                'blow': {'note': 'C', 'octave': 5},
                'draw': {'note': 'D', 'octave': 5}
            }
        }
    }


def test_transposer_init():
    """Test l'initialisation du Transposer"""
    transposer = Transposer()
    assert transposer is not None
    assert len(transposer.NOTE_TO_SEMITONES) > 0
    assert len(transposer.SEMITONES_TO_NOTE) == 12


def test_transpose_melody_no_change():
    """Test transposition de 0 demi-tons (pas de changement)"""
    transposer = Transposer()
    melody = create_test_melody()

    transposed = transposer.transpose_melody(melody, 0)

    # La mélodie doit être identique
    assert len(transposed['notes']) == len(melody['notes'])
    assert transposed['notes'][0]['midi'] == 60
    assert transposed['notes'][1]['midi'] == 62


def test_transpose_melody_up():
    """Test transposition vers le haut (+2 demi-tons)"""
    transposer = Transposer()
    melody = create_test_melody()

    transposed = transposer.transpose_melody(melody, 2)

    # C4 (60) -> D4 (62)
    assert transposed['notes'][0]['midi'] == 62
    assert transposed['notes'][0]['pitch'] == 'D'
    assert transposed['notes'][0]['octave'] == 4

    # D4 (62) -> E4 (64)
    assert transposed['notes'][1]['midi'] == 64
    assert transposed['notes'][1]['pitch'] == 'E'
    assert transposed['notes'][1]['octave'] == 4

    # E4 (64) -> F#4 (66)
    assert transposed['notes'][3]['midi'] == 66
    assert transposed['notes'][3]['pitch'] == 'F#'
    assert transposed['notes'][3]['octave'] == 4


def test_transpose_melody_down():
    """Test transposition vers le bas (-3 demi-tons)"""
    transposer = Transposer()
    melody = create_test_melody()

    transposed = transposer.transpose_melody(melody, -3)

    # C4 (60) -> A3 (57)
    assert transposed['notes'][0]['midi'] == 57
    assert transposed['notes'][0]['pitch'] == 'A'
    assert transposed['notes'][0]['octave'] == 3


def test_transpose_note_with_rest():
    """Test que les silences ne sont pas transposés"""
    transposer = Transposer()
    rest = {
        'type': 'rest',
        'duration': 2,
        'note_type': 'eighth'
    }

    transposed = transposer._transpose_note(rest, 5)

    assert transposed['type'] == 'rest'
    assert 'midi' not in transposed


def test_midi_to_note():
    """Test la conversion MIDI -> note"""
    transposer = Transposer()

    # C4 = MIDI 60
    note, octave = transposer._midi_to_note(60)
    assert note == 'C'
    assert octave == 4

    # A4 = MIDI 69
    note, octave = transposer._midi_to_note(69)
    assert note == 'A'
    assert octave == 4

    # C5 = MIDI 72
    note, octave = transposer._midi_to_note(72)
    assert note == 'C'
    assert octave == 5

    # F#3 = MIDI 54
    note, octave = transposer._midi_to_note(54)
    assert note == 'F#'
    assert octave == 3


def test_check_playability_full():
    """Test vérification de jouabilité (100%)"""
    transposer = Transposer()
    melody = create_test_melody()
    harmonica_map = create_test_harmonica_map()

    playability = transposer.check_playability(melody, harmonica_map)

    assert playability['playable'] is True
    assert playability['coverage'] == 1.0
    assert playability['playable_notes'] == 3  # 3 notes (pas le silence)
    assert playability['total_notes'] == 3
    assert len(playability['missing_notes']) == 0


def test_check_playability_partial():
    """Test vérification de jouabilité partielle"""
    transposer = Transposer()

    # Mélodie avec une note non jouable (F4)
    melody = {
        'notes': [
            {'type': 'note', 'pitch': 'C', 'octave': 4, 'midi': 60},
            {'type': 'note', 'pitch': 'F', 'octave': 4, 'midi': 65},  # Non jouable
            {'type': 'note', 'pitch': 'G', 'octave': 4, 'midi': 67}
        ]
    }

    harmonica_map = create_test_harmonica_map()
    playability = transposer.check_playability(melody, harmonica_map)

    assert playability['playable'] is False
    assert playability['coverage'] < 1.0
    assert playability['playable_notes'] == 2
    assert playability['total_notes'] == 3
    assert 'F4' in playability['missing_notes']


def test_find_best_transposition():
    """Test recherche de la meilleure transposition"""
    transposer = Transposer()

    # Mélodie avec une note non jouable initialement
    melody = {
        'notes': [
            {'type': 'note', 'pitch': 'A', 'octave': 3, 'midi': 57},
            {'type': 'note', 'pitch': 'B', 'octave': 3, 'midi': 59},
        ]
    }

    harmonica_map = create_test_harmonica_map()

    # Chercher une transposition
    result = transposer.find_best_transposition(melody, harmonica_map)

    assert result is not None
    semitones, playability = result

    # Vérifier qu'une transposition a été trouvée
    assert isinstance(semitones, int)
    assert playability['coverage'] > 0


def test_get_transposition_info():
    """Test génération d'info de transposition"""
    transposer = Transposer()

    assert transposer.get_transposition_info(0) == "Aucune transposition"
    assert "ton(s) au-dessus" in transposer.get_transposition_info(2)
    assert "ton(s) au-dessous" in transposer.get_transposition_info(-3)


def test_get_key_from_transposition():
    """Test calcul de la nouvelle tonalité"""
    transposer = Transposer()

    # C + 2 demi-tons = D
    assert transposer.get_key_from_transposition('C', 2) == 'D'

    # G + 5 demi-tons = C
    assert transposer.get_key_from_transposition('G', 5) == 'C'

    # D - 2 demi-tons = C
    assert transposer.get_key_from_transposition('D', -2) == 'C'

    # C + 12 demi-tons = C (octave au-dessus)
    assert transposer.get_key_from_transposition('C', 12) == 'C'


def test_transpose_for_harmonica_no_transpose():
    """Test helper function sans transposition nécessaire"""
    melody = create_test_melody()
    harmonica_map = create_test_harmonica_map()

    transposed, semitones, playability = transpose_for_harmonica(melody, harmonica_map)

    # Pas de transposition nécessaire
    assert semitones == 0
    assert playability['playable'] is True


def test_transpose_for_harmonica_force_transpose():
    """Test helper function avec transposition forcée"""
    melody = create_test_melody()
    harmonica_map = create_test_harmonica_map()

    transposed, semitones, playability = transpose_for_harmonica(
        melody,
        harmonica_map,
        force_transpose=2
    )

    assert semitones == 2
    assert transposed['notes'][0]['midi'] == 62  # C4 -> D4


def test_transpose_melody_with_list():
    """Test transposition avec une simple liste de notes"""
    transposer = Transposer()
    notes_list = [
        {'type': 'note', 'pitch': 'C', 'octave': 4, 'midi': 60},
        {'type': 'note', 'pitch': 'D', 'octave': 4, 'midi': 62}
    ]

    transposed = transposer.transpose_melody(notes_list, 2)

    assert isinstance(transposed, list)
    assert transposed[0]['midi'] == 62
    assert transposed[1]['midi'] == 64


def test_transpose_octave_change():
    """Test transposition qui change d'octave"""
    transposer = Transposer()
    melody = {
        'notes': [
            {'type': 'note', 'pitch': 'B', 'octave': 3, 'midi': 59}
        ]
    }

    # B3 + 2 demi-tons = C#4 (changement d'octave)
    transposed = transposer.transpose_melody(melody, 2)

    assert transposed['notes'][0]['midi'] == 61
    assert transposed['notes'][0]['pitch'] == 'C#'
    assert transposed['notes'][0]['octave'] == 4
