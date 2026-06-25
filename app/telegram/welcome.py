from telegram import Update
from telegram.ext import ContextTypes

RULES_TEXT = """👋 MeshtasTurk grubuna hoş geldin.

📌 Grup Kuralları
1. Saygılı iletişim.
2. Reklam ve spam yasaktır.
3. Siyasi/dini tartışma yok.
4. MQTT ve node bilgilerini kötüye kullanmayalım.
5. Yardım isterken cihaz modeli, bölge ve hata mesajını yazalım.

📡 Komutlar
/map
/mqtt
/json
/nodes
/yakin istanbul
/hava istanbul
/deprem
/durum
"""

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        name = member.first_name or "arkadaşımız"
        try:
            await context.bot.send_message(chat_id=member.id, text=RULES_TEXT)
            await update.message.reply_text(f"Hoş geldin {name} 👋\nKurallar ve komutlar özel mesaj olarak gönderildi.")
        except Exception:
            await update.message.reply_text(
                f"Hoş geldin {name} 👋\nKurallar ve komutları almak için bana özelden /start yazabilirsin."
            )

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_user.id, text=RULES_TEXT)
        await update.message.reply_text("Kurallar ve komutlar özelden gönderildi.")
    except Exception:
        await update.message.reply_text(RULES_TEXT)

async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rules_command(update, context)
