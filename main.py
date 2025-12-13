from fastapi import FastAPI
from pydantic import BaseModel
from kerykeion import AstrologicalSubject

app = FastAPI()

class BirthData(BaseModel):
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    timezone: str = "Europe/Vilnius"
    lat: float
    lon: float

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Astrology API", "version": "1.0"}

@app.post("/calculate")
async def calculate(data: BirthData):
    subject = AstrologicalSubject(
        name="User",
        year=int(data.date[:4]),
        month=int(data.date[5:7]),
        day=int(data.date[8:10]),
        hour=int(data.time[:2]),
        minute=int(data.time[3:5]),
        lng=data.lon,
        lat=data.lat,
        tz_str=data.timezone
    )

    # Pvz., grąžinam planetų pozicijas
    planets = {
        planet.name: {
            "sign": planet.sign,
            "position": planet.abs_pos
        } for planet in subject.planets_list
    }

    return {"status": "ok", "planets": planets, "houses": subject.houses_list}
