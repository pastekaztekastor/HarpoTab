"""
Tests pour le module ocr_reader
"""
import pytest
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ocr_reader import AudiverisOCR, read_partition_from_pdf


def test_audiveris_initialization():
    """Test de l'initialisation d'Audiveris"""
    try:
        ocr = AudiverisOCR()
        assert ocr.audiveris_path.exists(), "Audiveris devrait être trouvé"
        print("✅ Test initialisation: OK")
    except FileNotFoundError:
        pytest.skip("Audiveris n'est pas installé")


def test_audiveris_path_custom():
    """Test avec un chemin personnalisé"""
    with pytest.raises(FileNotFoundError):
        AudiverisOCR(audiveris_path='/path/invalid/audiveris')
    print("✅ Test chemin invalide: OK")


def test_parse_simple_musicxml():
    """Test du parsing d'un fichier MusicXML simple"""
    # Créer un fichier temporaire pour Audiveris (pas utilisé pour ce test, juste pour init)
    import tempfile
    temp_audiveris = Path(tempfile.mktemp())
    temp_audiveris.touch()

    try:
        ocr = AudiverisOCR(audiveris_path=str(temp_audiveris))

        # Créer un fichier MusicXML minimal pour le test
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <work>
    <work-title>Test Piece</work-title>
  </work>
  <identification>
    <creator type="composer">Test Composer</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
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
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""

        # Sauvegarder le XML de test
        test_file = Path("/tmp/test_musicxml.xml")
        test_file.write_text(test_xml)

        # Parser le fichier
        result = ocr.parse_musicxml(test_file)

        # Vérifications
        assert result is not None, "Le parsing devrait réussir"
        assert 'metadata' in result, "Devrait contenir metadata"
        assert 'parts' in result, "Devrait contenir parts"
        assert result['metadata']['title'] == 'Test Piece', "Titre devrait être extrait"
        assert result['metadata']['composer'] == 'Test Composer', "Compositeur devrait être extrait"
        assert result['metadata']['time_signature'] == '4/4', "Signature rythmique devrait être 4/4"
        assert len(result['parts']) == 1, "Devrait avoir une partie"
        assert len(result['parts'][0]['measures']) == 1, "Devrait avoir une mesure"
        assert len(result['parts'][0]['measures'][0]['notes']) == 1, "Devrait avoir une note"

        note = result['parts'][0]['measures'][0]['notes'][0]
        assert note['type'] == 'note', "Devrait être une note"
        assert note['pitch']['step'] == 'C', "Note devrait être C"
        assert note['pitch']['octave'] == 4, "Octave devrait être 4"

        # Nettoyer
        test_file.unlink()

        print("✅ Test parsing MusicXML: OK")

    except Exception as e:
        pytest.fail(f"Test parsing MusicXML failed: {e}")
    finally:
        # Nettoyer le fichier temporaire Audiveris
        temp_audiveris.unlink(missing_ok=True)


if __name__ == "__main__":
    """Exécuter les tests"""
    print("=== Tests ocr_reader ===\n")

    try:
        test_audiveris_initialization()
    except Exception as e:
        print(f"❌ Test initialisation: {e}")

    try:
        test_audiveris_path_custom()
    except Exception as e:
        print(f"❌ Test chemin invalide: {e}")

    try:
        test_parse_simple_musicxml()
    except Exception as e:
        print(f"❌ Test parsing MusicXML: {e}")

    print("\n=== Tests terminés ===")
