#!/bin/bash
set -e
cd /opt/meshtasturk-bot-pro

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Önce .env dosyasını doldur:"
  echo "nano /opt/meshtasturk-bot-pro/.env"
  exit 1
fi

docker rm -f meshtasturk-bot 2>/dev/null || true
docker build -t meshtasturk-bot .
docker run -d \
  --name meshtasturk-bot \
  --restart unless-stopped \
  --env-file /opt/meshtasturk-bot-pro/.env \
  -v /opt/meshtasturk-bot-pro/data:/app/data \
  -v /opt/meshtasturk-bot-pro/logs:/app/logs \
  -v /opt/meshtasturk-bot-pro/texts:/app/texts \
  meshtasturk-bot

echo "✅ MeshtasTurk Bot başlatıldı."
docker logs -f meshtasturk-bot
