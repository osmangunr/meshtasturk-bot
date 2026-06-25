from telegram import Update
from telegram.ext import ContextTypes
from app.config import MAP_URL, MQTT_SUB_TOPIC, CHAT_ID, ADMIN_IDS, ONLINE_MINUTES
from app.database.db import stats, all_nodes, nearest_nodes, node_name
from app.utils.time import fmt_ts, now_text
from app.utils.geo import city_location
from app.services.weather import weather_text
from app.services.earthquake import earthquake_text
from app.utils.mqttinfo import mqtt_info_text
from app.services.texts import read_role_text

def is_admin(update: Update) -> bool:
    return str(update.effective_user.id) in ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MeshtasTurk Bot aktif. /help yazabilirsiniz.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📡 MeshtasTurk Bot\n\n"
        "/map - Harita\n"
        "/mqtt - MQTT ayar bilgisi\n"
        "/json - JSON topic\n"
        "/nodes - Node listesi\n"
        "/stats - İstatistik\n"
        "/durum - Sistem durumu\n"
        "/hava istanbul - Hava durumu\n"
        "/deprem - Son 4.0+ depremler\n"
        "/yakin istanbul - Şehre yakın node\n"
        "/komsu istanbul - Şehre yakın node\n"
        "/kurallar - Grup kuralları\n"
        "/komutlar - Komut listesi\\n"
        "/role 1 - Röle/bölge bilgisi"
    )

async def map_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🗺 MeshtasTurk Haritası\n{MAP_URL}")

async def mqtt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(mqtt_info_text())

async def json_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"JSON Topic:\n{MQTT_SUB_TOPIC}")

async def nodes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = all_nodes(limit=80)
    if not rows:
        await update.message.reply_text("Henüz kayıtlı node yok.")
        return
    lines = ["📡 MeshtasTurk Node Listesi\n"]
    for i, r in enumerate(rows, 1):
        loc = "📍" if r["latitude"] is not None and r["longitude"] is not None else "❌"
        lines.append(f"{i}) {node_name(r)} | {r['node_id']} | {loc} | {fmt_ts(r['last_seen'])}")
    text = "\n".join(lines)
    if len(text) > 3900:
        text = text[:3900] + "\n..."
    await update.message.reply_text(text)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total, online, located = stats()
    await update.message.reply_text(
        f"📊 MeshtasTurk İstatistik\n\n"
        f"Toplam Node: {total}\n"
        f"Online Node: {online}\n"
        f"Konum Paylaşan: {located}\n"
        f"Online Süresi: Son {ONLINE_MINUTES} dk"
    )

async def durum_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 Bot: Online\n📡 MQTT: Dinleniyor\n🗺 Harita: {MAP_URL}\n🕒 {now_text()}")

async def hava_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args).strip() or "istanbul"
    await update.message.reply_text(weather_text(city, long=True))

async def deprem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(earthquake_text(long=True))

async def yakin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args).strip()
    if not city:
        await update.message.reply_text("📍 Şehir yazın veya konum gönderin.\nÖrnek: /yakin istanbul")
        return
    found = city_location(city)
    if not found:
        await update.message.reply_text("Şehir bulunamadı.")
        return
    lat, lon, name = found
    nearby = nearest_nodes(lat, lon, limit=10)
    if not nearby:
        await update.message.reply_text(f"{name} yakınında konumlu node bulunamadı.")
        return
    lines = [f"📍 {name} Yakınındaki Node'lar\n"]
    for i, (d, r) in enumerate(nearby, 1):
        lines.append(f"{i}) {node_name(r)} - {d:.1f} km - {fmt_ts(r['last_seen'])}")
    await update.message.reply_text("\n".join(lines))

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    nearby = nearest_nodes(loc.latitude, loc.longitude, limit=5)
    if not nearby:
        await update.message.reply_text("Yakında konum bilgisi olan node bulunamadı.")
        return
    lines = ["📡 Yakınınızdaki Node'lar\n"]
    for i, (d, r) in enumerate(nearby, 1):
        lines.append(f"{i}) {node_name(r)} - {d:.1f} km")
    await update.message.reply_text("\n".join(lines))


async def role_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role_no = context.args[0] if context.args else None
    await update.message.reply_text(read_role_text(role_no))

async def send_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bu komut sadece yöneticiye özel.")
        return
    await update.message.reply_text("ℹ️ Meshtastic'e direkt MQTT dönüşü şimdilik kapalı.")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bu komut sadece yöneticiye özel.")
        return
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Kullanım: /broadcast mesaj")
        return
    await context.bot.send_message(chat_id=CHAT_ID, text=f"📢 Duyuru\n\n{text}")
