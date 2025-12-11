#!/usr/bin/env python3
"""
Script de vérification système pour HarpoTab.
Vérifie toutes les dépendances et affiche un rapport complet.
"""

import sys
import os
import subprocess
import importlib.util

def check_command(command, description):
    """Vérifie si une commande est disponible."""
    try:
        result = subprocess.run(
            ['which', command],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Essayer d'obtenir la version
            try:
                version_result = subprocess.run(
                    [command, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = version_result.stdout.split('\n')[0] if version_result.returncode == 0 else "installé"
            except:
                version = "installé"
            return True, version
        return False, None
    except:
        return False, None

def check_python_module(module_name, description):
    """Vérifie si un module Python est installé."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'installé')
                return True, version
            except:
                return True, 'installé'
        return False, None
    except:
        return False, None

def main():
    print("=" * 70)
    print("  HarpoTab - Vérification Système")
    print("=" * 70)
    print()

    # Vérifications système
    checks = {
        'Commandes système': [
            ('python3', 'Python 3'),
            ('lilypond', 'LilyPond (génération PDF professionnelle)'),
            ('audiveris', 'Audiveris (OCR musical RÉEL)'),
        ],
        'Modules Python essentiels': [
            ('flask', 'Flask (serveur web)'),
            ('reportlab', 'ReportLab (PDF basique)'),
            ('PIL', 'Pillow (traitement images)'),
            ('pdfplumber', 'PDFPlumber (lecture PDF)'),
        ],
        'Modules Python avancés': [
            ('music21', 'music21 (MusicXML parsing)'),
            ('cv2', 'OpenCV (analyse images - optionnel)'),
        ]
    }

    results = {
        'ok': 0,
        'missing': 0,
        'optional_missing': 0
    }

    for category, items in checks.items():
        print(f"📦 {category}")
        print("-" * 70)

        for item, description in items:
            # Déterminer si c'est une commande ou un module
            if category.startswith('Modules'):
                installed, version = check_python_module(item, description)
                is_optional = 'optionnel' in description.lower()
            else:
                installed, version = check_command(item, description)
                is_optional = item in ['audiveris', 'lilypond']

            if installed:
                status = "✅"
                results['ok'] += 1
                print(f"  {status} {description:50} {version}")
            else:
                if is_optional:
                    status = "⚠️ "
                    results['optional_missing'] += 1
                else:
                    status = "❌"
                    results['missing'] += 1
                print(f"  {status} {description:50} NON INSTALLÉ")

        print()

    # Vérifications des dossiers
    print("📁 Dossiers")
    print("-" * 70)
    required_dirs = [
        'static/uploads',
        'static/output',
        'static/lilypond',
        'data',
        'modules',
        'templates'
    ]

    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}")

    print()

    # Résumé
    print("=" * 70)
    print("  Résumé")
    print("=" * 70)
    print()
    print(f"  ✅ Installé        : {results['ok']}")
    print(f"  ❌ Manquant        : {results['missing']}")
    print(f"  ⚠️  Optionnel      : {results['optional_missing']}")
    print()

    # Recommandations
    if results['missing'] > 0:
        print("🔧 Actions requises:")
        print("-" * 70)
        print("  1. Exécuter : ./setup.sh")
        print("  2. Vérifier votre connexion internet")
        print()

    if results['optional_missing'] > 0:
        print("💡 Améliorations recommandées:")
        print("-" * 70)

        # Vérifier spécifiquement Audiveris
        audiveris_installed, _ = check_command('audiveris', 'Audiveris')
        if not audiveris_installed:
            print("  • Installer Audiveris pour OCR RÉEL:")
            print("      ./install_audiveris.sh")
            print()

        # Vérifier spécifiquement LilyPond
        lilypond_installed, _ = check_command('lilypond', 'LilyPond')
        if not lilypond_installed:
            print("  • Installer LilyPond pour PDF professionnels:")
            print("      sudo pacman -S lilypond  # Manjaro/Arch")
            print("      sudo apt install lilypond  # Ubuntu/Debian")
            print()

        # Vérifier music21
        music21_installed, _ = check_python_module('music21', 'music21')
        if not music21_installed:
            print("  • Installer music21 pour support MusicXML:")
            print("      source venv/bin/activate")
            print("      pip install music21")
            print()

    # État final
    if results['missing'] == 0:
        if results['optional_missing'] == 0:
            print("=" * 70)
            print("  🎉 Tout est installé ! L'application est prête.")
            print("=" * 70)
            print()
            print("  Lancer l'application:")
            print("    ./run.sh")
            print()
            return 0
        else:
            print("=" * 70)
            print("  ✓ Configuration minimale OK")
            print("  ⚠ Installez les composants optionnels pour toutes les fonctionnalités")
            print("=" * 70)
            print()
            return 0
    else:
        print("=" * 70)
        print("  ⚠ Installation incomplète")
        print("=" * 70)
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
