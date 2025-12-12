"""
Tests unitaires pour le module melody_extractor
"""
import pytest
from modules.melody_extractor import MelodyExtractor, extract_melody_from_musicxml


def create_test_musicxml_data():
    """Crée des données MusicXML de test"""
    return {
        'metadata': {
            'title': 'Test Song',
            'composer': 'Test Composer',
            'key': {'fifths': 0, 'mode': 'major'},
            'time_signature': '4/4',
            'tempo': 120
        },
        'parts': [
            {
                'id': 'P1',
                'measures': [
                    {
                        'number': 1,
                        'notes': [
                            {
                                'type': 'note',
                                'pitch': {'step': 'C', 'octave': 4, 'alter': 0},
                                'duration': 4,
                                'note_type': 'quarter'
                            },
                            {
                                'type': 'note',
                                'pitch': {'step': 'E', 'octave': 4, 'alter': 0},
                                'duration': 4,
                                'note_type': 'quarter'
                            },
                            {
                                'type': 'rest',
                                'duration': 2,
                                'note_type': 'eighth'
                            },
                            {
                                'type': 'note',
                                'pitch': {'step': 'G', 'octave': 4, 'alter': 0},
                                'duration': 4,
                                'note_type': 'quarter'
                            }
                        ]
                    },
                    {
                        'number': 2,
                        'notes': [
                            {
                                'type': 'note',
                                'pitch': {'step': 'F', 'octave': 4, 'alter': 1},  # F#
                                'duration': 8,
                                'note_type': 'half'
                            }
                        ]
                    }
                ]
            }
        ],
        'source_file': 'test.mxl'
    }


def test_melody_extractor_init():
    """Test l'initialisation du MelodyExtractor"""
    extractor = MelodyExtractor()
    assert extractor.keep_rests is True
    assert extractor.simplify_chords is True

    extractor2 = MelodyExtractor(keep_rests=False, simplify_chords=False)
    assert extractor2.keep_rests is False
    assert extractor2.simplify_chords is False


def test_extract_melody_basic():
    """Test l'extraction de mélodie basique"""
    musicxml_data = create_test_musicxml_data()
    extractor = MelodyExtractor(keep_rests=True)
    result = extractor.extract_melody(musicxml_data)

    assert result is not None
    assert 'notes' in result
    assert 'metadata' in result
    assert 'part_id' in result
    assert 'total_measures' in result

    # Vérifier le nombre d'événements (4 notes + 1 silence)
    assert len(result['notes']) == 5

    # Vérifier que les métadonnées sont copiées
    assert result['metadata']['title'] == 'Test Song'
    assert result['metadata']['composer'] == 'Test Composer'


def test_extract_melody_no_rests():
    """Test l'extraction sans les silences"""
    musicxml_data = create_test_musicxml_data()
    extractor = MelodyExtractor(keep_rests=False)
    result = extractor.extract_melody(musicxml_data)

    assert result is not None
    # Seulement 4 notes, pas de silences
    assert len(result['notes']) == 4

    # Vérifier qu'il n'y a que des notes
    for note in result['notes']:
        assert note['type'] == 'note'


def test_extract_melody_invalid_data():
    """Test avec des données invalides"""
    extractor = MelodyExtractor()

    # Données None
    result = extractor.extract_melody(None)
    assert result is None

    # Dictionnaire vide
    result = extractor.extract_melody({})
    assert result is None

    # Sans parties
    result = extractor.extract_melody({'parts': []})
    assert result is None


def test_note_to_midi():
    """Test la conversion note -> MIDI"""
    extractor = MelodyExtractor()

    # C4 = MIDI 60
    assert extractor._note_to_midi('C', 4, 0) == 60

    # A4 = MIDI 69
    assert extractor._note_to_midi('A', 4, 0) == 69

    # C5 = MIDI 72
    assert extractor._note_to_midi('C', 5, 0) == 72

    # F#4 = MIDI 66
    assert extractor._note_to_midi('F', 4, 1) == 66

    # Bb3 = MIDI 58
    assert extractor._note_to_midi('B', 3, -1) == 58


