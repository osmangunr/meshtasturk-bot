import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import BOT_TOKEN, CHAT_ID
from app.database.db import init_db
from app.telegram import commands
from app.telegram.welcome import welcome_new_members, rules_command, commands_command
from app.mqtt.client import MqttBridge
from app.services.scheduler import register_jobs

def send_tg_sync(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except Exception as e:
        print("Telegram gönderim hatası:", e, flush=True)

def build_app():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_cmd))
    app.add_handler(CommandHandler("map", commands.map_cmd))
    app.add_handler(CommandHandler("harita", commands.map_cmd))
    app.add_handler(CommandHandler("mqtt", commands.mqtt_cmd))
    app.add_handler(CommandHandler("json", commands.json_cmd))
    app.add_handler(CommandHandler("nodes", commands.nodes_cmd))
    app.add_handler(CommandHandler("stats", commands.stats_cmd))
    app.add_handler(CommandHandler("durum", commands.durum_cmd))
    app.add_handler(CommandHandler("status", commands.durum_cmd))
    app.add_handler(CommandHandler("hava", commands.hava_cmd))
    app.add_handler(CommandHandler("deprem", commands.deprem_cmd))
    app.add_handler(CommandHandler("yakin", commands.yakin_cmd))
    app.add_handler(CommandHandler("yakın", commands.yakin_cmd))
    app.add_handler(CommandHandler("komsu", commands.yakin_cmd))
    app.add_handler(CommandHandler("send", commands.send_cmd))
    app.add_handler(CommandHandler("broadcast", commands.broadcast_cmd))
    app.add_handler(CommandHandler("kurallar", rules_command))
    app.add_handler(CommandHandler("komutlar", commands_command))
    app.add_handler(CommandHandler("role", commands.role_cmd))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    app.add_handler(MessageHandler(filters.LOCATION, commands.location_handler))

    register_jobs(app)
    return app

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN boş. .env dosyasını doldurun.")

    init_db()
    MqttBridge(send_tg_sync).start_thread()

    app = build_app()
    print("MeshtasTurk Bot Pro başlıyor...", flush=True)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
