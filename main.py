from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pytz
import swisseph as swe


swe.set_ephe_path(".")

app = FastAPI()

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lon: float
    timezone: str

SIGNS_LT = [
    "Avinas","Jautis","Dvyniai","Vėžys","Liūtas","Mergelė",
    "Svarstyklės","Skorpionas","Šaulys","Ožiaragis","Vandenis","Žuvys"
]

PLANETS = {
    "Saulė": swe.SUN,
    "Mėnulis": swe.MOON,
    "Merkurijus": swe.MERCURY,
    "Venera": swe.VENUS,
    "Marsas": swe.MARS,
    "Jupiteris": swe.JUPITER,
    "Saturnas": swe.SATURN,
    "Uranas": swe.URANUS,
    "Neptūnas": swe.NEPTUNE,
    "Plutonas": swe.PLUTO
}

ASPECTS_LT = {
    "Sąjunga": {"angle": 0, "orb": 8},
    "Priešprieša": {"angle": 180, "orb": 8},
    "Kvadratas": {"angle": 90, "orb": 8},
    "Trigonas": {"angle": 120, "orb": 8},
    "Seksilis": {"angle": 60, "orb": 6}
}

def zodiac_position(longitude):
    sign = SIGNS_LT[int(longitude // 30)]
    degree = round(longitude % 30, 2)
    return sign, degree

def calculate_aspects(planets):
    aspects = []
    names = list(planets.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            p1, p2 = names[i], names[j]
            lon1, lon2 = planets[p1]["longitude"], planets[p2]["longitude"]
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            for name, info in ASPECTS_LT.items():
                if abs(diff - info["angle"]) <= info["orb"]:
                    aspects.append({
                        "planeta1": p1,
                        "planeta2": p2,
                        "tipas": name,
                        "laipsniai": round(diff, 2)
                    })
    return aspects

@app.post("/astro")
def calculate_astro(data: BirthData):
    local = pytz.timezone(data.timezone)
    dt_local = local.localize(datetime(data.year, data.month, data.day, data.hour, data.minute))
    dt_utc = dt_local.astimezone(pytz.utc)

    jd = swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60
    )

    planets = {}
    for name, pid in PLANETS.items():
        lon = swe.calc_ut(jd, pid)[0][0]
        sign, deg = zodiac_position(lon)
        planets[name] = {
            "laipsniai_ecliptikoje": round(lon, 4),
            "ženklas": sign,
            "laipsniai": deg
        }

    houses, ascmc = swe.houses(jd, data.lat, data.lon, b'P')
    house_data = {}
    for i in range(12):
        sign, deg = zodiac_position(houses[i])
        house_data[f"{i+1} namas"] = {
            "laipsniai_ecliptikoje": round(houses[i], 4),
            "ženklas": sign,
            "laipsniai": deg
        }

    asc_sign, asc_deg = zodiac_position(ascmc[0])
    mc_sign, mc_deg = zodiac_position(ascmc[1])

    return {
        "Ascendentas": {
            "laipsniai_ecliptikoje": round(ascmc[0], 4),
            "ženklas": asc_sign,
            "laipsniai": asc_deg
        },
        "Medium_coeli": {
            "laipsniai_ecliptikoje": round(ascmc[1], 4),
            "ženklas": mc_sign,
            "laipsniai": mc_deg
        },
        "Planetos": planets,
        "Namai": house_data,
        "Aspektai": calculate_aspects(planets)
    }
