# Station météo IoT – Pico W + API + Web

Une station météo connectée basée sur Raspberry Pi Pico W (MicroPython), qui lit plusieurs capteurs (BME280, MQ135, pluie, UV), envoie les mesures à une API backend, stocke en base, et les affiche côté web (UI inspirée de Death Stranding).

## 🌐 Liens rapides

- API (base): http://51.91.141.222:5000
- API santé: http://51.91.141.222:5000/health
- API ajout mesure (POST): http://51.91.141.222:5000/add
- Backend (server) – dépôt: à compléter
- Frontend (web) – dépôt: à compléter

> Mettez à jour les deux liens “à compléter” avec vos dépôts GitHub si disponibles.

---

## 🔭 Architecture

```
[Raspberry Pi Pico W]
   ├─ BME280 (I2C1: SDA GP6, SCL GP7)
   ├─ MQ135   (ADC0: GP26, digital: GP14)
   ├─ Pluie   (ADC2: GP28, digital: GP15)
   └─ UV (GUVA) (ADC1: GP27)
  ↓ Wi‑Fi (scan + reconnexion)
[API / Server]
  ↓
[Base de données]  ←→  [Dashboard Web]
```

- Cadence d’envoi: toutes les 30 secondes (configurable).
- Calibration et persistance locales: `mq135_cal.json`, `uv_cal.json`, `rain_cal.json`.

---

## 🧩 Composants matériels

- **Raspberry Pi Pico W** - Microcontrôleur principal avec Wi-Fi
- **BME280** - Capteur de température, humidité et pression atmosphérique (I2C)
- **MQ135** - Capteur de qualité d'air/CO2 (analogique + digital)
- **Capteur de pluie** - Module avec plaque conductrice et comparateur LM393 (analogique + digital)
- **GUVA-S12SD** - Capteur UV (analogique)

## Branchements

### BME280 (I2C1 recommandé)
- VIN → 3.3V
- GND → GND
- SCL → GP7 (I2C1 SCL)
- SDA → GP6 (I2C1 SDA)

### MQ135 (Qualité d'air)
- VCC → 3.3V
- GND → GND
- AO → GP26 (ADC0)
- DO → GP14 (entrée digitale)

### Capteur de pluie
- VCC → 3.3V
- GND → GND
- AO → GP28 (ADC2)
- DO → GP15 (entrée digitale)

### GUVA-S12SD (UV)
- VCC → 3.3V
- GND → GND
- OUT → GP27 (ADC1)

## Structure du projet

### Fichiers MicroPython (Pico W)
- `station_meteo.py` - Programme principal (collecte, Wi‑Fi, envoi API, logs détaillés)
- `blink.py` - Test LED pour vérifier la carte

Persistences locales côté Pico W:
- `mq135_cal.json` – calibration MQ135 (R0)
- `uv_cal.json` – offset/échelle UV
- `rain_cal.json` – bornes sec/mouillé pluie

### Application Web (Next.js)
- `/web` - Application Next.js pour la visualisation des données (police Rajdhani, esthétique DS)

## ⚙️ Configuration et exécution

### Configuration du Pico W

1. Flasher MicroPython sur le Pico W
2. Transférer les fichiers Python sur le Pico
3. Modifier les paramètres Wi‑Fi et l’URL API dans `station_meteo.py`
4. Redémarrer le Pico pour commencer la collecte de données

### Démarrage de l'application Web

```bash
cd web
npm install
npm run dev
```

## ✅ Fonctionnalités firmware clés

- Wi‑Fi UX améliorée: scan et affichage des réseaux disponibles avant et pendant la connexion, logs de progression, reconnexion automatique.
- BME280 robuste sur I2C1 (GP6/GP7):
  - Détection d’adresse 0x76/0x77
  - Repli de fréquence: 100 kHz → 50 kHz → 10 kHz
  - Logs détaillés pour faciliter le diagnostic
- MQ135:
  - Calcul Rs correct, calibration R0 en air propre (~400 ppm) avec persistance
  - Lissage et correction prudente selon T/H
- Pluie:
  - EMA (lissage), suivi dynamique des bornes sec/mouillé avec persistance
  - Normalisation 0–100% + hystérésis pluie
- UV (GUVA):
  - Offset sombre (obscurité) avec adaptation lente (p5), lissage
  - Auto‑scale optionnel (p95 → UVI cible) pour éviter valeurs trop basses/hautes
  - Plafond raisonnable à UVI 12

## 📦 API – Endpoints

- Santé: `GET /health`
  - Utilité: vérifier que le serveur répond.
  - Réponse attendue: HTTP 200 (contenu simple, p.ex. "OK").

- Ajout mesure: `POST /add`
  - Corps JSON (exemple ci‑dessous)
  - Réponse: HTTP 200–299 si OK

Exemple `POST /add`:

```json
{
  "temperature": 22.7,
  "humidite": 48.5,
  "pression": 1012.8,
  "co2": 560.3,
  "humidite_surface": 12.4,
  "pluie_detectee": false,
  "indice_uv": 1.8
}
```

