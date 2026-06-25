#!/bin/bash
set -e
APP_DIR="/opt/meshtasturk-bot-pro"

echo "📦 MeshtasTurk Bot Pro kuruluyor..."

if ! command -v docker >/dev/null 2>&1; then
  apt update
  apt install -y docker.io
  systemctl enable --now docker
fi

mkdir -p "$APP_DIR"
cp -r . "$APP_DIR"/
cd "$APP_DIR"

mkdir -p data logs backups

if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️ .env oluşturuldu. Bilgileri doldur:"
  echo "nano $APP_DIR/.env"
fi

chmod +x *.sh
echo "✅ Kurulum hazır."
echo "Başlatmak için:"
echo "$APP_DIR/start.sh"
