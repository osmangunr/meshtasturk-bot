# MeshtasTurk Bot Pro

## Kurulum

```bash
cd /opt
unzip meshtasturk-bot-pro.zip
cd meshtasturk-bot-pro
chmod +x *.sh
./install.sh
nano /opt/meshtasturk-bot-pro/.env
/opt/meshtasturk-bot-pro/start.sh
```

## Telegram Komutları

- /help
- /map
- /mqtt
- /json
- /nodes
- /stats
- /durum
- /hava istanbul
- /deprem
- /yakin istanbul
- /komsu istanbul
- /kurallar
- /komutlar

## Admin Komutları

- /send mesaj
- /broadcast mesaj

## Meshtastic MQTT Komutları

Şimdilik cevaplar Telegram grubuna düşer:

- !hava istanbul
- !deprem
- !nodes
- !durum
- !harita
- !mqtt


## Role / Röle Sistemi

Röle bilgileri dosyadan okunur:

```bash
nano /opt/meshtasturk-bot-pro/texts/roles/1.txt
nano /opt/meshtasturk-bot-pro/texts/roles/2.txt
...
nano /opt/meshtasturk-bot-pro/texts/roles/9.txt
```

Telegram:
- /role
- /role 1

Meshtastic MQTT:
- !role
- !role 1
