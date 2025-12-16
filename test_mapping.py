#!/usr/bin/env python
"""Test du mapping harmonica pour A et B"""

from modules.harmonica_mapper import HarmonicaMapper
from pathlib import Path
from config import Config

# Créer le mapper
mapper = HarmonicaMapper('diatonic', 'C', Config.HARMONICA_MAPS_DIR)

# Tester les notes A4 et B4
test_notes = [
    {'type': 'note', 'pitch': 'A', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'B', 'octave': 4, 'duration': 4},
]

print("Test mapping A4 et B4:\n")
for note in test_notes:
    result = mapper._map_note_to_tab(note)
    print(f"{note['pitch']}{note['octave']}:")
    print(f"  Trou: {result['hole']}")
    print(f"  Direction: {result['direction']}")
    print(f"  Technique: {result.get('technique')}")
    print()

# Test de la mélodie complète
melody = [
    {'type': 'note', 'pitch': 'C', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'D', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'E', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'F', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'G', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'A', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'B', 'octave': 4, 'duration': 4},
    {'type': 'note', 'pitch': 'C', 'octave': 5, 'duration': 4},
]

tabs = mapper.map_melody_to_tabs(melody)

print("Gamme de Do complète:")
for i, (note, tab) in enumerate(zip(melody, tabs)):
    technique_str = f" ({tab.get('technique')})" if tab.get('technique') else ""
    print(f"{note['pitch']}{note['octave']}: {tab['hole']}{tab['direction'][0].upper()}{technique_str}")
