#!/usr/bin/env bash
set -Eeuo pipefail
[[ "$EUID" -eq 0 ]] || { echo "Root olarak çalıştırın."; exit 1; }
[[ -r /dev/tty ]] || { echo "Etkileşimli terminal gerekli; dosyayı indirip sudo bash ile çalıştırın."; exit 1; }
command -v apt-get >/dev/null || { echo "Ubuntu/Debian apt sistemi gerekli."; exit 1; }

BROKER_IP="87.106.168.118"
MQTT_DOMAIN="mqtt.meshtasturk.com"
REPO_URL="https://github.com/osmangunr/meshtasturk-bot.git"
APP_DIR="/opt/meshtasturk-bot-pro"
GATEWAY_ID="!33691d9c"
GATEWAY_NUM="862526876"
SUB_TOPIC="msh/2/json/MeshtasTurk/#"
DOWNLINK_TOPIC="msh/2/json/mqtt/!33691d9c"
ECHO_TOPIC="msh/2/json/MeshtasTurk/!33691d9c"

umask 077
export DEBIAN_FRONTEND=noninteractive
echo "== MeshtasTurk MQTT + Telegram Bot kurulumu =="
apt-get update
apt-get install -y ca-certificates curl git mosquitto mosquitto-clients docker.io python3
systemctl enable --now docker
systemctl stop mosquitto 2>/dev/null || true

if [[ -f /etc/mosquitto/mosquitto.conf ]]; then
  cp -a /etc/mosquitto/mosquitto.conf "/etc/mosquitto/mosquitto.conf.pre-meshtasturk.$(date +%s)"
fi
mkdir -p /etc/mosquitto /var/lib/mosquitto /var/log/mosquitto
cat > /etc/mosquitto/mosquitto.conf <<'MOSQ'
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
MOSQ
cat > /etc/mosquitto/acl <<'ACL'
pattern readwrite msh/#
pattern readwrite test/#
ACL
chown mosquitto:mosquitto /etc/mosquitto/mosquitto.conf /etc/mosquitto/acl
chmod 640 /etc/mosquitto/acl

echo
echo "MQTT ana kullanıcı: osmangunr"
if [[ -s /etc/mosquitto/passwd ]]; then
  mosquitto_passwd /etc/mosquitto/passwd osmangunr
else
  mosquitto_passwd -c /etc/mosquitto/passwd osmangunr
fi
echo
echo "Bot MQTT kullanıcısı: meshtasbot"
mosquitto_passwd /etc/mosquitto/passwd meshtasbot
chown mosquitto:mosquitto /etc/mosquitto/passwd
chmod 640 /etc/mosquitto/passwd
systemctl enable mosquitto
systemctl restart mosquitto
systemctl is-active --quiet mosquitto || { journalctl -u mosquitto -n 80 --no-pager; exit 1; }

echo
read -r -s -p "Telegram BotFather token: " BOT_TOKEN < /dev/tty
printf '\n'
[[ -n "$BOT_TOKEN" ]] || { echo "BOT_TOKEN boş olamaz."; exit 1; }
read -r -p "Telegram grup/sohbet ID (ör. -100...): " CHAT_ID < /dev/tty
[[ -n "$CHAT_ID" ]] || { echo "CHAT_ID boş olamaz."; exit 1; }
read -r -p "Telegram yönetici kullanıcı ID (isteğe bağlı, çokluysa virgülle): " ADMIN_IDS < /dev/tty
echo
read -r -s -p "meshtasbot MQTT şifresini tekrar gir (.env için, aynı şifre): " MQTT_PASS < /dev/tty
printf '\n'
[[ -n "$MQTT_PASS" ]] || { echo "MQTT bot şifresi boş olamaz."; exit 1; }

if [[ -d "$APP_DIR/.git" ]]; then
  git -C "$APP_DIR" fetch --depth 1 origin main
  git -C "$APP_DIR" reset --hard origin/main
