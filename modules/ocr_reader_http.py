"""
Module de lecture de partitions via Audiveris HTTP API

Ce module fournit une interface pour utiliser Audiveris via son service HTTP
au lieu d'appeler l'exécutable en ligne de commande.
"""
import os
import logging
import requests
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AudiverisHTTPClient:
    """Client HTTP pour le service Audiveris"""

    def __init__(self, service_url: Optional[str] = None):
        """
        Initialise le client HTTP

        Args:
            service_url: URL du service Audiveris (défaut: depuis variable d'environnement)
        """
        self.service_url = service_url or os.getenv('AUDIVERIS_SERVICE_URL', 'http://audiveris:8080')
        self._check_service()

    def _check_service(self) -> bool:
        """Vérifie que le service Audiveris est accessible"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"Service Audiveris accessible à: {self.service_url}")
                return True
            else:
                logger.warning(f"Service Audiveris répond avec le code {response.status_code}")
                return False
        except requests.ConnectionError:
            logger.error(f"Impossible de se connecter au service Audiveris à {self.service_url}")
            raise ConnectionError(f"Service Audiveris non accessible à {self.service_url}")
        except requests.Timeout:
            logger.error("Timeout lors de la connexion au service Audiveris")
            raise TimeoutError("Service Audiveris ne répond pas")

    def read_partition(self, input_file: Path, output_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Lit une partition et extrait les données musicales via l'API HTTP

        Args:
            input_file: Fichier PDF ou image de la partition
            output_dir: Dossier de sortie pour les fichiers MusicXML (local, pour référence)

        Returns:
            Dictionnaire contenant les données extraites ou None en cas d'erreur
        """
        logger.info(f"Envoi de la partition au service OCR: {input_file}")

        if not input_file.exists():
            logger.error(f"Fichier non trouvé: {input_file}")
            return None

        try:
            # Envoyer le fichier au service Audiveris
            with open(input_file, 'rb') as f:
                files = {'file': (input_file.name, f, self._get_mimetype(input_file))}

                logger.info(f"Envoi de la requête POST à {self.service_url}/ocr")
                response = requests.post(
                    f"{self.service_url}/ocr",
                    files=files,
                    timeout=300  # 5 minutes max
                )

            if response.status_code != 200:
                logger.error(f"Erreur du service OCR: {response.status_code} - {response.text}")
                return None

            result = response.json()

            if not result.get('success'):
                logger.error(f"OCR a échoué: {result.get('error')}")
                return None

            # Télécharger le fichier MusicXML généré
            output_file_path = result.get('output_file')
            logger.info(f"Fichier MusicXML généré: {output_file_path}")

            # Télécharger le fichier
            download_url = f"{self.service_url}/download/{output_file_path}"
            musicxml_response = requests.get(download_url, timeout=30)

            if musicxml_response.status_code != 200:
                logger.error(f"Erreur lors du téléchargement du MusicXML: {musicxml_response.status_code}")
                return None

            # Sauvegarder le fichier localement
            output_dir.mkdir(parents=True, exist_ok=True)
            local_musicxml_path = output_dir / Path(output_file_path).name
            local_musicxml_path.write_bytes(musicxml_response.content)

            logger.info(f"Fichier MusicXML sauvegardé localement: {local_musicxml_path}")

            # Parser le fichier MusicXML
            return self.parse_musicxml(local_musicxml_path)

        except requests.Timeout:
            logger.error("Timeout lors de l'appel au service OCR (> 5 minutes)")
            return None
        except requests.ConnectionError as e:
            logger.error(f"Erreur de connexion au service OCR: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au service OCR: {e}")
            return None

    def _get_mimetype(self, file_path: Path) -> str:
        """Retourne le type MIME du fichier"""
        extension = file_path.suffix.lower()
        mimetypes = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff'
        }
        return mimetypes.get(extension, 'application/octet-stream')

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
    client = AudiverisHTTPClient()
    return client.read_partition(pdf_path, output_dir)
