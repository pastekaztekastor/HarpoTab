"""
Module de lecture de partitions via OCR musical (Audiveris)

Ce module fournit une interface pour utiliser Audiveris en ligne de commande
et parser les fichiers MusicXML générés.
"""
import subprocess
import logging
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AudiverisOCR:
    """Interface avec Audiveris pour la lecture de partitions"""

    def __init__(self, audiveris_path: str = '/usr/local/bin/audiveris'):
        """
        Initialise le lecteur OCR

        Args:
            audiveris_path: Chemin vers l'exécutable Audiveris
        """
        self.audiveris_path = Path(audiveris_path)
        self._check_audiveris()

    def _check_audiveris(self) -> bool:
        """Vérifie que Audiveris est installé et accessible"""
        if not self.audiveris_path.exists():
            logger.error(f"Audiveris non trouvé à: {self.audiveris_path}")
            raise FileNotFoundError(f"Audiveris n'est pas installé à {self.audiveris_path}")

        logger.info(f"Audiveris trouvé à: {self.audiveris_path}")
        return True

    def read_partition(self, input_file: Path, output_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Lit une partition et extrait les données musicales

        Args:
            input_file: Fichier PDF ou image de la partition
            output_dir: Dossier de sortie pour les fichiers MusicXML

        Returns:
            Dictionnaire contenant les données extraites ou None en cas d'erreur
        """
        logger.info(f"Lecture de la partition: {input_file}")

        if not input_file.exists():
            logger.error(f"Fichier non trouvé: {input_file}")
            return None

        # Créer le dossier de sortie
        output_dir.mkdir(parents=True, exist_ok=True)

        # Commande Audiveris en mode batch
        command = [
            str(self.audiveris_path),
            '-batch',
            '-export',
            '-output', str(output_dir),
            str(input_file)
        ]

        logger.info(f"Commande Audiveris: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes max
            )

            if result.returncode != 0:
                logger.error(f"Erreur Audiveris: {result.stderr}")
                return None

            logger.info("Audiveris terminé avec succès")

            # Chercher le fichier MusicXML généré
            # Audiveris génère un fichier avec le même nom de base que l'entrée
            base_name = input_file.stem
            expected_mxl = output_dir / f"{base_name}.mxl"
            expected_xml = output_dir / f"{base_name}.xml"

            if expected_mxl.exists():
                musicxml_file = expected_mxl
            elif expected_xml.exists():
                musicxml_file = expected_xml
            else:
                # Fallback: chercher n'importe quel fichier MusicXML récent
                musicxml_files = sorted(
                    list(output_dir.glob("*.mxl")) + list(output_dir.glob("*.xml")),
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )
                if not musicxml_files:
                    logger.error("Aucun fichier MusicXML généré")
                    return None
                musicxml_file = musicxml_files[0]
                logger.warning(f"Fichier attendu '{base_name}.mxl' non trouvé, utilisation de: {musicxml_file.name}")

            logger.info(f"Fichier MusicXML trouvé: {musicxml_file}")

            return self.parse_musicxml(musicxml_file)

        except subprocess.TimeoutExpired:
            logger.error("Timeout Audiveris (> 5 minutes)")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution d'Audiveris: {e}")
            return None

    def parse_musicxml(self, musicxml_file: Path) -> Dict[str, Any]:
        """
        Parse un fichier MusicXML et extrait les informations

        Args:
            musicxml_file: Fichier MusicXML (.xml) ou MXL (.mxl compressé) généré par Audiveris

        Returns:
            Dictionnaire structuré avec les données musicales
        """
        logger.info(f"Parsing MusicXML: {musicxml_file}")

        try:
            # Gérer les fichiers .mxl (compressés)
            if musicxml_file.suffix.lower() == '.mxl':
                logger.info("Fichier MXL détecté - décompression en cours")
                with zipfile.ZipFile(musicxml_file, 'r') as zip_ref:
                    # Trouver le fichier XML principal (pas dans META-INF)
                    xml_files = [f for f in zip_ref.namelist()
                                if f.endswith('.xml') and 'META-INF' not in f]

                    if not xml_files:
                        logger.error("Aucun fichier XML trouvé dans l'archive MXL")
                        return None

                    main_xml = xml_files[0]
                    logger.info(f"Extraction de {main_xml} depuis l'archive MXL")

                    with zip_ref.open(main_xml) as xml_file:
                        tree = ET.parse(xml_file)
            else:
                # Fichier XML non compressé
                tree = ET.parse(musicxml_file)

            root = tree.getroot()

            # Extraire les métadonnées
            metadata = self._extract_metadata(root)

            # Extraire les mesures et notes
            parts = self._extract_parts(root)

            result = {
                'metadata': metadata,
                'parts': parts,
                'source_file': str(musicxml_file)
            }

            logger.info(f"MusicXML parsé avec succès: {len(parts)} partie(s)")
            return result

        except ET.ParseError as e:
            logger.error(f"Erreur de parsing XML: {e}")
            return None
        except zipfile.BadZipFile as e:
            logger.error(f"Erreur: fichier MXL corrompu: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors du parsing MusicXML: {e}")
            return None

    def _extract_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """Extrait les métadonnées du MusicXML"""
        metadata = {
            'title': None,
            'composer': None,
            'key': None,
            'time_signature': None,
            'tempo': None
        }

        # Titre et compositeur
        work = root.find('.//work/work-title')
        if work is not None:
            metadata['title'] = work.text

        creator = root.find('.//creator[@type="composer"]')
        if creator is not None:
            metadata['composer'] = creator.text

        # Tonalité (key signature)
        key = root.find('.//attributes/key')
        if key is not None:
            fifths = key.find('fifths')
            mode = key.find('mode')
            if fifths is not None:
                metadata['key'] = {
                    'fifths': int(fifths.text),
                    'mode': mode.text if mode is not None else 'major'
                }

        # Signature rythmique (time signature)
        time = root.find('.//attributes/time')
        if time is not None:
            beats = time.find('beats')
            beat_type = time.find('beat-type')
            if beats is not None and beat_type is not None:
                metadata['time_signature'] = f"{beats.text}/{beat_type.text}"

        # Tempo
        sound = root.find('.//sound[@tempo]')
        if sound is not None:
            metadata['tempo'] = int(float(sound.get('tempo')))

        return metadata

    def _extract_parts(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extrait les parties (instruments/voix) et leurs notes"""
        parts = []

        for part in root.findall('.//part'):
            part_id = part.get('id')
            measures = []

            for measure in part.findall('measure'):
                measure_number = measure.get('number')
                notes = self._extract_notes(measure)

                measures.append({
                    'number': int(measure_number) if measure_number else 0,
                    'notes': notes
                })

            parts.append({
                'id': part_id,
                'measures': measures
            })

        return parts

    def _extract_notes(self, measure: ET.Element) -> List[Dict[str, Any]]:
        """Extrait les notes d'une mesure"""
        notes = []

        for note in measure.findall('note'):
            note_data = {}

            # Note ou silence
            if note.find('rest') is not None:
                note_data['type'] = 'rest'
            else:
                note_data['type'] = 'note'

                pitch = note.find('pitch')
                if pitch is not None:
                    step = pitch.find('step')
                    octave = pitch.find('octave')
                    alter = pitch.find('alter')

                    note_data['pitch'] = {
                        'step': step.text if step is not None else None,
                        'octave': int(octave.text) if octave is not None else None,
                        'alter': int(alter.text) if alter is not None else 0
                    }

            # Durée
            duration = note.find('duration')
            if duration is not None:
                note_data['duration'] = int(duration.text)

            # Type de note (quarter, eighth, etc.)
            note_type = note.find('type')
            if note_type is not None:
                note_data['note_type'] = note_type.text

            notes.append(note_data)

        return notes


def read_partition_from_pdf(pdf_path: Path, output_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Fonction helper pour lire une partition depuis un PDF

    Args:
        pdf_path: Chemin du fichier PDF
        output_dir: Dossier de sortie

    Returns:
        Données musicales extraites
    """
    ocr = AudiverisOCR()
    return ocr.read_partition(pdf_path, output_dir)
