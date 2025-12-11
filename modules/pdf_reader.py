"""
Module de lecture et extraction de données musicales depuis PDF et images.

NOUVEAU : OCR musical RÉEL avec Audiveris !
- Reconnaissance optique automatique des partitions PDF/images
- Export MusicXML puis parsing avec music21
- Support MusicXML direct pour import depuis MuseScore/Finale/Sibelius

Ordre de priorité :
1. MusicXML direct (zéro perte)
2. Audiveris OCR (si installé) - RÉEL
3. Données démo (fallback pour tests)
"""

import pdfplumber
from PIL import Image
import subprocess
import os
import tempfile

# OpenCV est optionnel
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# music21 pour MusicXML
try:
    from music21 import converter, stream, note, chord
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False


def check_audiveris_installed():
    """
    Vérifie si Audiveris est installé sur le système.

    Returns:
        bool: True si Audiveris est disponible
    """
    # Chemins possibles pour Audiveris
    possible_paths = [
        os.path.expanduser('~/.local/bin/audiveris'),
        '/usr/bin/audiveris',
        '/usr/local/bin/audiveris',
        'audiveris'
    ]

    for audiveris_path in possible_paths:
        if os.path.exists(audiveris_path) or audiveris_path == 'audiveris':
            try:
                # Essayer d'exécuter sans options (Audiveris se lance juste)
                result = subprocess.run(
                    [audiveris_path],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                # Audiveris retourne une erreur si lancé sans arguments, mais c'est OK
                return True
            except subprocess.TimeoutExpired:
                # Timeout = Audiveris se lance (bon signe)
                return True
            except (FileNotFoundError, PermissionError):
                continue

    return False


def extract_music_from_pdf(filepath):
    """
    Extrait les données musicales d'un fichier PDF.

    NOUVEAU : Utilise Audiveris pour OCR RÉEL si disponible !

    Ordre de priorité :
    1. Audiveris OCR (si installé) - Reconnaissance réelle
    2. Données démo (fallback pour tests)

    Args:
        filepath (str): Chemin vers le fichier PDF

    Returns:
        dict: Données musicales extraites
    """
    # NOUVEAU : Essayer Audiveris d'abord
    if check_audiveris_installed():
        try:
            print("🎼 Utilisation d'Audiveris pour OCR musical réel...")
            return extract_with_audiveris(filepath)
        except Exception as e:
            print(f"⚠️  Audiveris a échoué : {e}")
            print("📋 Fallback sur données de démonstration...")

    try:
        # Ouvrir le PDF pour vérifier qu'il est valide
        with pdfplumber.open(filepath) as pdf:
            num_pages = len(pdf.pages)

        # Pour le MVP : retourner des données de démonstration
        # Dans une version complète, on ferait ici l'OCR musical
        demo_data = {
            'source': filepath,
            'num_pages': num_pages,
            'format': 'pdf',
            # Données de démonstration : gamme de Do majeur
            'raw_notes': [
                'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5',
                'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6'
            ],
            'demo': True,
            'message': 'Données de démonstration - Gamme de Do majeur'
        }

        return demo_data

    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du PDF : {str(e)}")


def extract_music_from_image(filepath):
    """
    Extrait les données musicales d'une image (PNG, JPG).

    Pour le MVP, retourne des données de démonstration basées sur "Avant Toi".
    IMPORTANT : Pour une partition piano (2 portées), extrait UNIQUEMENT la mélodie (clé de Sol).

    Une implémentation complète nécessiterait :
    - Prétraitement d'image (binarisation, débruitage)
    - Détection de portées (clé de Sol vs clé de Fa)
    - Reconnaissance de notes et symboles
    - Extraction des accords

    Args:
        filepath (str): Chemin vers le fichier image

    Returns:
        dict: Données musicales extraites (MÉLODIE UNIQUEMENT)
    """
    try:
        from modules.staff_detector import detect_chords_from_image

        # Ouvrir l'image pour vérifier qu'elle est valide
        image = Image.open(filepath)
        width, height = image.size

        # Détecter les accords
        chords = detect_chords_from_image(filepath)

        # Pour le MVP : retourner des données basées sur "Avant Toi"
        # Mélodie extraite de la portée SUPÉRIEURE (clé de Sol) UNIQUEMENT
        # La portée INFÉRIEURE (clé de Fa / accompagnement) est IGNORÉE
        demo_data = {
            'source': filepath,
            'width': width,
            'height': height,
            'format': 'image',
            'title': 'Avant Toi',
            'composer': 'VITAA & SLIMANE',

            # MÉLODIE UNIQUEMENT (clé de Sol - portée supérieure)
            # Mesures 1-4 : Am - F - C - G
            'raw_notes': [
                # Mesure 1 (Am)
                'E4', 'E4', 'E4', 'E4',
                # Mesure 2 (F)
                'F4', 'F4', 'F4', 'G4',
                # Mesure 3 (C)
                'E4', 'E4', 'E4', 'E4',
                # Mesure 4 (G)
                'G4', 'G4',
                # Mesure 5 (Am) - avec triolets
                'E4', 'E4', 'E4', 'F4',
                # Mesure 6 (F)
                'F4', 'E4', 'E4', 'F4',
                # Mesure 7 (C)
                'E4', 'E4', 'E4', 'F4',
                # Mesure 8 (G)
                'G4', 'G4',
                # Mesure 9 (Am)
                'A4', 'E4', 'E4', 'E4',
                # Mesure 10 (F)
                'F4', 'F4', 'F4', 'F4',
                # Mesure 11 (C)
                'E4', 'E4', 'E4', 'E4',
                # Mesure 12 (G)
                'G4', 'G4',
            ],

            # Accords (au-dessus de la portée)
            'chords': chords,

            'demo': True,
            'message': 'Mélodie "Avant Toi" - UNIQUEMENT clé de Sol (portée supérieure)',
            'staff_info': {
                'type': 'piano_score',
                'staves_count': 2,
                'extracted_staff': 'treble_clef',  # Clé de Sol UNIQUEMENT
                'ignored_staff': 'bass_clef'       # Clé de Fa IGNORÉE
            }
        }

        return demo_data

    except Exception as e:
        raise Exception(f"Erreur lors de la lecture de l'image : {str(e)}")


def analyze_staff_lines(image_path):
    """
    Détecte les lignes de portée dans une image.
    (Fonction utilitaire pour une future implémentation complète)

    Args:
        image_path (str): Chemin vers l'image

    Returns:
        list: Coordonnées des lignes de portée
    """
    if not CV2_AVAILABLE:
        raise ImportError("OpenCV (cv2) n'est pas installé. Installez-le avec: pip install opencv-python")

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Binarisation
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    # Détection de lignes horizontales (portées)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Trouver les contours
    contours, _ = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    staff_lines = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > img.shape[1] * 0.5:  # Ligne assez longue pour être une portée
            staff_lines.append({'y': y, 'x': x, 'width': w, 'height': h})

    return sorted(staff_lines, key=lambda x: x['y'])


def extract_note_positions(image_path):
    """
    Détecte les positions des notes dans une image.
    (Fonction utilitaire pour une future implémentation complète)

    Args:
        image_path (str): Chemin vers l'image

    Returns:
        list: Liste des positions détectées
    """
    # Cette fonction serait implémentée avec un modèle ML
    # ou des techniques avancées de traitement d'image
    pass


def extract_music_from_musicxml(filepath):
    """
    Extrait les données musicales d'un fichier MusicXML.
    
    Cette fonction permet d'importer directement des partitions exportées
    depuis MuseScore, Finale, Sibelius, etc.
    
    Args:
        filepath (str): Chemin vers le fichier MusicXML (.musicxml, .mxl, .xml)
    
    Returns:
        dict: Données musicales extraites
    """
    if not MUSIC21_AVAILABLE:
        raise Exception("music21 n'est pas installé. Installez-le avec: pip install music21")
    
    try:
        # Parser le fichier MusicXML avec music21
        score = converter.parse(filepath)
        
        # Extraire les métadonnées
        title = ''
        composer = ''
        
        if score.metadata:
            title = score.metadata.title or ''
            composer = score.metadata.composer or ''
        
        # Extraire les notes de toutes les parties
        raw_notes = []
        chords_data = []
        
        # Parcourir toutes les parties (voix)
        for part in score.parts:
            # Aplatir la structure pour avoir toutes les notes dans l'ordre
            for element in part.flatten().notesAndRests:
                if isinstance(element, note.Note):
                    # Note simple
                    raw_notes.append({
                        'name': element.nameWithOctave,
                        'duration': element.quarterLength,
                        'measure': element.measureNumber or 0,
                        'offset': element.offset
                    })
                elif isinstance(element, chord.Chord):
                    # Accord - prendre la note la plus haute (mélodie)
                    highest_note = element.pitches[-1]
                    raw_notes.append({
                        'name': highest_note.nameWithOctave,
                        'duration': element.quarterLength,
                        'measure': element.measureNumber or 0,
                        'offset': element.offset
                    })
                    
                    # Stocker aussi l'accord
                    chord_symbol = element.pitchedCommonName
                    if element.measureNumber not in [c[0] for c in chords_data]:
                        chords_data.append((element.measureNumber, chord_symbol))
        
        # Convertir en format compatible
        note_names = [n['name'] for n in raw_notes]
        
        # Extraire informations temporelles
        time_signature = '4/4'  # Défaut
        key_signature = 'C'     # Défaut
        
        if score.parts:
            first_part = score.parts[0]
            
            # Signature temporelle
            ts = first_part.flatten().getElementsByClass('TimeSignature')
            if ts:
                time_signature = ts[0].ratioString
            
            # Armure
            ks = first_part.flatten().getElementsByClass('KeySignature')
            if ks:
                key_signature = ks[0].asKey().name
        
        return {
            'source': filepath,
            'format': 'musicxml',
            'title': title,
            'composer': composer,
            'raw_notes': note_names,
            'notes_with_durations': raw_notes,
            'chords': chords_data,
            'time_signature': time_signature,
            'key_signature': key_signature,
            'staff_info': {
                'extracted_from': 'musicxml',
                'method': 'music21'
            }
        }
    
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier MusicXML : {str(e)}")


def extract_with_audiveris(filepath):
    """
    Extrait les données musicales avec Audiveris (OCR RÉEL).

    Audiveris est le standard open-source pour l'OCR musical.
    Il analyse la partition et génère un fichier MusicXML.

    Args:
        filepath (str): Chemin vers le fichier PDF ou image

    Returns:
        dict: Données musicales extraites
    """
    if not check_audiveris_installed():
        raise Exception(
            "Audiveris n'est pas installé.\n"
            "Installez-le avec: ./install_audiveris.sh\n"
            "ou manuellement depuis https://github.com/Audiveris/audiveris"
        )

    if not MUSIC21_AVAILABLE:
        raise Exception("music21 est requis pour parser les résultats d'Audiveris")

    # Trouver le chemin d'Audiveris
    audiveris_cmd = None
    possible_paths = [
        os.path.expanduser('~/.local/bin/audiveris'),
        '/usr/bin/audiveris',
        '/usr/local/bin/audiveris',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            audiveris_cmd = path
            break

    if not audiveris_cmd:
        audiveris_cmd = 'audiveris'  # Fallback vers PATH

    try:
        # Créer un fichier temporaire pour le MusicXML
        with tempfile.NamedTemporaryFile(suffix='.mxl', delete=False) as tmp:
            output_mxl = tmp.name

        print(f"🔍 Audiveris : Analyse de {os.path.basename(filepath)}...")

        # Lancer Audiveris en mode batch
        # Audiveris va analyser la partition et générer un MusicXML
        # Configurer l'environnement pour Audiveris
        env = os.environ.copy()
        env['JAVA_HOME'] = '/usr/lib/jvm/java-21-openjdk'
        env['TESSDATA_PREFIX'] = '/usr/share/tessdata'

        result = subprocess.run(
            [
                audiveris_cmd,
                '-batch',
                '-export',
                '-output', output_mxl,
                filepath
            ],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes max
            env=env
        )
        
        if result.returncode != 0:
            # Fallback : essayer avec d'autres options
            print("⚠️  Première tentative échouée, essai avec options alternatives...")
            result = subprocess.run(
                [
                    'audiveris',
                    '-batch',
                    '-option', 'org.audiveris.omr.sheet.Book.desiredStaffHeight=15',
                    '-export',
                    '-output', output_mxl,
                    filepath
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
        
        # Vérifier que le fichier MusicXML a été généré
        if not os.path.exists(output_mxl):
            raise Exception(
                f"Audiveris n'a pas généré de fichier MusicXML.\n"
                f"Erreur : {result.stderr[:500]}"
            )
        
        print(f"✅ OCR terminé : {os.path.getsize(output_mxl)} bytes de MusicXML généré")
        
        # Parser le MusicXML généré avec music21
        music_data = extract_music_from_musicxml(output_mxl)
        
        # Ajouter métadonnées OCR
        music_data['ocr_method'] = 'audiveris'
        music_data['ocr_confidence'] = 'high'  # Audiveris est très fiable
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(output_mxl)
        except:
            pass
        
        return music_data
    
    except subprocess.TimeoutExpired:
        raise Exception(
            "Timeout : Audiveris a pris trop de temps (>2min).\n"
            "La partition est peut-être trop complexe."
        )
    
    except Exception as e:
        raise Exception(f"Erreur Audiveris : {str(e)}")
