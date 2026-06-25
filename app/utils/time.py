import time
from datetime import datetime
from app.config import TZ

def now_ts() -> int:
    return int(time.time())

def now_text() -> str:
    return datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")

def fmt_ts(ts: int) -> str:
    try:
        return datetime.fromtimestamp(int(ts), TZ).strftime("%d.%m %H:%M")
    except Exception:
        return "-"
