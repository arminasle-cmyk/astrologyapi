from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kerykeion import AstrologicalSubject

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
    timezone: str = "Europe/Vilnius"

@app.get("/")
async def root():
    return {"message": "Astrology API veikia! 🌟 Naudok /docs testavimui. Bandymas"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.1"}

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

        # Planetos su house info
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto"
        ]

        planets = {
            name.capitalize(): {
                "sign": planet.sign,
                "degree": round(planet.abs_pos, 2),
                "house": planet.house
            }
            for name in planet_names
            if (planet := getattr(person, name))
        }

        # Astrologiniai namai
        houses = {
            house.name: {
                "sign": house.sign,
                "degree": round(house.abs_pos, 2)
            }
            for house in person.houses_list
        }

        return {
            "sun_sign": person.sun.sign,
            "moon_sign": person.moon.sign,
            "ascendant": getattr(person.first_house, "sign", "Nežinomas"),
            "planets": planets,
            "houses": houses
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant: {str(e)}")
