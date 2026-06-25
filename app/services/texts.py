from pathlib import Path

BASE_TEXT_DIR = Path("/app/texts")
FALLBACK_TEXT_DIR = Path("/opt/meshtasturk-bot-pro/texts")

def _read_text(path: Path):
    try:
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    except Exception:
        return None
    return None

def read_role_text(role_no=None) -> str:
    if not role_no:
        for base in [BASE_TEXT_DIR, FALLBACK_TEXT_DIR]:
            text = _read_text(base / "roles" / "index.txt")
            if text:
                return text
        return "📡 Role listesi bulunamadı."

    role_no = str(role_no).strip()
    if not role_no.isdigit() or int(role_no) < 1 or int(role_no) > 9:
        return "Kullanım: /role 1 ile /role 9 arasında seçim yapın."

    for base in [BASE_TEXT_DIR, FALLBACK_TEXT_DIR]:
        text = _read_text(base / "roles" / f"{role_no}.txt")
        if text:
            return text

    return f"ROLE {role_no} dosyası bulunamadı."
