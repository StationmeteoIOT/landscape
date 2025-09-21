# Station Météo IoT avec Raspberry Pi Pico W

Ce projet implémente une station météo complète basée sur le Raspberry Pi Pico W qui collecte des données environnementales (température, humidité, pression, qualité de l'air, indice UV et détection de pluie) et les envoie à une API pour stockage et visualisation dans une interface web inspirée de Death Stranding.

## Composants matériels

- **Raspberry Pi Pico W** - Microcontrôleur principal avec Wi-Fi
- **BME280** - Capteur de température, humidité et pression atmosphérique (I2C)
- **MQ135** - Capteur de qualité d'air/CO2 (analogique + digital)
- **Capteur de pluie** - Module avec plaque conductrice et comparateur LM393 (analogique + digital)
- **GUVA-S12SD** - Capteur UV (analogique)

## Branchements

### BME280 (I2C)
- VIN → 3.3V
- GND → GND
- SCL → GP5 (I2C0 SCL)
- SDA → GP4 (I2C0 SDA)

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
- `station_meteo.py` - Programme principal pour la collecte et l'envoi des données
- `bme280_scan.py` - Utilitaire pour détecter les capteurs BME280 sur les bus I2C
- `blink.py` - Simple test de clignotement de la LED pour vérifier que le Pico fonctionne

### Application Web (Next.js)
- `/web` - Application Next.js pour la visualisation des données
  - `/app` - Pages et composants de l'interface utilisateur
  - `/api` - Endpoints API pour la récupération des données
  - `/lib` - Utilitaires et fonctions partagées

## Configuration et exécution

### Configuration du Pico W

1. Flasher MicroPython sur le Pico W
2. Transférer les fichiers Python sur le Pico
3. Modifier les paramètres WiFi dans `station_meteo.py`
4. Redémarrer le Pico pour commencer la collecte de données

### Démarrage de l'application Web

```bash
cd web
npm install
npm run dev
```

## Points importants

1. Le capteur BME280 peut fonctionner avec deux adresses I2C différentes (0x76 ou 0x77) selon la connexion de la broche SDO
2. Le programme principal a un mécanisme de reconnexion WiFi robuste
3. Toutes les 60 secondes, les données sont envoyées à l'API
4. L'interface web se met à jour automatiquement toutes les 15 secondes

## Dépannage

- Si le BME280 n'est pas détecté, essayez le branchement alternatif sur I2C1 (voir `bme280_alternative.py`)
- Vérifiez que les capteurs analogiques renvoient des valeurs raisonnables
- Assurez-vous que l'API est accessible et que le WiFi est correctement configuré

## Améliorations futures

- Ajout de plus de capteurs (direction du vent, luminosité, etc.)
- Mode basse consommation pour une alimentation sur batterie
- Stockage local des données en cas de perte de connexion
- Alertes configurables basées sur les seuils de mesure