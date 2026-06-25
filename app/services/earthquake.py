import requests
from app.config import QUAKE_MIN_MAG

def earthquake_text(long: bool = False) -> str:
    try:
        data = requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live", timeout=15).json()
        items = data.get("result", [])[:20]
        filtered = [e for e in items if float(e.get("mag", 0) or 0) >= QUAKE_MIN_MAG]
        if not filtered:
            return f"✅ Son kayıtlarda {QUAKE_MIN_MAG}+ deprem görünmüyor."
        e = filtered[0]
        title = e.get("title", "Bilinmiyor")
        mag = e.get("mag", "?")
        depth = e.get("depth", "?")
        date = e.get("date", "")
        if long:
            return f"🚨 Son {QUAKE_MIN_MAG}+ Deprem\n\nYer: {title}\nBüyüklük: {mag}\nDerinlik: {depth} km\nTarih: {date}"
        return f"🚨 Deprem {mag} {title} Derinlik:{depth}km"
    except Exception:
        return "Deprem bilgisi alınamadı."
