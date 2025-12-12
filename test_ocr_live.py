#!/usr/bin/env python3
"""
Script de test pour le module OCR
Teste la lecture d'une partition avec Audiveris
"""
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le projet au path
sys.path.insert(0, str(Path(__file__).parent))

from modules.ocr_reader import AudiverisOCR


def test_ocr_partition(partition_path: str):
    """
    Teste l'OCR sur une partition

    Args:
        partition_path: Chemin vers le fichier PDF ou image
    """
    print("=" * 60)
    print("TEST OCR - HARPOTAB")
    print("=" * 60)
    print()

    # Vérifier que le fichier existe
    input_file = Path(partition_path)
    if not input_file.exists():
        print(f"❌ Erreur: Fichier non trouvé: {partition_path}")
        return

    print(f"📄 Fichier d'entrée: {input_file}")
    print(f"📦 Taille: {input_file.stat().st_size / 1024:.2f} KB")
    print()

    # Créer le dossier de sortie
    output_dir = Path("temp/ocr_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Dossier de sortie: {output_dir}")
    print()

    # Initialiser l'OCR
    print("🔧 Initialisation d'Audiveris...")
    try:
        ocr = AudiverisOCR()
        print("✅ Audiveris initialisé")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return

    print()
    print("🎵 Lancement de l'OCR musical...")
    print("⏳ Cela peut prendre quelques minutes...")
    print()

    # Lancer l'OCR
    result = ocr.read_partition(input_file, output_dir)

    if result is None:
        print("❌ Échec de l'OCR")
        print()
        print("💡 Vérifiez que:")
        print("  - La partition est de bonne qualité")
        print("  - Le fichier n'est pas corrompu")
        print("  - Audiveris est correctement installé")
        return

    # Afficher les résultats
    print()
    print("=" * 60)
    print("✅ OCR TERMINÉ AVEC SUCCÈS")
    print("=" * 60)
    print()

    # Métadonnées
    metadata = result.get('metadata', {})
    print("📋 MÉTADONNÉES:")
    print(f"  Titre: {metadata.get('title', 'N/A')}")
    print(f"  Compositeur: {metadata.get('composer', 'N/A')}")
    print(f"  Tonalité: {metadata.get('key', 'N/A')}")
    print(f"  Signature: {metadata.get('time_signature', 'N/A')}")
    print(f"  Tempo: {metadata.get('tempo', 'N/A')} BPM")
    print()

    # Parties
    parts = result.get('parts', [])
    print(f"🎼 PARTIES MUSICALES: {len(parts)}")
    print()

    for i, part in enumerate(parts, 1):
        part_id = part.get('id', 'N/A')
        measures = part.get('measures', [])
        total_notes = sum(len(m.get('notes', [])) for m in measures)

        print(f"  Partie {i} (ID: {part_id}):")
        print(f"    - Mesures: {len(measures)}")
        print(f"    - Notes totales: {total_notes}")

        # Afficher les 5 premières notes
        if measures and measures[0].get('notes'):
            print(f"    - Premières notes:")
            for note in measures[0]['notes'][:5]:
                if note['type'] == 'note':
                    pitch = note.get('pitch', {})
                    step = pitch.get('step', '?')
                    octave = pitch.get('octave', '?')
                    alter = pitch.get('alter', 0)
                    alteration = {-1: '♭', 0: '', 1: '♯'}.get(alter, '')
                    print(f"      • {step}{alteration}{octave} ({note.get('note_type', '?')})")
                else:
                    print(f"      • Silence ({note.get('note_type', '?')})")
        print()

    # Fichier source
    print(f"📁 Fichier MusicXML: {result.get('source_file', 'N/A')}")
    print()
    print("=" * 60)
    print("🎉 Test terminé avec succès!")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ocr_live.py <chemin_partition.pdf>")
        print()
        print("Exemple:")
        print("  python test_ocr_live.py partition.pdf")
        print("  python test_ocr_live.py ~/Downloads/sheet_music.pdf")
        sys.exit(1)

    partition_path = sys.argv[1]
    test_ocr_partition(partition_path)
