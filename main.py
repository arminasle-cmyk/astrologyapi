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
        # 1️⃣ Timezone
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=data.lat, lng=data.lon)
        if not tz_str:
            raise HTTPException(
                status_code=400,
                detail="Nepavyko nustatyti laiko zonos pagal koordinates"
            )

        # 2️⃣ Lokalų laiką → UTC
        local_tz = pytz.timezone(tz_str)
        naive_dt = dt.strptime(
            f"{data.date} {data.time}",
            "%Y-%m-%d %H:%M"
        )
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        # 3️⃣ Chart
        date_obj = Datetime(
            utc_dt.strftime("%Y/%m/%d"),
            utc_dt.strftime("%H:%M"),
            "+00:00"
        )
        pos = GeoPos(data.lat, data.lon)
        chart = Chart(date_obj, pos)

        # 4️⃣ Namai
        houses = {
            h.id: {
                "sign": h.sign,
                "degree": round(h.lon, 2)
            }
            for h in chart.houses
        }

        # 5️⃣ Planetos su TIKSLIAI nustatytu namu
        planets = {}
        for pid in PLANETS:
            p = chart.get(pid)

            house_number = None
            for i, h in enumerate(chart.houses, start=1):
                if h.inHouse(p.lon):
                    house_number = i
                    break

            planets[p.id] = {
                "sign": p.sign,
                "degree": round(p.lon, 2),
                "house": house_number
            }

        # 6️⃣ Ascendant
        asc = chart.get(const.ASC)

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
        raise HTTPException(
            status_code=400,
            detail=f"Klaida skaičiuojant: {str(e)}"
        )
