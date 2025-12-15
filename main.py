from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from timezonefinder import TimezoneFinder
from datetime import datetime as dt
import pytz

app = FastAPI(
    title="Astrology API",
    description="Natal chart ir planetų bei namų pozicijų skaičiavimas",
    version="1.3"
)

class BirthData(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    lat: float
    lon: float

PLANETS = [
    const.SUN,
    const.MOON,
    const.MERCURY,
    const.VENUS,
    const.MARS,
    const.JUPITER,
    const.SATURN,
]

@app.get("/")
async def root():
    return {"message": "Astrology API veikia! ✨ Naudok /docs testavimui."}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.3"}

@app.post("/calculate")
async def calculate(data: BirthData):
    try:
        # 1️⃣ Laiko zona
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=data.lat, lng=data.lon)
        if not tz_str:
            raise HTTPException(status_code=400, detail="Nepavyko nustatyti laiko zonos pagal koordinates")

        # 2️⃣ Lokalų laiką → UTC
        local_tz = pytz.timezone(tz_str)
        naive_dt = dt.strptime(f"{data.date} {data.time}", "%Y-%m-%d %H:%M")
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        # 3️⃣ Sudaromas horoskopas
        date_obj = Datetime(utc_dt.strftime("%Y/%m/%d"), utc_dt.strftime("%H:%M"), "+00:00")
        pos = GeoPos(data.lat, data.lon)
        chart = Chart(date_obj, pos)

        # 4️⃣ Namai kaip žemėlapis
        houses = {
            h.id: {
                "sign": h.sign,
                "degree": round(h.lon, 2)
            }
            for h in chart.houses
        }

        # 5️⃣ Namų sąrašas (rikiuojame pagal ilgumą)
        house_list = sorted(chart.houses, key=lambda h: h.lon)

        # 6️⃣ Funkcija planetos namui nustatyti (360° logika)
        def get_house_by_lon(lon, house_list):
            for i in range(len(house_list)):
                start = house_list[i].lon
                end = house_list[(i + 1) % 12].lon
                if start < end:
                    if start <= lon < end:
                        return i + 1
                else:  # pereina per 360°
                    if lon >= start or lon < end:
                        return i + 1
            return None

        # 7️⃣ Planetų analizė
        planets = {}
        for pid in PLANETS:
            p = chart.get(pid)
            house_number = get_house_by_lon(p.lon, house_list)
            planets[p.id] = {
                "sign": p.sign,
                "degree": round(p.lon, 2),
                "house": house_number
            }

        # 8️⃣ ASC
        asc = chart.get(const.ASC)

        # 9️⃣ Atsakymas
        return {
            "sun_sign": chart.get(const.SUN).sign,
            "moon_sign": chart.get(const.MOON).sign,
            "ascendant": {
                "sign": asc.sign,
                "degree": round(asc.lon, 2)
            },
            "timezone": tz_str,
            "planets": planets,
            "houses": houses
        }

    except Exception as e:
        print(f"[Klaida]: {e}")
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant: {str(e)}")