Exemples cURL (optionnels):

```bash
# Vérifier l’API
curl -s http://51.91.141.222:5000/health

# Envoyer une mesure de test
curl -X POST http://51.91.141.222:5000/add \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 22.7,
    "humidite": 48.5,
    "pression": 1012.8,
    "co2": 560.3,
    "humidite_surface": 12.4,
    "pluie_detectee": false,
    "indice_uv": 1.8
  }'
```

---

## 🗄️ Base de données

Table `mesures`

| Colonne           | Type SQL                       | Description                                        |
|-------------------|--------------------------------|----------------------------------------------------|
| id                | INT AUTO_INCREMENT PRIMARY KEY | Identifiant unique                                 |
| timestamp         | DATETIME                       | Date et heure de la mesure                         |
| temperature       | FLOAT                          | Température en °C                                  |
| humidite          | FLOAT                          | Humidité en %                                      |
| pression          | FLOAT                          | Pression en hPa                                    |
| co2               | FLOAT                          | Concentration de CO₂ (ppm)                         |
| humidite_surface  | FLOAT                          | Humidité détectée par la plaque pluie (0–100%)     |
| pluie_detectee    | BOOLEAN                        | 0 = pas de pluie, 1 = pluie détectée               |
| indice_uv         | FLOAT                          | Indice UV calculé                                  |

DDL de référence (MySQL/MariaDB):

```sql
CREATE TABLE IF NOT EXISTS mesures (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  temperature FLOAT,
  humidite FLOAT,
  pression FLOAT,
  co2 FLOAT,
  humidite_surface FLOAT,
  pluie_detectee BOOLEAN,
  indice_uv FLOAT
);
```

> Selon le SGBD, `BOOLEAN` peut être mappé en `TINYINT(1)`.

Correspondance API → DB:
- `temperature` → `temperature`
- `humidite` → `humidite`
- `pression` → `pression`
- `co2` → `co2`
- `humidite_surface` → `humidite_surface`
- `pluie_detectee` → `pluie_detectee`
- `indice_uv` → `indice_uv`
- `timestamp` est renseigné côté DB (DEFAULT CURRENT_TIMESTAMP) ou côté serveur.

---

## 🧪 Qualité des données & calibrations

- MQ135 (CO₂ approx.)
  - Besoin de chauffe (plusieurs minutes)
  - Calibration R0 en air propre (~400 ppm) automatique et persistée
  - Fichier: `mq135_cal.json`
- UV (GUVA)
  - Offset sombre calibré (couvrez le capteur) et adaptable lentement (5e percentile)
  - Auto‑scale optionnel (95e percentile → UVI cible, par défaut 8) pour rester plausible
  - Fichier: `uv_cal.json`
- Pluie
  - EMA + bornes sec/mouillé dynamiques avec persistance
  - Fichier: `rain_cal.json`

---

## 🛠️ Dépannage

- BME280 non détecté
  - Vérifiez le câblage I2C1: SDA GP6, SCL GP7
  - Observez les logs: adresses détectées (0x76/0x77) et fréquence utilisée
  - Si nécessaire, testez à 50 kHz puis 10 kHz (déjà automatisé)
- Wi‑Fi n’accroche pas
  - Confirmez SSID/mot de passe
  - Vérifiez la liste des réseaux scannée dans les logs
  - Évitez les caractères spéciaux non ASCII dans l’ESSID si possible
- UVI aberrant la nuit
  - Couvrez le capteur quelques secondes pour (re)calibrer l’offset sombre
  - Supprimez `uv_cal.json` pour repartir de zéro
- Valeurs CO₂ incohérentes
  - Laissez chauffer le MQ135, puis recalibrez en air propre (supprimer `mq135_cal.json`)
- Humidité de surface toujours basse/haute
  - Laissez la station tourner quelques minutes pour apprendre les bornes sec/mouillé
  - Vérifiez `rain_cal.json`

---

## 🔒 Sécurité & durcissement

- L’endpoint `/add` est exposé; pensez à ajouter une authentification (clé API, token) et une validation stricte côté serveur.
- Limitez l’origine (CORS) et le débit si nécessaire.

---

## 📃 Licence

Spécifiez la licence du projet ici (MIT, Apache-2.0, etc.).

---

## 🙌 Remerciements

- Communauté MicroPython & Raspberry Pi Pico W
- Contributeurs du projet

---

## 🧭 À faire (idées)

- Ajouter un mode maintenance pour forcer des calibrations
- Graphiques historiques côté web (moyennes/percentiles)
- Authentification API et chiffrement (HTTPS)

## Améliorations futures

- Ajout de plus de capteurs (direction du vent, luminosité, etc.)
- Mode basse consommation pour une alimentation sur batterie
- Stockage local des données en cas de perte de connexion
- Alertes configurables basées sur les seuils de mesure