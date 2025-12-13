from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "Astrology API",
        "version": "1.0"
    }


class BirthData(BaseModel):
    date: str      # YYYY-MM-DD
    time: str      # HH:MM
    timezone: str  # pvz. Europe/Vilnius
    lat: float
    lon: float


@app.post("/calculate")
def calculate(data: BirthData):
    return {
        "status": "OK",
        "received": data
    }
