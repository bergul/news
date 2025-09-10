# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl ca-certificates &&     rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ=Europe/Istanbul
CMD ["python", "-m", "app.main"]
