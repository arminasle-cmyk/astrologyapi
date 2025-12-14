from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kerykeion import AstrologicalSubject

app = FastAPI(
    title="Astrology API",
    description="Natal chart ir planetų pozicijų skaičiavimas",
    version="1.0"
)

class BirthData(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    lat: float
    lon: float
    timezone: str = "Europe/Vilnius"

@app.get("/")
async def root():
    return {"message": "Astrology API veikia! 🌟 Naudok /docs testavimui."}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0"}

@app.post("/calculate")
async def calculate(data: BirthData):
    try:
        person = AstrologicalSubject(
            "User",
            year=int(data.date[:4]),
            month=int(data.date[5:7]),
            day=int(data.date[8:10]),
            hour=int(data.time[:2]),
            minute=int(data.time[3:5]),
            lat=data.lat,
            lng=data.lon,
            tz_str=data.timezone
        )

        # Planetų vardai pagal kerykeion
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto"
        ]

        planets = {
            name.capitalize(): {
                "sign": getattr(person, name).sign,
                "degree": round(getattr(person, name).abs_pos, 2)
            }
            for name in planet_names
        }

        return {
            "sun_sign": person.sun.sign,
            "moon_sign": person.moon.sign,
            "ascendant": getattr(person.first_house, "sign", "Nežinomas"),
            "planets": planets
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant: {str(e)}")
