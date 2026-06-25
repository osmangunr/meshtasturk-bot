import sqlite3
from app.config import DB_PATH, ONLINE_MINUTES
from app.utils.time import now_ts
from app.utils.geo import haversine

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        node_id TEXT PRIMARY KEY,
        sender TEXT,
        short_name TEXT,
        long_name TEXT,
        latitude REAL,
        longitude REAL,
        altitude REAL,
        rssi REAL,
        snr REAL,
        last_seen INTEGER,
        first_seen INTEGER
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        node_id TEXT,
        text TEXT,
        created_at INTEGER
    )
    """)
    conn.commit()
    conn.close()

def node_name(row):
    return row["long_name"] or row["short_name"] or row["sender"] or row["node_id"]

def save_event(event_type, node_id, text):
    conn = get_conn()
    conn.execute(
        "INSERT INTO events(event_type,node_id,text,created_at) VALUES(?,?,?,?)",
        (event_type, node_id, text, now_ts()),
    )
    conn.commit()
    conn.close()

def upsert_node(payload):
    sender = str(payload.get("sender") or payload.get("from") or "unknown")
    node_id = sender
    p = payload.get("payload") or {}

    lat = lon = alt = None
    if "latitude_i" in p and "longitude_i" in p:
        lat = p.get("latitude_i") / 10000000
        lon = p.get("longitude_i") / 10000000
        alt = p.get("altitude")

    short_name = p.get("short_name") or p.get("shortName")
    long_name = p.get("long_name") or p.get("longName")

    conn = get_conn()
    old = conn.execute("SELECT * FROM nodes WHERE node_id=?", (node_id,)).fetchone()

    if old is None:
        conn.execute("""
        INSERT INTO nodes(node_id,sender,short_name,long_name,latitude,longitude,altitude,rssi,snr,last_seen,first_seen)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (node_id, sender, short_name, long_name, lat, lon, alt, payload.get("rssi"), payload.get("snr"), now_ts(), now_ts()))
        is_new = True
    else:
        conn.execute("""
        UPDATE nodes SET
          sender=?,
          short_name=COALESCE(?, short_name),
          long_name=COALESCE(?, long_name),
          latitude=COALESCE(?, latitude),
          longitude=COALESCE(?, longitude),
          altitude=COALESCE(?, altitude),
          rssi=COALESCE(?, rssi),
          snr=COALESCE(?, snr),
          last_seen=?
        WHERE node_id=?
        """, (sender, short_name, long_name, lat, lon, alt, payload.get("rssi"), payload.get("snr"), now_ts(), node_id))
        is_new = False

    conn.commit()
    conn.close()
    return node_id, is_new, lat, lon

def stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM nodes").fetchone()["c"]
    located = conn.execute("SELECT COUNT(*) c FROM nodes WHERE latitude IS NOT NULL AND longitude IS NOT NULL").fetchone()["c"]
    online_after = now_ts() - ONLINE_MINUTES * 60
    online = conn.execute("SELECT COUNT(*) c FROM nodes WHERE last_seen>=?", (online_after,)).fetchone()["c"]
    conn.close()
    return total, online, located

def all_nodes(limit=100):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM nodes ORDER BY last_seen DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows

def nearest_nodes(lat, lon, limit=10, radius_km=None):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM nodes WHERE latitude IS NOT NULL AND longitude IS NOT NULL").fetchall()
    conn.close()
    out = []
    for r in rows:
        d = haversine(lat, lon, r["latitude"], r["longitude"])
        if radius_km is None or d <= radius_km:
            out.append((d, r))
    out.sort(key=lambda x: x[0])
    return out[:limit]
