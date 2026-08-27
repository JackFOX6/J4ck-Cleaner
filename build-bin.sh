#!/usr/bin/env bash
# ==============================================================================
# J4ck Cleaner - Standalone Binary Builder (PyInstaller)
# Generates single-file standalone Linux executable for GitHub Releases
# ==============================================================================

set -e

APP_DIR="/home/j4ck/Dev/nocturne-guardian"
VENV_PIP="$APP_DIR/venv/bin/pip"
VENV_PYINSTALLER="$APP_DIR/venv/bin/pyinstaller"

echo "================================================="
echo "   Compilador de Binario Nativo (J4ck Cleaner)  "
echo "================================================="

cd "$APP_DIR"

if [ ! -f "$VENV_PYINSTALLER" ]; then
    echo "[+] Instalando PyInstaller en el entorno virtual..."
    "$VENV_PIP" install -q pyinstaller
fi

echo "[+] Compilando J4ck Cleaner a binario Standalone..."
"$VENV_PYINSTALLER" \
    --noconfirm \
    --onefile \
    --windowed \
    --name "j4ck-cleaner-bin" \
    --add-data "assets:assets" \
    --add-data "j4ck_cleaner/locales:j4ck_cleaner/locales" \
    --hidden-import "PySide6.QtCore" \
    --hidden-import "PySide6.QtWidgets" \
    --hidden-import "PySide6.QtGui" \
    --hidden-import "psutil" \
    --hidden-import "matplotlib" \
    main.py

echo "================================================="
if [ -f "$APP_DIR/dist/j4ck-cleaner-bin" ]; then
    SIZE=$(du -h "$APP_DIR/dist/j4ck-cleaner-bin" | cut -f1)
    echo "[✓] Compilación completada con éxito."
    echo "[i] Ejecutable generado en: dist/j4ck-cleaner-bin (Tamaño: $SIZE)"
    echo "[+] Actualizando instalador en entorno de usuario..."
    "$APP_DIR/install.sh"
else
    echo "[!] Error durante la compilación."
    exit 1
fi
echo "================================================="

