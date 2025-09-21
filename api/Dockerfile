# Python slim image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/

# Default env (override via -e or compose)
ENV DB_HOST=stationmeteo-db \
    DB_PORT=3306 \
    DB_NAME=stationmeteo \
    DB_USER=pico \
    DB_PASS=motdepassepico \
    PORT=5000

EXPOSE 5000
CMD ["python", "app.py"]