def test_select_highest_note():
    """Test la sélection de la note la plus haute d'un accord"""
    extractor = MelodyExtractor()

    chord_notes = [
        {
            'type': 'note',
            'pitch': {'step': 'C', 'octave': 4, 'alter': 0},
            'duration': 4
        },
        {
            'type': 'note',
            'pitch': {'step': 'E', 'octave': 4, 'alter': 0},
            'duration': 4
        },
        {
            'type': 'note',
            'pitch': {'step': 'G', 'octave': 4, 'alter': 0},
            'duration': 4
        }
    ]

    highest = extractor._select_highest_note(chord_notes)
    assert highest['pitch']['step'] == 'G'
    assert highest['pitch']['octave'] == 4


def test_calculate_average_pitch():
    """Test le calcul de la hauteur moyenne"""
    extractor = MelodyExtractor()

    part = {
        'id': 'P1',
        'measures': [
            {
                'number': 1,
                'notes': [
                    {
                        'type': 'note',
                        'pitch': {'step': 'C', 'octave': 4, 'alter': 0}
                    },
                    {
                        'type': 'note',
                        'pitch': {'step': 'C', 'octave': 5, 'alter': 0}
                    }
                ]
            }
        ]
    }

    avg = extractor._calculate_average_pitch(part)
    # C4 = 60, C5 = 72, moyenne = 66
    assert avg == 66.0


def test_get_note_name():
    """Test la génération du nom de note"""
    extractor = MelodyExtractor()

    # Note normale
    note1 = {
        'type': 'note',
        'pitch': 'C',
        'octave': 4,
        'alter': 0
    }
    assert extractor.get_note_name(note1) == 'C4'

    # Note avec dièse
    note2 = {
        'type': 'note',
        'pitch': 'F',
        'octave': 3,
        'alter': 1
    }
    assert extractor.get_note_name(note2) == 'F#3'

    # Note avec bémol
    note3 = {
        'type': 'note',
        'pitch': 'B',
        'octave': 4,
        'alter': -1
    }
    assert extractor.get_note_name(note3) == 'Bb4'

    # Silence
    rest = {
        'type': 'rest',
        'note_type': 'quarter'
    }
    assert 'Rest' in extractor.get_note_name(rest)


def test_extract_melody_multipart():
    """Test l'extraction avec plusieurs parties"""
    musicxml_data = {
        'metadata': {},
        'parts': [
            {
                'id': 'P1',
                'measures': [
                    {
                        'number': 1,
                        'notes': [
                            {
                                'type': 'note',
                                'pitch': {'step': 'C', 'octave': 3, 'alter': 0},
                                'duration': 4
                            }
                        ]
                    }
                ]
            },
            {
                'id': 'P2',
                'measures': [
                    {
                        'number': 1,
                        'notes': [
                            {
                                'type': 'note',
                                'pitch': {'step': 'C', 'octave': 5, 'alter': 0},
                                'duration': 4
                            },
                            {
                                'type': 'note',
                                'pitch': {'step': 'E', 'octave': 5, 'alter': 0},
                                'duration': 4
                            }
                        ]
                    }
                ]
            }
        ],
        'source_file': 'test.mxl'
    }

    extractor = MelodyExtractor()
    result = extractor.extract_melody(musicxml_data)

    # La partie P2 devrait être sélectionnée (plus de notes et tessiture plus haute)
    assert result['part_id'] == 'P2'
    assert len(result['notes']) == 2


def test_helper_function():
    """Test la fonction helper extract_melody_from_musicxml"""
    musicxml_data = create_test_musicxml_data()

    result = extract_melody_from_musicxml(musicxml_data, keep_rests=True)
    assert result is not None
    assert len(result['notes']) == 5

    result2 = extract_melody_from_musicxml(musicxml_data, keep_rests=False)
    assert result2 is not None
    assert len(result2['notes']) == 4