else
  if [[ -e "$APP_DIR" ]]; then mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d%H%M%S)"; fi
  git clone --depth 1 "$REPO_URL" "$APP_DIR"
fi
mkdir -p "$APP_DIR/data" "$APP_DIR/logs" "$APP_DIR/backups"

export BOT_TOKEN CHAT_ID ADMIN_IDS MQTT_PASS
export MQTT_HOST="127.0.0.1" MQTT_PORT="1883" MQTT_USER="meshtasbot"
export MQTT_SUB_TOPIC="$SUB_TOPIC" MQTT_GATEWAY_ID="$GATEWAY_ID" MQTT_GATEWAY_NUM="$GATEWAY_NUM"
export MQTT_DOWNLINK_TOPIC="$DOWNLINK_TOPIC" MQTT_ECHO_TOPIC="$ECHO_TOPIC"
export MAP_URL="https://map.meshtasturk.com" TIMEZONE="Europe/Istanbul"
export ONLINE_MINUTES="30" REPORT_TIMES="09:30,15:30,22:00" QUAKE_MIN_MAG="3.5"

python3 - <<'PY'
import json, os
path = "/opt/meshtasturk-bot-pro/.env"
keys = [
 "BOT_TOKEN","CHAT_ID","ADMIN_IDS","MQTT_HOST","MQTT_PORT","MQTT_USER","MQTT_PASS",
 "MQTT_SUB_TOPIC","MQTT_GATEWAY_ID","MQTT_GATEWAY_NUM","MQTT_DOWNLINK_TOPIC",
 "MQTT_ECHO_TOPIC","MAP_URL","TIMEZONE","ONLINE_MINUTES","REPORT_TIMES","QUAKE_MIN_MAG"
]
with open(path, "w", encoding="utf-8") as f:
    for key in keys:
        f.write(key + "=" + json.dumps(os.environ.get(key, ""), ensure_ascii=False) + "\n")
os.chmod(path, 0o600)
PY

chmod +x "$APP_DIR"/*.sh 2>/dev/null || true
docker rm -f meshtasturk-bot >/dev/null 2>&1 || true
docker build --pull -t meshtasturk-bot "$APP_DIR"
docker run -d --name meshtasturk-bot --restart unless-stopped --network host \
  --env-file "$APP_DIR/.env" \
  -v "$APP_DIR/data:/app/data" -v "$APP_DIR/logs:/app/logs" \
  -v "$APP_DIR/texts:/app/texts" meshtasturk-bot

if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
  ufw allow 1883/tcp >/dev/null
fi

DNS_IP="$(getent ahostsv4 "$MQTT_DOMAIN" 2>/dev/null | awk 'NR==1 {print $1}' || true)"
if [[ "$DNS_IP" == "$BROKER_IP" ]]; then
  echo "DNS OK: $MQTT_DOMAIN -> $BROKER_IP"
else
  echo "DNS UYARISI: $MQTT_DOMAIN şu an '$DNS_IP' olarak görünüyor."
  echo "DNS sağlayıcısında A kaydını $MQTT_DOMAIN -> $BROKER_IP yapın."
fi

sleep 3
echo
systemctl --no-pager --full status mosquitto | sed -n '1,8p' || true
docker ps --filter name=meshtasturk-bot
docker logs --tail 35 meshtasturk-bot 2>&1 || true
echo "Kurulum tamamlandı. Bot logları: docker logs -f meshtasturk-bot"
echo "MQTT mesajları: mosquitto_sub -h 127.0.0.1 -p 1883 -u osmangunr -P '<şifre>' -t 'msh/#' -v"
echo "Not: Harici VPS güvenlik duvarında TCP/1883 izni gerekebilir."
echo "Güvenlik: MQTT 1883 TLS kullanmaz; kimlik bilgileri ağ üzerinde şifrelenmeden taşınır."
