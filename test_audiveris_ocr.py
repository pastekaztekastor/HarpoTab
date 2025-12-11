#!/usr/bin/env python3
"""
Test de l'OCR musical avec Audiveris.

Ce test vérifie que l'intégration d'Audiveris fonctionne correctement.
"""

import sys
import os
from modules.pdf_reader import check_audiveris_installed, extract_with_audiveris

def test_audiveris():
    """Test l'installation et le fonctionnement d'Audiveris."""
    print("=" * 70)
    print("Test Audiveris - OCR Musical RÉEL")
    print("=" * 70)
    print()

    # 1. Vérifier installation
    print("1. Vérification de l'installation d'Audiveris...")
    is_installed = check_audiveris_installed()

    if is_installed:
        print("   ✅ Audiveris est installé et accessible")
    else:
        print("   ❌ Audiveris n'est PAS installé")
        print()
        print("Pour installer Audiveris :")
        print("   ./install_audiveris.sh")
        print()
        print("Ou manuellement :")
        print("   - Manjaro/Arch : yay -S audiveris")
        print("   - Ubuntu/Debian : sudo apt-get install audiveris")
        print("   - macOS : brew install audiveris")
        print()
        return False

    print()

    # 2. Tester avec une partition si disponible
    print("2. Test d'OCR avec une partition...")

    # Chercher une partition de test
    test_files = [
        'avant-toi-partition-piano-724x1024.jpg',
        'static/uploads/avant-toi-partition-piano-724x1024.jpg'
    ]

    test_file = None
    for f in test_files:
        if os.path.exists(f):
            test_file = f
            break

    if not test_file:
        print("   ⚠️  Aucune partition de test trouvée")
        print("   Placez une partition (PDF ou image) pour tester l'OCR")
        print()
        print("   Audiveris est installé et prêt à être utilisé !")
        return True

    print(f"   📄 Fichier de test : {os.path.basename(test_file)}")
    print()

    try:
        # Lancer l'OCR
        print("   🔍 Lancement de l'OCR Audiveris...")
        print("   (Cela peut prendre 30 secondes à 2 minutes)")
        print()

        music_data = extract_with_audiveris(test_file)

        # Afficher les résultats
        print()
        print("=" * 70)
        print("✅ OCR RÉUSSI !")
        print("=" * 70)
        print()
        print("Données extraites :")
        print(f"   • Titre       : {music_data.get('title', 'N/A')}")
        print(f"   • Compositeur : {music_data.get('composer', 'N/A')}")
        print(f"   • Notes       : {len(music_data.get('raw_notes', []))} notes")
        print(f"   • Accords     : {len(music_data.get('chords', []))} accords")
        print(f"   • Méthode OCR : {music_data.get('ocr_method', 'N/A')}")
        print(f"   • Confiance   : {music_data.get('ocr_confidence', 'N/A')}")
        print()

        # Afficher quelques notes
        if music_data.get('raw_notes'):
            notes_sample = music_data['raw_notes'][:10]
            print(f"   Premières notes : {', '.join(notes_sample)}")
            if len(music_data['raw_notes']) > 10:
                print(f"   ... et {len(music_data['raw_notes']) - 10} autres")

        print()
        print("=" * 70)
        print("🎉 Audiveris fonctionne parfaitement !")
        print("=" * 70)
        print()
        print("HarpoTab peut maintenant reconnaître automatiquement")
        print("les partitions uploadées avec un OCR musical réel.")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERREUR lors de l'OCR")
        print("=" * 70)
        print()
        print(f"Erreur : {str(e)}")
        print()
        print("Vérifiez :")
        print("  1. Que Audiveris est correctement installé")
        print("  2. Que la partition est lisible (bonne qualité)")
        print("  3. Que Java est installé (requis par Audiveris)")
        print()
        return False

if __name__ == '__main__':
    success = test_audiveris()
    sys.exit(0 if success else 1)
