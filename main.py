from fastapi import FastAPI
from pydantic import BaseModel
from kerykeion import AstrologicalSubject

app = FastAPI(
    title="Astrology API",
    description="Natal chart calculations",
    version="1.0"
)

class BirthData(BaseModel):
    name: str = "User"
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    lat: float
    lon: float
    timezone: str = "Europe/Vilnius"

@app.get("/health")
def health():
    return {"status": "ok", "service": "Astrology API"}

@app.post("/calculate")
def calculate(data: BirthData):
    subject = AstrologicalSubject(
        data.name,
        year=int(data.date[:4]),
        month=int(data.date[5:7]),
        day=int(data.date[8:10]),
        hour=int(data.time[:2]),
        minute=int(data.time[3:5]),
        lat=data.lat,
        lng=data.lon,
        tz_str=data.timezone
    )

    planets = {p.name: {"sign": p.sign, "degree": p.abs_pos, "house": p.house} for p in subject.planets_list}

    return {
        "sun_sign": subject.sun.sign,
        "moon_sign": subject.moon.sign,
        "ascendant": subject.first_house.sign,
        "planets": planets
    }
