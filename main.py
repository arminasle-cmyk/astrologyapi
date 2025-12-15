from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.const import PLANETS, HOUSES
from zoneinfo import ZoneInfo
from datetime import datetime as dt

app = FastAPI(
    title="Astrology API",
    description="Natal chart ir planetų pozicijų skaičiavimas",
    version="1.1"
)

class BirthData(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    lat: float
    lon: float
    timezone: str = "Europe/Vilnius"  # Vartotojas nurodo laiko juostą pagal pavadinimą

@app.get("/")
async def root():
    return {"message": "Astrology API veikia! 🌟 Naudok /docs testavimui..."}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.1"}

@app.post("/calculate")
async def calculate(data: BirthData):
    try:
        # Konvertuojame laiko juostą į UTC offset
        tzinfo = ZoneInfo(data.timezone)
        local_dt = dt.strptime(f"{data.date} {data.time}", "%Y-%m-%d %H:%M").replace(tzinfo=tzinfo)
        utc_offset = local_dt.utcoffset()
        offset_hours = int(utc_offset.total_seconds() // 3600)
        offset_minutes = int((utc_offset.total_seconds() % 3600) // 60)
        offset_str = f"{offset_hours:+03d}:{abs(offset_minutes):02d}"

        # Flatlib datoms
        dt_flat = Datetime(data.date, data.time, offset_str)
        pos = GeoPos(str(data.lat), str(data.lon))
        chart = Chart(dt_flat, pos)

        planets = {}
        for name in PLANETS:
            planet = chart.get(name)
            planets[name] = {
                "sign": planet.sign,
                "degree": round(float(planet.lon), 2),
                "house": planet.house
            }

        houses = {}
        for house_name in HOUSES:
            house = chart.get(house_name)
            houses[house_name] = {
                "sign": house.sign,
                "degree": round(float(house.lon), 2)
            }

        return {
            "sun_sign": chart.get('SUN').sign,
            "moon_sign": chart.get('MOON').sign,
            "ascendant": chart.get('ASC').sign,
            "planets": planets,
            "houses": houses
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant: {str(e)}")
