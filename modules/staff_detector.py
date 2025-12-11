"""
Module de détection et séparation des portées musicales.

Gère les partitions piano avec 2 portées :
- Portée supérieure (clé de Sol) : MÉLODIE → pour harmonica
- Portée inférieure (clé de Fa) : ACCOMPAGNEMENT → à ignorer
"""


class StaffType:
    """Types de portées musicales."""
    TREBLE = 'treble'  # Clé de Sol (mélodie)
    BASS = 'bass'      # Clé de Fa (accompagnement)
    UNKNOWN = 'unknown'


class Staff:
    """Représente une portée musicale."""

    def __init__(self, staff_type, position_y, notes=None, chords=None):
        """
        Initialise une portée.

        Args:
            staff_type (str): Type de portée (treble/bass)
            position_y (int): Position verticale dans l'image
            notes (list): Liste des notes sur cette portée
            chords (list): Liste des accords
        """
        self.staff_type = staff_type
        self.position_y = position_y
        self.notes = notes or []
        self.chords = chords or []

    def is_melody(self):
        """Retourne True si c'est la portée de mélodie (clé de Sol)."""
        return self.staff_type == StaffType.TREBLE

    def is_accompaniment(self):
        """Retourne True si c'est la portée d'accompagnement (clé de Fa)."""
        return self.staff_type == StaffType.BASS

    def __repr__(self):
        return f"Staff({self.staff_type}, y={self.position_y}, notes={len(self.notes)})"


class PianoScore:
    """Représente une partition de piano avec 2 portées."""

    def __init__(self):
        self.treble_staff = None  # Portée clé de Sol (mélodie)
        self.bass_staff = None    # Portée clé de Fa (accompagnement)
        self.chords = []          # Progression d'accords
        self.title = None
        self.composer = None

    def set_treble_staff(self, staff):
        """Définit la portée de mélodie (clé de Sol)."""
        self.treble_staff = staff

    def set_bass_staff(self, staff):
        """Définit la portée d'accompagnement (clé de Fa)."""
        self.bass_staff = staff

    def get_melody_notes(self):
        """
        Retourne UNIQUEMENT les notes de la mélodie (clé de Sol).
        C'est ce que l'harmonica va jouer.
        """
        if self.treble_staff:
            return self.treble_staff.notes
        return []

    def has_two_staves(self):
        """Retourne True si la partition a bien 2 portées (piano)."""
        return self.treble_staff is not None and self.bass_staff is not None

    def __repr__(self):
        return f"PianoScore(treble={len(self.get_melody_notes())} notes, chords={len(self.chords)})"


def detect_staff_type_from_position(position_y, image_height):
    """
    Détecte le type de portée selon sa position verticale.

    Dans une partition piano :
    - Portée haute (< 50% hauteur) = Clé de Sol (mélodie)
    - Portée basse (> 50% hauteur) = Clé de Fa (accompagnement)

    Args:
        position_y (int): Position Y de la portée
        image_height (int): Hauteur totale de l'image

    Returns:
        str: Type de portée (treble/bass/unknown)
    """
    # Ratio de position
    ratio = position_y / image_height

    if ratio < 0.5:
        # Portée supérieure = Clé de Sol
        return StaffType.TREBLE
    elif ratio > 0.5:
        # Portée inférieure = Clé de Fa
        return StaffType.BASS
    else:
        return StaffType.UNKNOWN


def separate_piano_staves(music_data):
    """
    Sépare les données musicales en 2 portées (piano).

    Pour le MVP avec données de démo :
    - On simule la détection de 2 portées
    - On marque la portée supérieure comme mélodie (clé de Sol)
    - On ignore la portée inférieure (clé de Fa)

    Args:
        music_data (dict): Données musicales brutes

    Returns:
        PianoScore: Partition piano avec portées séparées
    """
    score = PianoScore()

    # Pour le MVP : simuler la détection
    if music_data.get('format') == 'image':
        # C'est une image de partition piano
        height = music_data.get('height', 1024)

        # Portée supérieure (clé de Sol) - MÉLODIE
        treble_staff = Staff(
            staff_type=StaffType.TREBLE,
            position_y=int(height * 0.3),  # ~30% de la hauteur
            notes=music_data.get('raw_notes', [])  # Notes de la mélodie
        )
        score.set_treble_staff(treble_staff)

        # Portée inférieure (clé de Fa) - ACCOMPAGNEMENT (ignorée)
        bass_staff = Staff(
            staff_type=StaffType.BASS,
            position_y=int(height * 0.7),  # ~70% de la hauteur
            notes=[]  # On ne récupère pas les notes d'accompagnement
        )
        score.set_bass_staff(bass_staff)

        # Accords (si disponibles)
        if 'chords' in music_data:
            score.chords = music_data['chords']

        # Métadonnées
        score.title = music_data.get('title')
        score.composer = music_data.get('composer')

    return score


def extract_melody_only(music_data):
    """
    Extrait UNIQUEMENT la mélodie (clé de Sol) d'une partition piano.

    Cette fonction filtre les données pour ne garder que la portée supérieure,
    ignorant complètement la portée d'accompagnement (clé de Fa).

    Args:
        music_data (dict): Données musicales complètes

    Returns:
        dict: Données filtrées avec seulement la mélodie
    """
    # Séparer les portées
    piano_score = separate_piano_staves(music_data)

    # Créer un nouveau dict avec SEULEMENT la mélodie
    melody_data = {
        'source': music_data.get('source'),
        'format': music_data.get('format'),
        'raw_notes': piano_score.get_melody_notes(),  # UNIQUEMENT clé de Sol
        'chords': piano_score.chords,
        'title': piano_score.title,
        'composer': piano_score.composer,
        'demo': music_data.get('demo', False),
        'message': 'Mélodie extraite (clé de Sol uniquement)',
        'staff_info': {
            'has_two_staves': piano_score.has_two_staves(),
            'melody_notes_count': len(piano_score.get_melody_notes()),
            'extracted_from': 'treble_clef'
        }
    }

    return melody_data


def detect_chords_from_image(image_path):
    """
    Détecte les symboles d'accords au-dessus de la portée.

    Pour le MVP : retourne une progression d'accords typique.

    Args:
        image_path (str): Chemin vers l'image

    Returns:
        list: Liste de tuples (mesure, accord)
    """
    # Pour le MVP : "Avant Toi" utilise Am-F-C-G
    demo_chords = [
        (1, 'Am'),
        (2, 'F'),
        (3, 'C'),
        (4, 'G'),
        (5, 'Am'),
        (6, 'F'),
        (7, 'C'),
        (8, 'G'),
        (9, 'Am'),
        (10, 'F'),
        (11, 'C'),
        (12, 'G'),
        (13, 'Dm'),
        (14, 'Dm'),
        (15, 'F'),
        (16, 'G'),
    ]

    return demo_chords


def is_piano_score(music_data):
    """
    Détermine si c'est une partition de piano (2 portées).

    Args:
        music_data (dict): Données musicales

    Returns:
        bool: True si partition piano
    """
    # Pour le MVP : toutes les images sont considérées comme partitions piano
    if music_data.get('format') == 'image':
        return True

    # PDF : pas de détection pour le MVP
    return False
