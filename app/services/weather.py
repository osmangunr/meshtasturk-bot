import requests

def weather_text(city: str = "istanbul", long: bool = False) -> str:
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "tr", "format": "json"},
            timeout=15,
        ).json()
        if not geo.get("results"):
            return "🌤 Şehir bulunamadı."

        g = geo["results"][0]
        w = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": g["latitude"],
                "longitude": g["longitude"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            timeout=15,
        ).json()["current"]

        if long:
            return f"🌤 {g['name']}\nSıcaklık: {w['temperature_2m']}°C\nNem: %{w['relative_humidity_2m']}\nRüzgar: {w['wind_speed_10m']} km/s"
        return f"🌤 {g['name']} {w['temperature_2m']}C Nem:%{w['relative_humidity_2m']} Rüzgar:{w['wind_speed_10m']}km/s"
    except Exception:
        return "🌤 Hava durumu alınamadı."
