#!/bin/bash
# ==============================================================
# NIS2 Audit Tool — Deploy script (venv + gunicorn + systemd)
# Voor gebruik ACHTER een reverse proxy (nginx) die je zelf instelt.
# Dit script regelt alleen de Python-app zelf: venv, dependencies,
# de package-structuur, en een systemd-service zodat de app als
# achtergronddienst draait en automatisch herstart bij een crash
# of server-reboot.
# ==============================================================

set -e  # stop direct bij een fout

# ---------- Instellingen (pas aan indien nodig) ----------
APP_NAME="nis2-tool"
APP_USER="${SUDO_USER:-$(whoami)}"
INSTALL_DIR="/opt/nis2-tool"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
PORT=5077
GUNICORN_WORKERS=3
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"  # root van de repo

echo "🚀 NIS2 Audit Tool - Deployment (venv + systemd)"
echo "   Bron:        $SOURCE_DIR"
echo "   Installdir:  $INSTALL_DIR"
echo "   Poort:       $PORT"
echo ""

# ---------- Vereisten check ----------
if [ "$EUID" -ne 0 ]; then
    echo "❌ Dit script moet met sudo/root draaien (voor systemd + /opt)."
    echo "   Probeer: sudo ./scripts/deploy.sh"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 niet gevonden. Installeer Python 3.11+ eerst."
    exit 1
fi

echo "📦 Python versie: $(python3 --version)"

# ---------- Installatiemap voorbereiden ----------
echo "📁 Installatiemap voorbereiden..."
mkdir -p "$INSTALL_DIR"

# Kopieer de app-bestanden als package 'nis2app' (geen streepjes toegestaan
# in een Python-modulenaam), zodat de relatieve imports in app.py
# (from .database import ...) gewoon blijven werken.
mkdir -p "$INSTALL_DIR/nis2app"
cp "$SOURCE_DIR/__init__.py" \
   "$SOURCE_DIR/app.py" \
   "$SOURCE_DIR/database.py" \
   "$SOURCE_DIR/scanner.py" \
   "$SOURCE_DIR/questionnaire.py" \
   "$SOURCE_DIR/advies.py" \
   "$SOURCE_DIR/pdf_report.py" \
   "$INSTALL_DIR/nis2app/"

cp "$SOURCE_DIR/requirements.txt" "$INSTALL_DIR/"

# Frontend-bestanden mee (handig als je ze later los wilt serveren,
# nginx kan hier ook direct naar wijzen als static root)
cp "$SOURCE_DIR/index.html" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SOURCE_DIR/script.js" "$INSTALL_DIR/" 2>/dev/null || true

echo "✅ Bestanden gekopieerd naar $INSTALL_DIR"

# ---------- Virtual environment ----------
echo "🐍 Virtual environment aanmaken..."
python3 -m venv "$VENV_DIR"

echo "📦 Dependencies installeren..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet
"$VENV_DIR/bin/pip" install gunicorn --quiet

echo "✅ Virtual environment klaar: $VENV_DIR"

# ---------- Databasebestand: schrijfrechten ----------
touch "$INSTALL_DIR/nis2_audit.db" 2>/dev/null || true

# ---------- Eigenaarschap ----------
chown -R "$APP_USER":"$APP_USER" "$INSTALL_DIR"

# ---------- systemd service-bestand ----------
echo "⚙️  systemd service aanmaken..."
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=NIS2 Audit Tool (gunicorn)
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers $GUNICORN_WORKERS \\
    --bind 127.0.0.1:$PORT \\
    --access-logfile - \\
    --error-logfile - \\
    nis2app.app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service-bestand geschreven: $SERVICE_FILE"

# ---------- Service starten ----------
echo "🚀 Service herladen en starten..."
systemctl daemon-reload
systemctl enable "$APP_NAME"
systemctl restart "$APP_NAME"

sleep 2

# ---------- Status check ----------
if systemctl is-active --quiet "$APP_NAME"; then
    echo ""
    echo "✅ NIS2 Audit Tool draait als systemd-service!"
    echo ""
    echo "   Luistert lokaal op: http://127.0.0.1:$PORT"
    echo "   (bind is bewust 127.0.0.1 — zet je eigen nginx ervoor als reverse proxy)"
    echo ""
    echo "📋 Nuttige commando's:"
    echo "   Status:      systemctl status $APP_NAME"
    echo "   Logs volgen: journalctl -u $APP_NAME -f"
    echo "   Herstarten:  sudo systemctl restart $APP_NAME"
    echo "   Stoppen:     sudo systemctl stop $APP_NAME"
    echo "   Uitzetten (bij boot): sudo systemctl disable $APP_NAME"
else
    echo ""
    echo "❌ Service is niet actief. Bekijk de logs:"
    echo "   journalctl -u $APP_NAME -n 50 --no-pager"
    exit 1
fi
