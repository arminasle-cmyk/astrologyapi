from fastapi import FastAPI
from pydantic import BaseModel
from kerykeion import AstrologicalSubject  # jei naudoji kerykeion

app = FastAPI(
    title="Astrology API",
    description="Natal chart ir planetų pozicijų skaičiavimas",
    version="1.0"
)

class BirthData(BaseModel):
    date: str      # pvz. "1990-05-15"
    time: str      # pvz. "14:30"
    lat: float     # pvz. 54.6872 (Vilnius)
    lon: float     # pvz. 25.2797 (Vilnius)
    timezone: str = "Europe/Vilnius"  # pagal nutylėjimą Vilnius

# 1. Pridėk root endpoint'ą – kad pagrindinis URL rodytų kažką gražaus
@app.get("/")
async def root():
    return {
        "message": "Sveiki atvykę į Astrology API! 🌟",
        "docs": "/docs",           # automatiškai sugeneruota interaktyvi dokumentacija
        "redoc": "/redoc",         # alternatyvi dokumentacija
        "health": "/health"
    }

# 2. /health jau turi, palik kaip yra
@app.get("/health")
async def health():
    return {"status": "ok", "service": "Astrology API", "version": "1.0"}

# 3. /calculate – įsitikink, kad tikrai yra POST metodas
@app.post("/calculate")
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

        # Planetos pasiekiamos tiesiogiai kaip atributai (naujausia kerykeion versija)
        planets = {
            "Sun": {"sign": person.sun.sign, "degree": round(person.sun.abs_pos, 2), "house": person.sun.house if hasattr(person.sun, 'house') else None},
            "Moon": {"sign": person.moon.sign, "degree": round(person.moon.abs_pos, 2), "house": person.moon.house if hasattr(person.moon, 'house') else None},
            "Mercury": {"sign": person.mercury.sign, "degree": round(person.mercury.abs_pos, 2)},
            "Venus": {"sign": person.venus.sign, "degree": round(person.venus.abs_pos, 2)},
            "Mars": {"sign": person.mars.sign, "degree": round(person.mars.abs_pos, 2)},
            "Jupiter": {"sign": person.jupiter.sign, "degree": round(person.jupiter.abs_pos, 2)},
            "Saturn": {"sign": person.saturn.sign, "degree": round(person.saturn.abs_pos, 2)},
            "Uranus": {"sign": person.uranus.sign, "degree": round(person.uranus.abs_pos, 2)},
            "Neptune": {"sign": person.neptune.sign, "degree": round(person.neptune.abs_pos, 2)},
            "Pluto": {"sign": person.pluto.sign, "degree": round(person.pluto.abs_pos, 2)},
        }

        return {
            "sun_sign": person.sun.sign,
            "moon_sign": person.moon.sign,
            "ascendant": person.first_house.sign if hasattr(person, 'first_house') else "N/A",
            "planets": planets
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant horoskopą: {str(e)}")
