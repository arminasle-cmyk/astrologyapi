from fastapi import FastAPI
from pydantic import BaseModel
from kerykeion import AstrologicalSubject

app = FastAPI(title="Astrology API", version="1.0")

class BirthData(BaseModel):
    date: str      # "1990-05-15"
    time: str    # "14:30"
    lat: float
    lon: float
    timezone: str = "Europe/Vilnius"

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Astrology API"}

@app.post("/calculate")
async def calculate(data: BirthData):
    person = AstrologicalSubject(
        "User",
        year=int(data.date[:4]),
        month=int(data.date[5:7]),
        day=int(data.date[8:10]),
        hour=int(data.time[:2]),
        minute=int(data.time[3:5]),
        lng=data.lon,
        lat=data.lat,
        tz_str=data.timezone
    )

    return {
        "sun": person.sun.sign,
        "moon": person.moon.sign,
        "ascendant": person.first_house.sign,
        "planets": {p.name: p.sign for p in person.planets_list}
    }
