from app.config import MAP_URL
from app.database.db import stats, nearest_nodes, node_name
from app.services.weather import weather_text
from app.services.earthquake import earthquake_text
from app.utils.mqttinfo import mqtt_info_text
from app.services.texts import read_role_text

def handle_meshtastic_command(text: str, node_id=None, lat=None, lon=None):
    t = text.strip()
    parts = t.split()
    if not parts:
        return None
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd in ["!yardim", "!help"]:
        return "!harita !durum !hava istanbul !deprem !nodes !mqtt !komsu !role 1"

    if cmd in ["!harita", "!map"]:
        return f"🗺 {MAP_URL}"

    if cmd == "!mqtt":
        return mqtt_info_text()


    if cmd == "!role":
        role_no = args[0] if args else None
        return read_role_text(role_no)

    if cmd == "!durum":
        total, online, located = stats()
        return f"📡 Online:{online} Toplam:{total} Konum:{located}"

    if cmd == "!nodes":
        total, online, located = stats()
        return f"📡 Online:{online} Toplam:{total}"

    if cmd == "!hava":
        city = " ".join(args) or "istanbul"
        return weather_text(city, long=False)

    if cmd == "!deprem":
        return earthquake_text(long=False)

    if cmd == "!komsu":
        if lat is None or lon is None:
            return "📍 Bu node için konum yok. Konum gönderen node ile deneyin."
        nearby = nearest_nodes(lat, lon, limit=3)
        if not nearby:
            return "Yakın node yok."
        return "📡 Yakın: " + ", ".join([f"{node_name(r)} {d:.1f}km" for d, r in nearby])

    return None
