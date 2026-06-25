import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
ADMIN_IDS = [x.strip() for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt.meshtasturk.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASS = os.getenv("MQTT_PASS", "")
MQTT_SUB_TOPIC = os.getenv("MQTT_SUB_TOPIC", "msh/2/json/MeshtasTurk/#")

MAP_URL = os.getenv("MAP_URL", "https://map.meshtasturk.com")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Istanbul")
TZ = ZoneInfo(TIMEZONE)

ONLINE_MINUTES = int(os.getenv("ONLINE_MINUTES", "30"))
REPORT_TIMES = os.getenv("REPORT_TIMES", "09:30,22:00")
QUAKE_MIN_MAG = float(os.getenv("QUAKE_MIN_MAG", "4.0"))

DB_PATH = "/app/data/nodes.db"
