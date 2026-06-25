from datetime import time as dtime
from app.config import REPORT_TIMES, TZ, CHAT_ID
from app.services.reports import daily_report_text

def parse_times():
    out = []
    for item in REPORT_TIMES.split(","):
        item = item.strip()
        if not item:
            continue
        h, m = item.split(":")
        out.append((int(h), int(m)))
    return out

async def report_job(context):
    await context.bot.send_message(chat_id=CHAT_ID, text=daily_report_text())

def register_jobs(app):
    for h, m in parse_times():
        app.job_queue.run_daily(
            report_job,
            time=dtime(hour=h, minute=m, tzinfo=TZ),
            name=f"report_{h}_{m}",
        )
