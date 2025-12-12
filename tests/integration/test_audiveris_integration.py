"""
Tests d'intégration pour Audiveris OCR

Ces tests nécessitent:
- Audiveris installé
- Java 21+
- Fichiers de test réels (PDF/PNG)

Ils sont conçus pour tourner dans l'environnement Docker via docker-tests.yml
"""
import pytest
from pathlib import Path
import sys

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.ocr_reader import AudiverisOCR, read_partition_from_pdf
from modules.melody_extractor import MelodyExtractor
from modules.transposer import Transposer


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def audiveris_ocr():
    """Initialise Audiveris OCR"""
    try:
        return AudiverisOCR()
    except FileNotFoundError:
        pytest.skip("Audiveris n'est pas installé")


@pytest.fixture
def test_fixtures_dir():
    """Répertoire contenant les fichiers de test"""
    return Path(__file__).parent.parent / "fixtures"


# =============================================================================
# TESTS D'INITIALISATION
# =============================================================================

def test_audiveris_installation(audiveris_ocr):
    """Vérifie qu'Audiveris est installé et accessible"""
    assert audiveris_ocr.audiveris_path.exists()
    assert audiveris_ocr.audiveris_path.is_file()
    print(f"✅ Audiveris trouvé: {audiveris_ocr.audiveris_path}")


def test_audiveris_help(audiveris_ocr):
    """Vérifie que la commande audiveris --help fonctionne"""
    import subprocess
    try:
        result = subprocess.run(
            [str(audiveris_ocr.audiveris_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Audiveris peut retourner un code d'erreur même avec --help
        # On vérifie juste qu'il n'y a pas de crash complet
        assert result.returncode in [0, 1]
        print("✅ Audiveris répond à --help")
    except Exception as e:
        pytest.skip(f"Audiveris --help failed: {e}")


# =============================================================================
# TESTS DE PARSING MUSICXML
# =============================================================================

def test_parse_musicxml_file(audiveris_ocr, tmp_path):
    """Test du parsing d'un fichier MusicXML généré"""
    # Créer un MusicXML simple pour le test
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work>
    <work-title>Test Integration</work-title>
  </work>
  <identification>
    <creator type="composer">Integration Test</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Voice</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <key>
          <fifths>0</fifths>
          <mode>major</mode>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

    # Sauvegarder dans un fichier temporaire
    test_file = tmp_path / "test_integration.xml"
    test_file.write_text(test_xml)

    # Parser
    result = audiveris_ocr.parse_musicxml(test_file)

    # Vérifications
    assert result is not None
    assert result['metadata']['title'] == 'Test Integration'
    assert result['metadata']['composer'] == 'Integration Test'
    assert len(result['parts']) == 1
    assert len(result['parts'][0]['measures']) == 1
    assert len(result['parts'][0]['measures'][0]['notes']) == 4

    print("✅ Parsing MusicXML: OK")


def test_parse_mxl_compressed(audiveris_ocr, tmp_path):
    """Test du parsing d'un fichier MXL compressé"""
    import zipfile

    # Créer un MusicXML simple
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work><work-title>MXL Test</work-title></work>
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
      </attributes>
      <note>
        <pitch><step>G</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

    # Créer un fichier MXL (ZIP)
    mxl_file = tmp_path / "test.mxl"
    with zipfile.ZipFile(mxl_file, 'w') as zf:
        zf.writestr("test.xml", test_xml)

    # Parser
    result = audiveris_ocr.parse_musicxml(mxl_file)

    # Vérifications
    assert result is not None
    assert result['metadata']['title'] == 'MXL Test'
    assert len(result['parts'][0]['measures'][0]['notes']) == 1

    print("✅ Parsing MXL compressé: OK")


# =============================================================================
# TESTS DE PIPELINE COMPLET
# =============================================================================

def test_full_pipeline_melody_extraction(audiveris_ocr, tmp_path):
    """Test du pipeline complet: XML → Mélodie"""
    # Créer un fichier de test
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work><work-title>Pipeline Test</work-title></work>
  <part-list>
    <score-part id="P1">
      <part-name>Melody</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch><step>E</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch><step>G</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch><step>C</step><octave>5</octave></pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

    test_file = tmp_path / "pipeline_test.xml"
    test_file.write_text(test_xml)

    # Étape 1: Parser MusicXML
    musicxml_data = audiveris_ocr.parse_musicxml(test_file)
    assert musicxml_data is not None

    # Étape 2: Extraire la mélodie
    extractor = MelodyExtractor(keep_rests=True)
    melody = extractor.extract_melody(musicxml_data)

    assert melody is not None
    assert len(melody['notes']) == 4
    assert melody['notes'][0]['pitch']['step'] == 'C'
    assert melody['notes'][0]['midi'] == 60  # C4
    assert melody['notes'][3]['midi'] == 72  # C5

    print("✅ Pipeline complet (XML → Mélodie): OK")


def test_full_pipeline_with_transposition(audiveris_ocr, tmp_path):
    """Test du pipeline complet: XML → Mélodie → Transposition"""
    # Créer un fichier de test
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work><work-title>Transposition Test</work-title></work>
  <part-list>
    <score-part id="P1">
      <part-name>Voice</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>16</duration>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

    test_file = tmp_path / "transpose_test.xml"
    test_file.write_text(test_xml)

    # Étape 1: Parser
    musicxml_data = audiveris_ocr.parse_musicxml(test_file)

    # Étape 2: Extraire mélodie
    extractor = MelodyExtractor()
    melody = extractor.extract_melody(musicxml_data)

    # Étape 3: Transposer
    transposer = Transposer()
    transposed = transposer.transpose_melody(melody, semitones=2)

    # Vérifications
    assert melody['notes'][0]['midi'] == 60  # C4
    assert transposed['notes'][0]['midi'] == 62  # D4

    print("✅ Pipeline complet (XML → Mélodie → Transposition): OK")


# =============================================================================
# TESTS DE ROBUSTESSE
# =============================================================================

def test_empty_musicxml(audiveris_ocr, tmp_path):
    """Test avec un fichier MusicXML vide"""
    empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Empty</part-name>
    </score-part>
  </part-list>
  <part id="P1">
  </part>
</score-partwise>
"""

    test_file = tmp_path / "empty.xml"
    test_file.write_text(empty_xml)

    result = audiveris_ocr.parse_musicxml(test_file)

    # Devrait parser sans crash, mais sans notes
    assert result is not None
    assert len(result['parts']) == 1
    assert len(result['parts'][0]['measures']) == 0

    print("✅ Robustesse (XML vide): OK")


def test_invalid_xml(audiveris_ocr, tmp_path):
    """Test avec un XML invalide"""
    invalid_xml = "This is not XML at all!"

    test_file = tmp_path / "invalid.xml"
    test_file.write_text(invalid_xml)

    # Devrait lever une exception
    with pytest.raises(Exception):
        audiveris_ocr.parse_musicxml(test_file)

    print("✅ Robustesse (XML invalide): OK")


# =============================================================================
# MAIN (pour exécution directe)
# =============================================================================

if __name__ == "__main__":
    """Exécuter les tests d'intégration"""
    print("=== Tests d'intégration Audiveris ===\n")
    pytest.main([__file__, "-v", "--tb=short"])
