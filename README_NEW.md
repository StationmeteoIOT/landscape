# Station Météo IoT avec Raspberry Pi Pico W

![Station Météo](https://i.imgur.com/tCGkDEs.png)

## 📡 Présentation du Projet

Ce projet implémente une station météo complète basée sur le Raspberry Pi Pico W qui collecte des données environnementales (température, humidité, pression, qualité de l'air, indice UV et détection de pluie) et les envoie à une API pour stockage et visualisation dans une interface web inspirée de l'esthétique du jeu Death Stranding.

Le système fonctionne en temps réel, avec des mises à jour automatiques toutes les 10 minutes pour garantir un suivi précis des conditions environnementales tout en optimisant la lisibilité des données sur les graphiques.

## 🔧 Composants Matériels

- **Raspberry Pi Pico W** - Microcontrôleur principal avec connectivité Wi-Fi intégrée
- **BME280** - Capteur de température, humidité et pression atmosphérique (I2C)
- **MQ135** - Capteur de qualité d'air/CO2 (analogique + digital)
- **Capteur de pluie** - Module avec plaque conductrice et comparateur LM393 (analogique + digital)
- **GUVA-S12SD** - Capteur UV (analogique)

## 📋 Branchements

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

## 🧰 Technologies Utilisées

### Côté Microcontrôleur
- **MicroPython** : Implémentation Python légère pour microcontrôleurs
- **Pilotes personnalisés** : Classes spécifiques pour chaque capteur (BME280_Simple, MQ135, RainSensor, UVSensor)
- **Gestion WiFi robuste** : Reconnexion automatique et gestion des erreurs réseau
- **Communication HTTP** : Requêtes POST vers l'API pour transmettre les données

### Backend (API)
- **Python** : Langage backend principal
- **Flask** : Framework web léger pour l'API REST
- **SQLite/SQLAlchemy** : Base de données relationnelle et ORM
- **Alembic** : Gestion des migrations de base de données
- **Docker** : Conteneurisation pour déploiement simplifié

### Frontend (Interface Web)
- **Next.js 14** : Framework React moderne avec fonctionnalités SSR et CSR
- **TypeScript** : Typage statique pour JavaScript
- **CSS-in-JS** : Styles intégrés directement dans les composants
- **Visualisation graphique** : Affichage temporel des données avec interactions
- **API Routes** : Proxy interne pour éviter les problèmes CORS
- **Client-side fetching** : Récupération des données et mise à jour automatique

## 🗂️ Structure du Projet

```
Station-meteo/
├── README.md                    # Documentation du projet
├── station_meteo.py             # Code MicroPython principal pour le Pico W
├── blink.py                     # Test LED pour vérifier le fonctionnement du Pico W
├── api/                         # Backend API
│   ├── app.py                   # Application Flask principale
│   ├── models.py                # Modèles de données SQLAlchemy
│   ├── migrations/              # Migrations Alembic
│   ├── Dockerfile               # Configuration Docker pour l'API
│   └── requirements.txt         # Dépendances Python
└── web/                         # Frontend Next.js
    ├── app/                     # Structure de l'application Next.js
    │   ├── layout.tsx           # Layout principal avec typographie et styles
    │   ├── page.tsx             # Page d'accueil avec données actuelles
    │   ├── data/                # Page de visualisation de données
    │   │   └── page.tsx         # Graphiques et tableau de données historiques
    │   └── api/                 # Routes API du frontend
    │       └── measures/        # Proxy pour l'API backend
    │           └── route.ts     # Route API pour les mesures
    ├── lib/                     # Bibliothèques utilitaires
    │   └── date.ts              # Fonctions de formatage de dates
    ├── public/                  # Ressources statiques
    ├── Dockerfile               # Configuration Docker pour le frontend
    └── package.json             # Configuration NPM et dépendances JavaScript
```

## 📊 Fonctionnalités

### Collecte de Données (Pico W)
- **Mesures précises** :
  - Température (°C) avec compensation
  - Humidité (%) avec calibration
  - Pression atmosphérique (hPa)
  - CO2 approximatif (ppm)
  - Humidité de surface (%)
  - Détection de pluie (OUI/NON)
  - Indice UV
- **Fiabilité** :
  - Calibration automatique des capteurs
  - Valeurs de secours en cas de défaillance matérielle
  - Gestion robuste de la connexion WiFi
  - Envoi périodique toutes les 10 minutes
  
### API Backend
- **Endpoints RESTful** :
  - `POST /add` : Ajoute de nouvelles mesures
  - `GET /measures` : Récupère l'historique des mesures
  - `GET /health` : Vérification de l'état du service
  - `GET /mesures` : Alias en français (même fonctionnalité que /measures)
- **Traitement des données** :
  - Validation des entrées
  - Horodatage automatique
  - Stockage persistant en base de données
  - Gestion d'erreurs robuste

### Interface Web
- **Page d'accueil** :
  - Conditions météorologiques actuelles
  - Horloge en temps réel avec date
  - Icône animée dynamique selon les conditions (pluie, soleil, nuages)
  - Panneau latéral avec résumé des mesures récentes
  - Mise à jour automatique toutes les 15 secondes
  - Design inspiré de Death Stranding avec animations subtiles
  - Fond animé avec particules et effets visuels

- **Page de Données** :
  - Graphiques temporels pour chaque type de mesure
  - Filtrage intelligent (1 point toutes les 10 minutes) pour une meilleure lisibilité
  - Tableau complet de toutes les mesures historiques
  - Tooltips interactifs sur les points des graphiques
  - Statistiques (min/max/moyenne) pour chaque mesure
  - Mise à jour automatique toutes les 60 secondes
  - Navigation intuitive entre les pages

## ⚙️ Configuration et Installation

### Pico W (MicroPython)
1. Flasher le firmware MicroPython sur le Raspberry Pi Pico W
2. Transférer `station_meteo.py` sur le Pico W
3. Configurer les paramètres WiFi et l'URL de l'API dans le script:
   ```python
   API_URL = 'http://votre-serveur:5000/add'
   WIFI_SSID = 'votre-ssid'
   WIFI_PASS = 'votre-mot-de-passe'
   ```
4. Brancher les capteurs selon le schéma de câblage
5. Redémarrer le Pico pour commencer la collecte de données

### API Backend (Docker)
```bash
# Se placer dans le répertoire api
cd api

# Construire l'image Docker
docker build -t station-meteo-api .

# Lancer le conteneur
docker run -d -p 5000:5000 --name station-meteo-api station-meteo-api
```

### Frontend Web (Docker)
```bash
# Se placer dans le répertoire web
cd web

# Construire l'image Docker
docker build -t station-meteo-web .

# Lancer le conteneur
docker run -d -p 3000:3000 --name station-meteo-web station-meteo-web
```

### Démarrage manuel de l'application Web (développement)
```bash
cd web
npm install
npm run dev
```

## 🔄 Flux de Données
1. Les capteurs collectent des données environnementales toutes les 2 secondes
2. Les valeurs sont moyennées et validées par le Pico W
3. Toutes les 10 minutes, les données sont envoyées à l'API backend via HTTP POST
4. L'API valide et stocke les données dans la base SQLite
5. Le frontend récupère les données via l'API et les affiche sous forme de graphiques et tableaux
6. L'interface se met à jour automatiquement pour afficher les données en temps réel

## 🎨 Design et UI
L'interface utilisateur est inspirée de l'esthétique futuriste du jeu Death Stranding, avec :
- **Palette de couleurs** : Noir profond, bleu nuit, cyan, accents lumineux
- **Typographie** :
  - **Rajdhani** : Police principale pour les textes et données numériques
  - **Barlow Condensed** : Utilisée pour les en-têtes et sous-titres
  - **Share Tech Mono** : Utilisée pour les détails techniques
- **Éléments visuels** :
  - Effet scanline subtil
  - Cartes avec bordures lumineuses
  - Animations météo contextuelles
  - Fond dynamique avec particules flottantes
  - Icônes animées pour les conditions météo

## 🚨 Points Importants

1. Le capteur BME280 peut fonctionner avec deux adresses I2C différentes (0x76 ou 0x77) selon la connexion de la broche SDO
2. Le programme principal a un mécanisme de reconnexion WiFi robuste qui gère plusieurs scénarios d'erreur
3. L'intervalle d'envoi des données est réglé à 10 minutes pour optimiser la lisibilité des graphiques
4. L'interface web se met à jour automatiquement sans nécessiter de rechargement de page
5. Le système est conçu pour être résilient aux pannes de capteurs individuels

## ❓ Dépannage

### Pico W
- **BME280 non détecté** : Le code essaie automatiquement les deux adresses possibles (0x76 et 0x77)
- **Valeurs anormales** : Vérifiez l'alimentation stable du Pico W (5V recommandé)
- **Problèmes de connexion WiFi** : Le code réessaie automatiquement et scanne les réseaux disponibles
- **Échec d'envoi API** : Vérifiez que l'API est accessible depuis le réseau du Pico W

### API
- **Erreur 500** : Vérifiez les logs du conteneur Docker
- **Problèmes de base de données** : Les migrations sont exécutées automatiquement au démarrage
- **Performance dégradée** : Envisagez une purge des anciennes données

### Frontend
- **Pas de données affichées** : Vérifiez que l'API est accessible
- **Problèmes de graphiques** : Vérifiez la console du navigateur pour les erreurs
- **Incompatibilité d'affichage** : Testez sur des navigateurs modernes (Chrome, Firefox, Edge)

## 🔍 Possibilités d'Extension

- **Hardware** :
  - Ajout de capteurs de luminosité, anémomètre, pluviomètre
  - Alimentation solaire et batterie pour installation extérieure autonome
  - Boîtier imprimé 3D résistant aux intempéries
  
- **Software** :
  - Alertes par email/SMS sur seuils dépassés
  - Apprentissage automatique pour prédictions météo locales
  - Application mobile native (React Native/Flutter)
  - Intégration avec les assistants domotiques (Home Assistant, etc.)
  - Stockage local sur carte SD en cas de perte de connexion

## 👥 Contributeurs
- Équipe du Projet N04 IOT

## 📜 Licence
Ce projet est développé dans le cadre d'un projet scolaire et reste la propriété intellectuelle de ses auteurs.

---

© 2025 - Projet Collaboratif N04 IOT