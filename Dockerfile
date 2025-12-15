# Bazinė sistema su Python 3.11
FROM python:3.11-slim

# Atnaujiname paketus ir įdiegiame pagrindinius įrankius
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Sukuriam darbo katalogą
WORKDIR /app

# Nukopijuojam visus projektinius failus į konteinerį
COPY . /app

# Įdiegiame priklausomybes
RUN pip install --upgrade pip && \
    pip install git+https://github.com/hhershey93/flatlib.git && \
    pip install -r requirements.txt

# Nustatome, kaip paleisti aplikaciją
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
