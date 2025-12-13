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
async def calculate(data: BirthData):
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

    planets = {p.name: {"sign": p.sign, "degree": round(p.abs_pos, 2)} for p in person.planets_list}

    return {
        "sun_sign": person.sun.sign,
        "moon_sign": person.moon.sign,
        "ascendant": person.first_house.sign,
        "planets": planets
    }

except Exception as e:
        raise HTTPException(status_code=400, detail=f"Klaida skaičiuojant horoskopą: {str(e)}")
