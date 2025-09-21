# Station Meteo API (Flask)

API REST simple pour recevoir les mesures du Raspberry Pi Pico W et les stocker dans MariaDB.

## Endpoints

- `GET /health` -> statut simple
- `POST /add` -> ajoute une mesure

### Payload JSON attendu

```json
{
  "temperature": 23.4,
  "humidite": 45.6,
  "pression": 1013.2,
  "co2": 530.0,
  "humidite_surface": 12.5,
  "pluie_detectee": true,
  "indice_uv": 2.1
}
```

## Variables d'environnement

- `DB_HOST` (par defaut `127.0.0.1` ou `stationmeteo-db` en Docker)
- `DB_PORT` (par defaut `3306`)
- `DB_NAME` (par defaut `stationmeteo`)
- `DB_USER` (par defaut `pico`)
- `DB_PASS` (par defaut `motdepassepico`)
- `PORT` (par defaut `5000`)

## Lancer sur Debian (host)

Installer Python et dependances:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt
export DB_HOST=127.0.0.1  # ou IP du conteneur
export DB_NAME=stationmeteo
export DB_USER=pico
export DB_PASS=motdepassepico
python api/app.py
```

Service systemd (optionnel):
Créez `/etc/systemd/system/stationmeteo-api.service`:

```
[Unit]
Description=Station Meteo API
After=network.target docker.service mariadb.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/stationmeteo/api
Environment=DB_HOST=127.0.0.1
Environment=DB_NAME=stationmeteo
Environment=DB_USER=pico
Environment=DB_PASS=motdepassepico
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Adaptez le chemin et l'utilisateur. Puis:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now stationmeteo-api
```

## Lancer en Docker (recommandé)

Construire l'image:

```bash
cd api
docker build -t stationmeteo-api:latest .
```

Lier au conteneur MariaDB `stationmeteo-db` via le reseau Docker (meme network):

```bash
docker network create stationmeteo-net  # si non existant
# connecter la DB si besoin
# docker network connect stationmeteo-net stationmeteo-db

docker run -d --name stationmeteo-api \
  --restart unless-stopped \
  --network stationmeteo-net \
  -e DB_HOST=stationmeteo-db \
  -e DB_NAME=stationmeteo \
  -e DB_USER=pico \
  -e DB_PASS=motdepassepico \
  -p 5000:5000 \
  stationmeteo-api:latest
```

## Test rapide

```bash
curl -X POST http://SERVER_IP:5000/add \
  -H "Content-Type: application/json" \
  -d '{"temperature":22.3,"humidite":44.0,"pression":1012.8,"co2":500,"humidite_surface":10.5,"pluie_detectee":false,"indice_uv":1.8}'
```
