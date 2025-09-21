# Station Meteo Web (Next.js)

A simple dashboard styled with a Death Stranding inspired theme to display measurements from the Flask API.

## Config

Create a `.env` file with:

```
API_BASE=http://stationmeteo-api:5000
```

## Development

```
pnpm install
pnpm dev
```

Open http://localhost:3000

## Build & Run (Docker)

```
docker build -t stationmeteo-web .
docker run -d --name stationmeteo-web --network stationmeteo-net -e API_BASE=http://stationmeteo-api:5000 -p 3000:3000 stationmeteo-web
```

## Compose (with existing network)

```yaml
services:
  web:
    image: stationmeteo-web:latest
    container_name: stationmeteo-web
    restart: unless-stopped
    environment:
      API_BASE: http://stationmeteo-api:5000
    ports:
      - "3000:3000"
    networks:
      - stationmeteo-net
networks:
  stationmeteo-net:
    external: true
```
