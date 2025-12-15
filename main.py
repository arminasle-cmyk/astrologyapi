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
    version="1.2"
)

class BirthData(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    lat: float
    lon: float

PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]

HOUSES = [
    const.HOUSE1, const.HOUSE2, const.HOUSE3, const.HOUSE4, const.HOUSE5,
    const.HOUSE6, const.HOUSE7, const.HOUSE8, const.HOUSE9, const.HOUSE10,
    const.HOUSE11, const.HOUSE12
]

@app.get("/")
async def root():
    return {"message": "Astrology API veikia! 🌟 Naudok /docs testavimui."}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.2"}

@app.post("/calculate")
async def calculate(data: BirthData):
    try:
        # Nustatyti laiko zoną pagal koordinates
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=data.lat, lng=data.lon)
        if not tz_str:
            raise HTTPException(status_code=400, detail="Nepavyko nustatyti laiko zonos pagal koordinates")

        # Konvertuoti laiką į UTC
        local_tz = pytz.timezone(tz_str)
        naive_dt = dt.strptime(f"{data.date} {data.time}", "%Y-%m-%d %H:%M")
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        # Sukurti astrologinį grafiką
        date_obj = Datetime(utc_dt.strftime("%Y/%m/%d"), utc_dt.strftime("%H:%M"), "UTC")
        pos = GeoPos(str(data.lat), str(data.lon))
        chart = Chart(date_obj, pos, hsys=const.PLACIDUS)

        # Planetų duomenys
        planets = {
            obj.id: {
                "sign": obj.sign,
                "degree": round(obj.lon, 2),
                "house": obj.house
            }
            for obj in [chart.get(p) for p in PLANETS]
        }

        # Namų duomenys
        houses = {
            house: {
                "sign": chart.houses.get(house).sign,
                "degree": round(chart.houses.get(house).lon, 2)
            }
            for house in HOUSES
        }

        return {
            "sun_sign": chart.get(const.SUN).sign,
            "moon_sign": chart.get(const.MOON).sign,
            "ascendant": chart.get(const.ASC).sign,
            "timezone": tz_str,
            "planets": planets,
            "houses": houses
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant: {str(e)}")
