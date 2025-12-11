#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités de jouabilité et transposition automatique.
"""

import sys
from modules.pdf_reader import extract_music_from_image
from modules.music_parser import parse_musical_notes
from modules.harmonica import analyze_playability, find_best_tonalities

def test_playability_features():
    """Test la vérification de jouabilité et la recherche de tonalités."""
    print("=" * 70)
    print("Test Jouabilité et Transposition Automatique")
    print("=" * 70)
    print()

    # 1. Charger les données
    print("1. Chargement de la partition 'Avant Toi'...")
    music_data = extract_music_from_image('avant-toi-partition-piano-724x1024.jpg')
    notes = parse_musical_notes(music_data)
    print(f"   ✓ {len(notes)} notes chargées")
    print()

    # 2. Tester avec tonalité C
    print("2. Analyse de jouabilité avec harmonica en DO (C)...")
    playability_c = analyze_playability(notes, 'diatonic', 'C')

    print(f"   Total notes         : {playability_c['total_notes']}")
    print(f"   Notes jouables      : {playability_c['playable_notes']}")
    print(f"   Notes non jouables  : {playability_c['unplayable_notes']}")
    print(f"   Jouabilité          : {playability_c['playability_percentage']:.1f}%")
    print(f"   100% jouable        : {'✓ OUI' if playability_c['is_fully_playable'] else '✗ NON'}")

    if playability_c['missing_notes']:
        print(f"   Notes manquantes    : {', '.join(playability_c['missing_notes'])}")

    print()

    # 3. Tester avec différentes tonalités
    print("3. Test avec d'autres tonalités...")
    tonalities_to_test = ['G', 'A', 'D', 'E', 'F', 'Bb']

    for tonality in tonalities_to_test:
        playability = analyze_playability(notes, 'diatonic', tonality)
        status = "✓" if playability['is_fully_playable'] else "✗"
        print(f"   {status} {tonality:2s} : {playability['playability_percentage']:5.1f}% "
              f"({playability['playable_notes']}/{playability['total_notes']} notes)")

    print()

    # 4. Recherche automatique des meilleures tonalités
    print("4. Recherche automatique des tonalités optimales (min 80%)...")
    best_tonalities = find_best_tonalities(notes, 'diatonic', min_playability=80.0)

    if not best_tonalities:
        print("   ✗ Aucune tonalité ne permet de jouer au moins 80% de la mélodie")
    else:
        print(f"   ✓ {len(best_tonalities)} tonalité(s) trouvée(s):")
        print()

        for i, tonality_info in enumerate(best_tonalities, 1):
            print(f"   {i}. Harmonica en {tonality_info['tonality']}")
            print(f"      Jouabilité : {tonality_info['playability']:.1f}%")
            print(f"      Notes      : {tonality_info['playable_notes']}/{tonality_info['total_notes']}")

            if tonality_info['is_fully_playable']:
                print(f"      Statut     : ✅ 100% JOUABLE !")
            else:
                print(f"      Manquantes : {', '.join(tonality_info['missing_notes'])}")
            print()

    print("=" * 70)
    print("✓ TEST TERMINÉ")
    print("=" * 70)
    print()

    # Résumé
    if best_tonalities and best_tonalities[0]['is_fully_playable']:
        print(f"🎯 RECOMMANDATION : Utiliser un harmonica en {best_tonalities[0]['tonality']}")
        print("   Cela permet de jouer 100% de la mélodie !")
    elif best_tonalities:
        print(f"🎯 RECOMMANDATION : Utiliser un harmonica en {best_tonalities[0]['tonality']}")
        print(f"   ({best_tonalities[0]['playability']:.1f}% de la mélodie jouable)")
    else:
        print("⚠️  ATTENTION : Cette mélodie est difficile à jouer sur harmonica diatonique")
        print("    Envisagez un harmonica chromatique.")

    print()
    return True

if __name__ == '__main__':
    success = test_playability_features()
    sys.exit(0 if success else 1)
