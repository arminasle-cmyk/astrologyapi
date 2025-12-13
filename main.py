from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "Astrology API",
        "version": "1.0"
    }
