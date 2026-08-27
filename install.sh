#!/usr/bin/env bash
# ==============================================================================
# J4ck Cleaner v1.2.5 - User Desktop Installer (J4ckENI Framework)
# Integrates application into Linux desktop launcher (~/.local/share/applications)
# ==============================================================================

set -e

APP_DIR="/home/j4ck/Dev/nocturne-guardian"
BIN_DIR="/home/j4ck/.local/bin"
J4CK_LAUNCHER="$BIN_DIR/j4ck-cleaner"
NOCTURNE_LAUNCHER="$BIN_DIR/nocturne-guardian"
DESKTOP_DIR="/home/j4ck/.local/share/applications"
ICON_DIR="/home/j4ck/.local/share/icons/hicolor/scalable/apps"

echo "================================================="
echo "   Instalador de J4ck Cleaner v1.2.5            "
echo "   (J4ckENI Framework / J4ck Library)           "
echo "================================================="

# 1. Ensure directories exist
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# 2. Check virtualenv
if [ ! -d "$APP_DIR/venv" ]; then
    echo "[+] Creando entorno virtual Python..."
    python3 -m venv "$APP_DIR/venv"
fi

echo "[+] Instalando/Verificando dependencias Python..."
"$APP_DIR/venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

# 3. Create launcher script (prefer standalone compiled binary if available)
echo "[+] Registrando ejecutables en $J4CK_LAUNCHER y $NOCTURNE_LAUNCHER..."
cat << 'EOF' > "$J4CK_LAUNCHER"
#!/bin/bash
export QT_QPA_PLATFORM="wayland;xcb"
if [ -x "/home/j4ck/Dev/nocturne-guardian/dist/j4ck-cleaner-bin" ]; then
    exec /home/j4ck/Dev/nocturne-guardian/dist/j4ck-cleaner-bin "$@"
else
    exec /home/j4ck/Dev/nocturne-guardian/venv/bin/python3 /home/j4ck/Dev/nocturne-guardian/main.py "$@"
fi
EOF
chmod +x "$J4CK_LAUNCHER"
ln -sf "$J4CK_LAUNCHER" "$NOCTURNE_LAUNCHER"

# 4. Copy Icon SVG
echo "[+] Instalando icono vectorial SVG..."
cp -f "$APP_DIR/assets/icons/nocturne-guardian.svg" "$ICON_DIR/nocturne-guardian.svg"

# 5. Copy Desktop File (remove legacy duplicate desktop entry)
echo "[+] Registrando entrada de escritorio en $DESKTOP_DIR..."
rm -f "$DESKTOP_DIR/nocturne-guardian.desktop"
cp -f "$APP_DIR/nocturne-guardian.desktop" "$DESKTOP_DIR/j4ck-cleaner.desktop"

# 6. Update desktop database cache
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "================================================="
echo "[✓] Instalación completada con éxito."
echo "[i] Puedes abrir 'J4ck Cleaner' desde tu lanzador de aplicaciones (Noctalia, Niri, Rofi, GNOME, etc.)"
echo "[i] O ejecutar directamente: j4ck-cleaner (o nocturne-guardian)"
echo "================================================="

