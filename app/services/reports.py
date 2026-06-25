from app.database.db import stats
from app.config import MAP_URL
from app.utils.time import now_text

def daily_report_text() -> str:
    total, online, located = stats()
    return (
        "📡 MeshtasTurk Günlük Rapor\n\n"
        f"🟢 Online Node: {online}\n"
        f"👥 Toplam Node: {total}\n"
        f"📍 Konumlu Node: {located}\n"
        f"🗺 Harita: {MAP_URL}\n"
        f"🕒 {now_text()}"
    )
