#!/bin/bash
# Script de compilation PyInstaller pour MetaCloud
#
# Usage :
#   ./build.sh          # Linux/macOS
#   ./build.sh --onedir # Compilation en mode dossier (plus rapide au démarrage)
#
# Pour Windows, utilisez build.bat à la place.

set -e

# Détecter le mode
MODE="--onefile"
if [ "$1" = "--onedir" ]; then
    MODE="--onedir"
fi

echo "=== Compilation MetaCloud (mode: $MODE) ==="

# Nettoyer les anciens builds
rm -rf build/ dist/

# Vérifier que PyInstaller est installé
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller n'est pas installé. Installez-le avec :"
    echo "   pip install pyinstaller"
    exit 1
fi

# Vérifier que plyer est installé (optionnel sur Linux, requis sur Windows/macOS)
if ! python3 -c "import plyer" 2>/dev/null; then
    echo "⚠️  plyer n'est pas installé. Les notifications peuvent ne pas fonctionner."
    echo "   Installez-le avec : pip install plyer"
fi

# Compilation
# --add-data : inclut le dossier assets/ (icônes)
# --hidden-import : modules non détectés automatiquement
# --collect-all : collecte tous les sous-modules de plyer (plateformes spécifiques)
pyinstaller \
    $MODE \
    --name "MetaCloud" \
    --add-data "assets:assets" \
    --hidden-import "plyer.platforms.linux.notification" \
    --hidden-import "plyer.platforms.win.libs" \
    --hidden-import "plyer.platforms.win.notification" \
    --hidden-import "plyer.platforms.macos.notification" \
    --collect-all "plyer" \
    --noconfirm \
    Release.py

echo ""
echo "=== Compilation terminée ==="
if [ "$MODE" = "--onefile" ]; then
    echo "Exécutable : dist/MetaCloud"
else
    echo "Dossier : dist/MetaCloud/"
fi
echo ""
echo "Pour lancer :"
if [ "$MODE" = "--onefile" ]; then
    echo "  ./dist/MetaCloud"
else
    echo "  ./dist/MetaCloud/MetaCloud"
fi
