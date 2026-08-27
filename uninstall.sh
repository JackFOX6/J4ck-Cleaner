#!/usr/bin/env bash
# ==============================================================================
# J4ck Cleaner - User Desktop Uninstaller
# Removes desktop shortcuts and launcher binaries
# ==============================================================================

set -e

J4CK_LAUNCHER="/home/j4ck/.local/bin/j4ck-cleaner"
NOCTURNE_LAUNCHER="/home/j4ck/.local/bin/nocturne-guardian"
DESKTOP_FILE="/home/j4ck/.local/share/applications/j4ck-cleaner.desktop"
LEGACY_DESKTOP_FILE="/home/j4ck/.local/share/applications/nocturne-guardian.desktop"
ICON_FILE="/home/j4ck/.local/share/icons/hicolor/scalable/apps/nocturne-guardian.svg"

echo "================================================="
echo "   Desinstalador de J4ck Cleaner                "
echo "================================================="

rm -f "$J4CK_LAUNCHER"
rm -f "$NOCTURNE_LAUNCHER"
rm -f "$DESKTOP_FILE"
rm -f "$LEGACY_DESKTOP_FILE"
rm -f "$ICON_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database ~/.local/share/applications 2>/dev/null || true
fi

echo "[✓] Entrada de escritorio y accesos directos eliminados correctamente."

