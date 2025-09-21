# Guide d'utilisation de la Station Météo IoT

Ce guide vous aidera à installer, configurer et utiliser votre station météo IoT basée sur le Raspberry Pi Pico W.

## Table des matières

1. [Contenu du kit](#contenu-du-kit)
2. [Prérequis](#prérequis)
3. [Installation matérielle](#installation-matérielle)
   - [Branchement des capteurs](#branchement-des-capteurs)
   - [Schéma complet](#schéma-complet)
4. [Installation logicielle](#installation-logicielle)
   - [Préparation du Pico W](#préparation-du-pico-w)
   - [Configuration du WiFi](#configuration-du-wifi)
5. [Utilisation de la station météo](#utilisation-de-la-station-météo)
   - [Démarrage de la station](#démarrage-de-la-station)
   - [Interprétation des données](#interprétation-des-données)
   - [Accès à l'interface web](#accès-à-linterface-web)
6. [Résolution des problèmes](#résolution-des-problèmes)
7. [Maintenance](#maintenance)
8. [Extensions possibles](#extensions-possibles)

## Contenu du kit

- 1 × Raspberry Pi Pico W
- 1 × Capteur BME280 (température, humidité, pression)
- 1 × Capteur MQ135 (qualité d'air)
- 1 × Capteur de pluie avec plaque
- 1 × Capteur UV GUVA-S12SD
- Câbles Dupont pour les connexions
- Optionnel: Boîtier de protection

## Prérequis

- Un ordinateur avec Thonny IDE ou VS Code + extension MicroPython
- Connexion WiFi 2.4 GHz
- Câble micro-USB pour connecter le Pico W
- Connaissances de base en électronique

## Installation matérielle

### Branchement des capteurs

#### BME280 (Température, Humidité, Pression)

```
BME280     Raspberry Pi Pico W
-------    ----------------
VIN/VCC -> 3.3V (PIN 36)
GND     -> GND (PIN 38)
SCL     -> GP5 (PIN 7)
SDA     -> GP4 (PIN 6)
```

#### MQ135 (Qualité d'air)

```
MQ135      Raspberry Pi Pico W
-------    ----------------
VCC     -> 3.3V (PIN 36)
GND     -> GND (PIN 38)
AO      -> GP26 (PIN 31) [ADC0]
DO      -> GP14 (PIN 19)
```

#### Capteur de pluie

```
RAIN       Raspberry Pi Pico W
-------    ----------------
VCC     -> 3.3V (PIN 36)
GND     -> GND (PIN 38)
AO      -> GP28 (PIN 34) [ADC2]
DO      -> GP15 (PIN 20)
```

#### Capteur UV

```
UV         Raspberry Pi Pico W
-------    ----------------
VCC     -> 3.3V (PIN 36)
GND     -> GND (PIN 38)
OUT     -> GP27 (PIN 32) [ADC1]
```

### Schéma complet

```
+----------+          +----------+
|  BME280  |          |  MQ135   |
+----------+          +----------+
| VCC  GND |          | VCC  GND |
| SCL  SDA |          | AO   DO  |
+----------+          +----------+
   |    |                |    |
   |    |                |    |
+-----------------------------+
|    Raspberry Pi Pico W      |
|                             |
| 3V3 -----------------+      |
| GND -----------------+--+   |
| GP4 (SDA) ----------+| |    |
| GP5 (SCL) ---------+|| |    |
| GP26 (ADC0) -------+|| |    |
| GP14 -------------+ ||| |   |
|                    | ||| |   |
+--------------------|-|||-|---+
                     | ||| |
+----------+         | ||| |   +----------+
|   RAIN   |         | ||| |   |    UV    |
+----------+         | ||| |   +----------+
| VCC  GND |         | ||| |   | VCC  GND |
| AO   DO  |         | ||| |   | OUT      |
+----------+         | ||| |   +----------+
   |    |            | ||| |      |
   |    |            | ||| |      |
   |    +------------+ ||| |      |
   |    +--------------||| |      |
   |    +-------------+||| |      |
   |    +-------------+||| |      |
   |                   ||| |      |
   |    +--------------+|| |      |
   |    +--------------+|| |      |
   |                    || |      |
   |    +---------------+| |      |
   |    +----------------+ |      |
   |                       |      |
   |    +------------------+      |
   |    |                         |
   +----+                         |
   +----------------------------+
```

## Installation logicielle

### Préparation du Pico W

1. Téléchargez la dernière version de MicroPython pour le Raspberry Pi Pico W sur le [site officiel](https://micropython.org/download/rp2-pico-w/)

2. Connectez le Pico W à votre ordinateur en maintenant le bouton BOOTSEL enfoncé

3. Relâchez le bouton une fois connecté, le Pico apparaîtra comme un périphérique de stockage

4. Copiez le fichier .uf2 téléchargé sur ce périphérique pour flasher MicroPython

5. Le Pico redémarrera automatiquement et disparaîtra du gestionnaire de fichiers

6. Ouvrez Thonny IDE et sélectionnez "MicroPython (Raspberry Pi Pico)" dans le menu d'interpréteur (coin inférieur droit)

7. Transférez les fichiers suivants sur le Pico W:
   - `station_meteo.py`
   - `bme280_scan.py` (utilitaire)
   - `test_sensors.py` (utilitaire)

### Configuration du WiFi

Ouvrez le fichier `station_meteo.py` et modifiez les paramètres WiFi:

```python
# Parametres API (adapter SERVER_IP ou nom DNS)
API_URL = 'http://VOTRE_SERVEUR:5000/add'
WIFI_SSID = 'VOTRE_SSID_WIFI'
WIFI_PASS = 'VOTRE_MOT_DE_PASSE_WIFI'
```

> **Important**: N'utilisez que des réseaux WiFi 2.4 GHz. Le Pico W ne peut pas se connecter aux réseaux 5 GHz.

## Utilisation de la station météo

### Démarrage de la station

1. Connectez tous les capteurs selon le schéma

2. Exécutez d'abord `test_sensors.py` pour vérifier que tous les capteurs fonctionnent correctement

3. Une fois les tests réussis, exécutez `station_meteo.py` pour démarrer la collecte des données

4. Les mesures s'afficheront dans la console toutes les 2 secondes et seront envoyées à l'API toutes les 60 secondes

### Interprétation des données

- **Température**: Affichée en °C, plage normale -10°C à +40°C
- **Humidité**: Affichée en %, 0% (air sec) à 100% (saturé)
- **Pression**: Affichée en hPa, typiquement autour de 1013.25 hPa (pression au niveau de la mer)
- **CO2**: En ppm (parties par million), une valeur saine est <1000 ppm
- **Humidité surface**: En %, indique le niveau d'humidité détecté par le capteur de pluie
- **Indice UV**: Échelle de 0 à 11+
   - 0-2: Faible
   - 3-5: Modéré
   - 6-7: Élevé
   - 8-10: Très élevé
   - 11+: Extrême

### Accès à l'interface web

1. Si vous utilisez l'API distante:
   - Accédez à l'URL fournie pour votre projet

2. Si vous hébergez votre propre serveur:
   - Assurez-vous que le serveur API est en cours d'exécution
   - Lancez l'application web Next.js:
     ```bash
     cd web
     npm install
     npm run dev
     ```
   - Accédez à `http://localhost:3000` dans votre navigateur

## Résolution des problèmes

### Le BME280 n'est pas détecté

1. Vérifiez les connexions, notamment SDA et SCL
2. Essayez l'autre adresse I2C (0x76 ou 0x77) en connectant SDO à GND ou à 3.3V
3. Essayez le bus I2C1 alternatif (GP2/GP3)
4. Exécutez `bme280_scan.py` pour voir si le capteur est détecté

### Les valeurs semblent incorrectes

- **Température anormale**: Vérifiez que le capteur n'est pas exposé à une source de chaleur directe
- **Humidité > 100%**: Problème de calibration ou de calcul, redémarrez le Pico
- **Valeurs CO2 instables**: Le capteur MQ135 nécessite un temps de chauffe, attendez 24h pour des valeurs stables

### Problèmes de connexion WiFi

1. Vérifiez que le SSID et le mot de passe sont corrects
2. Assurez-vous que le réseau est en 2.4 GHz (pas 5 GHz)
3. Vérifiez que le signal WiFi est assez fort là où est placée la station
4. Si le réseau est masqué, essayez de le rendre visible temporairement

## Maintenance

- **Nettoyage**: Dépoussiérez régulièrement les capteurs avec une brosse douce ou de l'air comprimé
- **Calibration**: Recalibrez le capteur de CO2 tous les 6 mois en le plaçant dans un environnement d'air frais
- **Vérification**: Exécutez `test_sensors.py` mensuellement pour vérifier le bon fonctionnement

## Extensions possibles

- **Alimentation solaire**: Ajoutez un panneau solaire et une batterie pour l'autonomie
- **Capteurs supplémentaires**:
  - Anémomètre pour la vitesse du vent
  - Girouette pour la direction du vent
  - Capteur de luminosité
  - Détecteur de foudre AS3935
- **Boîtier extérieur**: Installez la station dans un boîtier résistant aux intempéries pour l'utilisation extérieure
- **Affichage local**: Ajoutez un écran OLED pour afficher les données sans ordinateur