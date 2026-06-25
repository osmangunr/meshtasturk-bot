import json
import threading
import paho.mqtt.client as mqtt
from app.config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS, MQTT_SUB_TOPIC
from app.database.db import upsert_node
from app.meshtastic.commands import handle_meshtastic_command

class MqttBridge:
    def __init__(self, telegram_sender):
        self.telegram_sender = telegram_sender
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT bağlantı kodu:", rc, flush=True)
        client.subscribe(MQTT_SUB_TOPIC)
        self.telegram_sender("✅ MeshtasTurk Bot MQTT'ye bağlandı.")

    def on_message(self, client, userdata, msg):
        try:
            raw = msg.payload.decode("utf-8", errors="ignore")
            payload = json.loads(raw)

            node_id, is_new, lat, lon = upsert_node(payload)
            if is_new:
                self.telegram_sender(f"🟢 Yeni Node Görüldü\nNode: {node_id}")

            p = payload.get("payload") or {}
            text_msg = p.get("text") or p.get("message")
            if text_msg:
                if str(text_msg).startswith("!"):
                    reply = handle_meshtastic_command(str(text_msg), node_id=node_id, lat=lat, lon=lon)
                    if reply:
                        self.telegram_sender(f"📡 Meshtastic Komutu\n{node_id}: {text_msg}\n\n{reply}")
                else:
                    self.telegram_sender(f"💬 Meshtastic\n{node_id}: {text_msg}")
        except Exception as e:
            print("MQTT mesaj işleme hatası:", e, flush=True)

    def start(self):
        if MQTT_USER:
            self.client.username_pw_set(MQTT_USER, MQTT_PASS)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        self.client.loop_forever()

    def start_thread(self):
        threading.Thread(target=self.start, daemon=True).start()
