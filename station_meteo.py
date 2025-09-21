from machine import Pin, I2C, ADC
import utime
from micropython import const
import network
import ujson
try:
    import rp2
except Exception:
    rp2 = None
try:
    import uos as os
except Exception:
    os = None
try:
    import sys
except Exception:
    sys = None
try:
    import urequests as requests
except Exception:
    requests = None

# BME280 - Constantes d'adresse
BME280_I2C_ADDR_PRIM = const(0x76)
BME280_I2C_ADDR_SEC = const(0x77)

# BME280 - Constantes de registres
BME280_REG_CHIP_ID = const(0xD0)
BME280_CHIP_ID = const(0x60)
BME280_REG_RESET = const(0xE0)
BME280_REG_CTRL_HUM = const(0xF2)
BME280_REG_STATUS = const(0xF3)
BME280_REG_CTRL_MEAS = const(0xF4)
BME280_REG_CONFIG = const(0xF5)
BME280_REG_DATA = const(0xF7)

# BME280 - Registres de calibration
BME280_REG_TEMP_CALIB = const(0x88)
BME280_REG_PRESS_CALIB = const(0x8E)
BME280_REG_HUM_CALIB_1 = const(0xA1)
BME280_REG_HUM_CALIB_2 = const(0xE1)

class BME280_Simple:
    """Classe simplifiée et robuste pour le capteur BME280"""
    
    def __init__(self, i2c, addr=None):
        self.i2c = i2c
        # Facteurs de calibration (peuvent être ajustés pour améliorer la précision)
        self.temp_offset = 0.0      # Offset de température en °C
        self.hum_factor = 1.0       # Facteur multiplicateur pour l'humidité
        self.hum_offset = 0.0       # Offset d'humidité en %
        self.pressure_offset = 0.0  # Offset de pression en hPa
        
        # Recherche auto de l'adresse si non spécifiée
        if addr is None:
            addresses = [BME280_I2C_ADDR_PRIM, BME280_I2C_ADDR_SEC]
            for address in addresses:
                try:
                    if address in i2c.scan():
                        chip_id = i2c.readfrom_mem(address, BME280_REG_CHIP_ID, 1)[0]
                        if chip_id == BME280_CHIP_ID:
                            self.addr = address
                            print(f"BME280 trouvé à l'adresse: 0x{address:02x}")
                            break
                except:
                    pass
            else:
                raise RuntimeError("BME280 non trouvé. Vérifiez les connexions.")
        else:
            self.addr = addr
            chip_id = i2c.readfrom_mem(self.addr, BME280_REG_CHIP_ID, 1)[0]
            if chip_id != BME280_CHIP_ID:
                raise RuntimeError(f"ID incorrect: 0x{chip_id:02x} (attendu: 0x{BME280_CHIP_ID:02x})")
        
        # Reset du capteur
        i2c.writeto_mem(self.addr, BME280_REG_RESET, b'\xB6')
        utime.sleep_ms(200)
        
        # Attendre que le capteur soit prêt
        while i2c.readfrom_mem(self.addr, BME280_REG_STATUS, 1)[0] & 0x01:
            utime.sleep_ms(10)
        
        # Lire les coefficients de calibration
        self._read_coefficients()
        
        # Configuration du capteur
        # Oversampling: x1 pour temp, x1 pour pression, x1 pour humidité
        # Mode: forcé (0)
        self.i2c.writeto_mem(self.addr, BME280_REG_CTRL_HUM, b'\x01')  # Humidité x1
        self.i2c.writeto_mem(self.addr, BME280_REG_CTRL_MEAS, b'\x25')  # Temp x1, Press x1, Force mode
        
        # Un petit délai pour que tout soit prêt
        utime.sleep_ms(100)
    
    def _read_coefficients(self):
        """Lecture des coefficients de calibration"""
        # Température et pression
        calib = self.i2c.readfrom_mem(self.addr, BME280_REG_TEMP_CALIB, 24)
        
        self.dig_T1 = calib[0] | (calib[1] << 8)
        self.dig_T2 = calib[2] | (calib[3] << 8)
        if self.dig_T2 > 32767:
            self.dig_T2 -= 65536
        self.dig_T3 = calib[4] | (calib[5] << 8)
        if self.dig_T3 > 32767:
            self.dig_T3 -= 65536
            
        self.dig_P1 = calib[6] | (calib[7] << 8)
        self.dig_P2 = calib[8] | (calib[9] << 8)
        if self.dig_P2 > 32767:
            self.dig_P2 -= 65536
        self.dig_P3 = calib[10] | (calib[11] << 8)
        if self.dig_P3 > 32767:
            self.dig_P3 -= 65536
        self.dig_P4 = calib[12] | (calib[13] << 8)
        if self.dig_P4 > 32767:
            self.dig_P4 -= 65536
        self.dig_P5 = calib[14] | (calib[15] << 8)
        if self.dig_P5 > 32767:
            self.dig_P5 -= 65536
        self.dig_P6 = calib[16] | (calib[17] << 8)
        if self.dig_P6 > 32767:
            self.dig_P6 -= 65536
        self.dig_P7 = calib[18] | (calib[19] << 8)
        if self.dig_P7 > 32767:
            self.dig_P7 -= 65536
        self.dig_P8 = calib[20] | (calib[21] << 8)
        if self.dig_P8 > 32767:
            self.dig_P8 -= 65536
        self.dig_P9 = calib[22] | (calib[23] << 8)
        if self.dig_P9 > 32767:
            self.dig_P9 -= 65536
        
        # Humidité
        self.dig_H1 = self.i2c.readfrom_mem(self.addr, BME280_REG_HUM_CALIB_1, 1)[0]
        
        calib = self.i2c.readfrom_mem(self.addr, BME280_REG_HUM_CALIB_2, 7)
        
        self.dig_H2 = calib[0] | (calib[1] << 8)
        if self.dig_H2 > 32767:
            self.dig_H2 -= 65536
        self.dig_H3 = calib[2]
        
        self.dig_H4 = (calib[3] << 4) | (calib[4] & 0x0F)
        if self.dig_H4 > 32767:
            self.dig_H4 -= 65536
            
        self.dig_H5 = ((calib[4] & 0xF0) >> 4) | (calib[5] << 4)
        if self.dig_H5 > 32767:
            self.dig_H5 -= 65536
            
        self.dig_H6 = calib[6]
        if self.dig_H6 > 127:
            self.dig_H6 -= 256
    
    def force_measurement(self):
        """Force une nouvelle mesure en mode forcé"""
        # Lire les paramètres actuels
        reg = self.i2c.readfrom_mem(self.addr, BME280_REG_CTRL_MEAS, 1)[0]
        
        # Conserver les paramètres d'oversampling mais forcer une mesure (bits 0-1 = 01)
        reg = (reg & 0xFC) | 0x01
        
        # Écrire dans le registre
        self.i2c.writeto_mem(self.addr, BME280_REG_CTRL_MEAS, bytes([reg]))
        
        # Attendre que la mesure soit terminée
        while self.i2c.readfrom_mem(self.addr, BME280_REG_STATUS, 1)[0] & 0x08:
            utime.sleep_ms(10)
    
    def read_raw_data(self):
        """Lecture des données brutes du capteur"""
        # Forcer une nouvelle mesure
        self.force_measurement()
        
        # Lire les données
        data = self.i2c.readfrom_mem(self.addr, BME280_REG_DATA, 8)
        
        # Pression (20 bits)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        
        # Température (20 bits)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        
        # Humidité (16 bits)
        hum_raw = (data[6] << 8) | data[7]
        
        return (pres_raw, temp_raw, hum_raw)
    
    def read_compensated_data(self):
        """Lecture et compensation des données"""
        pres_raw, temp_raw, hum_raw = self.read_raw_data()
        
        # Compensation de la température
        var1 = ((((temp_raw >> 3) - (self.dig_T1 << 1))) * self.dig_T2) >> 11
        var2 = (((((temp_raw >> 4) - self.dig_T1) * ((temp_raw >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        temp = (t_fine * 5 + 128) >> 8
        
        # Compensation de la pression
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        
        if var1 == 0:
            pres = 0  # Éviter la division par zéro
        else:
            p = 1048576 - pres_raw
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.dig_P8 * p) >> 19
            pres = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        
        # Compensation de l'humidité - version corrigée
        # Cette implémentation suit de plus près la documentation du fabricant
        humidity = 0
        
        # Étape préliminaire - s'assurer que nous avons t_fine valide
        if hum_raw != 0:
            v_x1 = t_fine - 76800
            
            v_x1 = (((((hum_raw << 14) - (self.dig_H4 << 20) - (self.dig_H5 * v_x1)) + 
                    16384) >> 15) * (((((((v_x1 * self.dig_H6) >> 10) * 
                    (((v_x1 * self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) * 
                    self.dig_H2 + 8192) >> 14))
            
            v_x1 = v_x1 - (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * self.dig_H1) >> 4)
            
            # Limiter les valeurs
            if v_x1 < 0:
                v_x1 = 0
            if v_x1 > 419430400:
                v_x1 = 419430400
            
            # Conversion finale en pourcentage (0-100%)
            humidity = v_x1 >> 12
            
            # Division par 1024 pour obtenir le pourcentage
            humidity = humidity / 1024.0
            
            # Limiter l'humidité à des valeurs raisonnables (0-100%)
            if humidity > 100.0:
                humidity = 100.0
            if humidity < 0.0:
                humidity = 0.0
        
        return pres / 256.0, temp / 100.0, humidity
    
    def read_data(self):
        """Lecture des valeurs calculées: pression (hPa), température (°C), humidité (%)"""
        pres, temp, hum = self.read_compensated_data()
        
        # Conversion Pa -> hPa
        pres = pres / 100.0
        
        # Application des facteurs de calibration
        temp = temp + self.temp_offset
        hum = hum * self.hum_factor + self.hum_offset
        pres = pres + self.pressure_offset
        
        # Vérification finale des plages de valeurs raisonnables
        if pres < 300 or pres > 1100:  # Plage typique de pression atmosphérique en hPa
            pres = 1013.25  # Valeur standard au niveau de la mer
            
        if temp < -40 or temp > 85:  # Plage de fonctionnement du BME280
            temp = 25.0  # Température ambiante typique
            
        # Limiter l'humidité à la plage 0-100%
        if hum < 0:
            hum = 0
        elif hum > 100:
            hum = 100
        
        return pres, temp, hum

# Classe pour le capteur MQ135 (qualite d'air)
class MQ135:
    """Capteur MQ135 avec calibration et lissage pour des ppm plus fiables.

    Notes importantes:
    - Le MQ135 nécessite un temps de chauffe (plusieurs minutes) pour une meilleure stabilité.
    - La précision absolue d'un MQ135 pour le CO2 est limitée; une calibration R0 en air propre (~400 ppm)
      est indispensable et améliore nettement le réalisme des valeurs.
    """

    def __init__(self, analog_pin, digital_pin=None, rl=10000, r0=None,
                 vcc=3.3, a=116.6020682, b=-2.769034857,
                 cal_file='mq135_cal.json', smooth_samples=10):
        self.adc = ADC(analog_pin)
        self.digital_pin = None if digital_pin is None else Pin(digital_pin, Pin.IN)
        self.RL = float(rl)  # Résistance de charge du module (Ω), souvent 10kΩ
        self.R0 = float(r0) if r0 is not None else None  # Résistance de référence en air propre
        self.VCC = float(vcc)
        # Constantes de la courbe (ppm = A * (Rs/R0)^B) pour CO2 (approx d'après datasheet/communauté)
        self.A = float(a)
        self.B = float(b)
        self.cal_file = cal_file
        self.smooth_samples = max(1, int(smooth_samples))
        self._ppm_history = []
        self._start_ms = utime.ticks_ms()

        # Charger une calibration existante si disponible
        try:
            self._load_calibration()
        except Exception:
            pass

    # --- Calibration & persistance ---
    def _file_exists(self, path):
        try:
            if os is None:
                return False
            os.stat(path)
            return True
        except Exception:
            return False

    def _save_calibration(self):
        if os is None:
            return
        try:
            data = {"R0": self.R0, "RL": self.RL, "A": self.A, "B": self.B}
            with open(self.cal_file, 'w') as f:
                f.write(ujson.dumps(data))
            print('MQ135: calibration sauvegardée ->', self.cal_file, 'R0=', self.R0)
        except Exception as e:
            print('MQ135: echec sauvegarde calibration:', e)

    def _load_calibration(self):
        if not self._file_exists(self.cal_file):
            return
        try:
            with open(self.cal_file, 'r') as f:
                data = ujson.loads(f.read())
                if 'R0' in data and data['R0']:
                    self.R0 = float(data['R0'])
                    print('MQ135: calibration chargée, R0 =', self.R0)
        except Exception as e:
            print('MQ135: echec chargement calibration:', e)

    def _ratio_at_ppm(self, ppm):
        # Inversion de la courbe: ratio = (ppm/A)^(1/B)
        try:
            return pow((ppm / self.A), 1.0 / self.B)
        except Exception:
            return None

    def calibrate_in_clean_air(self, samples=60, sample_delay_ms=50, temperature=None, humidity=None):
        """Calibre R0 en air propre (~400 ppm CO2).
        Prend 'samples' mesures de Rs et calcule R0 = Rs_moyen / ratio_at_400ppm
        """
        ratio_400 = self._ratio_at_ppm(400.0)
        if ratio_400 is None or ratio_400 <= 0:
            raise RuntimeError('MQ135: ratio de référence invalide pour 400 ppm')

        rs_values = []
        for _ in range(max(1, int(samples))):
            rs = self._read_rs()
            if rs is not None and rs > 0:
                # Correction simplifiée (optionnelle) température/humidité
                cf = self._correction_factor(temperature, humidity)
                rs_values.append(rs / cf)
            utime.sleep_ms(sample_delay_ms)

        if not rs_values:
            raise RuntimeError('MQ135: mesures Rs invalides pendant calibration')

        rs_avg = sum(rs_values) / len(rs_values)
        self.R0 = rs_avg / ratio_400
        print('MQ135: R0 calibré =', self.R0)
        self._save_calibration()
        return self.R0

    def ensure_calibrated(self, temperature=None, humidity=None):
        if self.R0 is None:
            print('MQ135: aucune calibration trouvée, lancement calibration rapide en air propre...')
            try:
                # Calibration courte (~3s). Pour meilleure précision, refaire plus long après chauffe > 5 min.
                self.calibrate_in_clean_air(samples=60, sample_delay_ms=50,
                                            temperature=temperature, humidity=humidity)
            except Exception as e:
                print('MQ135: calibration rapide échouée:', e)

    # --- Mesures ---
    def _read_voltage(self):
        raw = self.adc.read_u16()
        # Clamp sécurité
        if raw < 1:
            raw = 1
        if raw > 65534:
            raw = 65534
        return (raw / 65535.0) * self.VCC

    def _read_rs(self):
        vout = self._read_voltage()
        # Rs = RL * (Vcc/Vout - 1)
        try:
            rs = self.RL * ((self.VCC / vout) - 1.0)
            if rs < 0:
                rs = None
            return rs
        except Exception:
            return None

    def _correction_factor(self, temperature, humidity):
        """Facteur de correction simplifié basé sur temp/hum.
        Approche conservative: légère correction si T < 20°C.
        """
        if temperature is None or humidity is None:
            return 1.0
        # +1%/°C en dessous de 20°C (gaz moins réactif à froid)
        if temperature < 20.0:
            return 1.0 + (0.01 * (20.0 - temperature))
        return 1.0

    def get_ppm(self, temperature=None, humidity=None):
        # Assurer une calibration minimale
        if self.R0 is None:
            self.ensure_calibrated(temperature, humidity)
            if self.R0 is None:
                return 0.0

        rs = self._read_rs()
        if rs is None or rs <= 0:
            return 0.0

        cf = self._correction_factor(temperature, humidity)
        rs_corr = rs / cf

        ratio = rs_corr / self.R0
        # Eviter valeurs absurdes
        if ratio <= 0:
            ratio = 1e-6

        ppm = self.A * pow(ratio, self.B)

        # Lissage simple
        self._ppm_history.append(ppm)
        if len(self._ppm_history) > self.smooth_samples:
            self._ppm_history.pop(0)
        ppm_smoothed = sum(self._ppm_history) / len(self._ppm_history)
        return ppm_smoothed

    def is_threshold_reached(self):
        # Renvoie True si le seuil de detection est atteint (si sortie digitale disponible)
        if self.digital_pin:
            return not self.digital_pin.value()  # Generalement actif a l'etat bas
        return False

class RainSensor:
    """Capteur pluie analogique avec calibration dynamique robuste.

    Approche:
    - EMA (exponential moving average) pour lisser la valeur brute.
    - Suivi dynamique du minimum (mouillé) et du maximum (sec) observés.
    - Normalisation de l'humidité de surface entre 0% et 100% via ces bornes.
    - Persistance des bornes pour ne pas perdre la calibration à chaque reboot.
    """

    def __init__(self, analog_pin, digital_pin=None, lower_is_wetter=True,
                 ema_alpha=0.2, init_samples=100, cal_file='rain_cal.json',
                 rain_on_threshold=20.0, rain_off_threshold=10.0):
        self.adc = ADC(analog_pin)
        self.digital_pin = None if digital_pin is None else Pin(digital_pin, Pin.IN)
        self.lower_is_wetter = bool(lower_is_wetter)
        self.ema_alpha = max(0.01, min(0.9, float(ema_alpha)))
        self.rain_on_threshold = float(rain_on_threshold)
        self.rain_off_threshold = float(rain_off_threshold)
        self.cal_file = cal_file

        # Etats
        self.raw_ema = None
        self.dry_max = None
        self.wet_min = None
        self.is_raining_flag = False
        self.last_surface_humidity = 0.0

        # Charger calibration si existante
        try:
            self._load_calibration()
        except Exception:
            pass

        # Phase d'initialisation rapide
        self._quick_initialize(init_samples)

    def _file_exists(self, path):
        try:
            if os is None:
                return False
            os.stat(path)
            return True
        except Exception:
            return False

    def _save_calibration(self):
        if os is None:
            return
        try:
            data = {"dry_max": self.dry_max, "wet_min": self.wet_min, "lower_is_wetter": self.lower_is_wetter}
            with open(self.cal_file, 'w') as f:
                f.write(ujson.dumps(data))
            print('Rain: calibration sauvegardée ->', self.cal_file,
                  'dry_max=', self.dry_max, 'wet_min=', self.wet_min)
        except Exception as e:
            print('Rain: echec sauvegarde calibration:', e)

    def _load_calibration(self):
        if not self._file_exists(self.cal_file):
            return
        try:
            with open(self.cal_file, 'r') as f:
                data = ujson.loads(f.read())
                if 'dry_max' in data and 'wet_min' in data:
                    self.dry_max = float(data['dry_max'])
                    self.wet_min = float(data['wet_min'])
                    if 'lower_is_wetter' in data:
                        self.lower_is_wetter = bool(data['lower_is_wetter'])
                    print('Rain: calibration chargée (dry_max={}, wet_min={})'.format(self.dry_max, self.wet_min))
        except Exception as e:
            print('Rain: echec chargement calibration:', e)

    def _read_raw(self):
        return self.adc.read_u16()

    def _quick_initialize(self, samples):
        # Collecte rapide pour initialiser EMA et bornes si absentes
        vals = []
        for _ in range(max(10, int(samples))):
            v = self._read_raw()
            vals.append(v)
            utime.sleep_ms(5)
        avg = sum(vals) / len(vals)
        self.raw_ema = avg
        if self.dry_max is None:
            self.dry_max = avg
        if self.wet_min is None:
            # Définir un min provisoire un peu en dessous de sec
            self.wet_min = max(0.0, self.dry_max - 8000.0)
        # Enregistrer calibration initiale
        self._save_calibration()

    @property
    def calibrated(self):
        return self.dry_max is not None and self.wet_min is not None and self.dry_max > self.wet_min

    def update(self):
        # Lecture et EMA
        raw = float(self._read_raw())
        if self.raw_ema is None:
            self.raw_ema = raw
        else:
            self.raw_ema = (self.ema_alpha * raw) + ((1 - self.ema_alpha) * self.raw_ema)

        # Mise à jour dynamique des bornes
        if self.lower_is_wetter:
            # Plus mouillé = valeur plus basse
            if self.raw_ema < (self.wet_min if self.wet_min is not None else self.raw_ema):
                self.wet_min = self.raw_ema
            if self.raw_ema > (self.dry_max if self.dry_max is not None else self.raw_ema):
                # montée sèche plus lente pour ne pas sauter avec du bruit
                self.dry_max = (self.dry_max * 0.99 + self.raw_ema * 0.01) if self.dry_max is not None else self.raw_ema
        else:
            # Inversion si hardware opposé
            if self.raw_ema > (self.wet_min if self.wet_min is not None else self.raw_ema):
                self.wet_min = self.raw_ema
            if self.raw_ema < (self.dry_max if self.dry_max is not None else self.raw_ema):
                self.dry_max = (self.dry_max * 0.99 + self.raw_ema * 0.01) if self.dry_max is not None else self.raw_ema

        # Normalisation humidité 0-100
        if not self.calibrated or self.raw_ema is None or self.dry_max is None or self.wet_min is None:
            self.last_surface_humidity = 0.0
        else:
            dry_max = float(self.dry_max)
            wet_min = float(self.wet_min)
            raw_ema = float(self.raw_ema)
            span = dry_max - wet_min
            if span < 1000:
                span = 1000.0
            if self.lower_is_wetter:
                surface_humidity = (dry_max - raw_ema) / span * 100.0
            else:
                surface_humidity = (raw_ema - dry_max) / span * 100.0

            if surface_humidity < 0:
                surface_humidity = 0.0
            if surface_humidity > 100:
                surface_humidity = 100.0

            # Hystérésis pluie
            if not self.is_raining_flag and surface_humidity >= self.rain_on_threshold:
                self.is_raining_flag = True
            elif self.is_raining_flag and surface_humidity <= self.rain_off_threshold:
                self.is_raining_flag = False

            self.last_surface_humidity = surface_humidity

        # Sauvegarder périodiquement (toutes ~5s)
        if utime.ticks_ms() % 5000 < 50:
            try:
                self._save_calibration()
            except Exception:
                pass

        return self.last_surface_humidity

    def is_raining(self):
        if self.digital_pin is not None:
            digital_detect = (not self.digital_pin.value())  # actif bas
            if digital_detect:
                self.is_raining_flag = True
        return self.is_raining_flag

    def get_debug_info(self):
        return {
            'dry_max': self.dry_max,
            'wet_min': self.wet_min,
            'raw_ema': self.raw_ema,
            'last_surface_humidity': self.last_surface_humidity,
            'calibrated': self.calibrated
        }

# Classe pour le capteur UV GUVA-S12SD
class UVSensor:
    """Capteur GUVA-S12SD avec offset sombre, lissage et auto-ajustements prudents.

    - Offset sombre: calibré et adapté lentement avec le 5e percentile des tensions.
    - Auto-scale optionnel: ajuste l'échelle pour que le 95e percentile corresponde à un UVI cible réaliste.
    """

    def __init__(self, analog_pin, vcc=3.3, scale=12.0, offset=None,
                 cal_file='uv_cal.json', smooth_samples=8,
                 v_alpha=0.2, hist_len=180, auto_dark_adapt=True,
                 auto_scale=True, target_uvi_day=8.0):
        self.adc = ADC(analog_pin)
        self.VCC = float(vcc)
        self.scale = float(scale)  # UVI par volt après offset
        self.offset = float(offset) if offset is not None else None  # V sombre
        self.cal_file = cal_file
        self.smooth_samples = max(1, int(smooth_samples))
        self._uvi_hist = []
        self._v_hist = []
        self._v_filt = None
        self.v_alpha = max(0.01, min(0.9, float(v_alpha)))
        self.hist_len = max(30, int(hist_len))
        self.auto_dark_adapt = bool(auto_dark_adapt)
        self.auto_scale = bool(auto_scale)
        self.target_uvi_day = float(target_uvi_day)
        self._last_cal_save_ms = 0

        # Charger calibration existante
        try:
            self._load_calibration()
        except Exception:
            pass

    def _file_exists(self, path):
        try:
            if os is None:
                return False
            os.stat(path)
            return True
        except Exception:
            return False

    def _save_calibration(self):
        if os is None:
            return
        try:
            data = {"offset": self.offset, "scale": self.scale}
            with open(self.cal_file, 'w') as f:
                f.write(ujson.dumps(data))
            print('UV: calibration sauvegardée ->', self.cal_file, 'offset=', self.offset)
        except Exception as e:
            print('UV: echec sauvegarde calibration:', e)

    def _load_calibration(self):
        if not self._file_exists(self.cal_file):
            return
        try:
            with open(self.cal_file, 'r') as f:
                data = ujson.loads(f.read())
                if 'offset' in data and data['offset'] is not None:
                    self.offset = float(data['offset'])
                    print('UV: calibration chargée, offset =', self.offset)
        except Exception as e:
            print('UV: echec chargement calibration:', e)

    def calibrate_dark(self, samples=50, sample_delay_ms=20):
        """Mesurez à l'ombre (cachez le capteur) pour estimer l'offset sombre."""
        volts = []
        for _ in range(max(1, int(samples))):
            volts.append(self.get_voltage())
            utime.sleep_ms(sample_delay_ms)
        if volts:
            # Choisir le 20e percentile pour être robuste au bruit
            volts.sort()
            idx = max(0, int(0.2 * len(volts)) - 1)
            self.offset = volts[idx]
            self._save_calibration()
        return self.offset

    def ensure_dark_calibrated(self):
        if self.offset is None:
            print('UV: pas d\'offset sombre, calibration rapide... (couvrez le capteur)')
            try:
                self.calibrate_dark(samples=30, sample_delay_ms=20)
            except Exception as e:
                print('UV: calibration sombre échouée:', e)

    def get_raw_value(self):
        return self.adc.read_u16()

    def get_voltage(self):
        raw = self.get_raw_value()
        return (raw / 65535.0) * self.VCC

    def get_uv_index(self):
        # Assurer calibration offset minimale
        self.ensure_dark_calibrated()
        v = self.get_voltage()
        # Filtrer la tension (EMA) pour réduire le bruit instantané
        if self._v_filt is None:
            self._v_filt = v
        else:
            self._v_filt = self.v_alpha * v + (1.0 - self.v_alpha) * self._v_filt

        # Historique pour percentiles
        self._v_hist.append(self._v_filt)
        if len(self._v_hist) > self.hist_len:
            self._v_hist.pop(0)

        # Adapter lentement l'offset sombre via le 5e percentile
        if self.auto_dark_adapt and len(self._v_hist) >= int(self.hist_len * 0.5):
            try:
                vals = sorted(self._v_hist)
                p05 = vals[max(0, int(0.05 * len(vals)) - 1)]
                new_off = p05
                if self.offset is None:
                    self.offset = new_off
                    print('UV: offset sombre initialisé par p05 ->', round(self.offset, 4))
                    self._last_cal_save_ms = utime.ticks_ms()
                    self._save_calibration()
                else:
                    # adaptation lente (1%) pour éviter les dérives rapides
                    self.offset = 0.99 * self.offset + 0.01 * new_off
            except Exception:
                pass

        off = self.offset if self.offset is not None else 0.0
        uvi_raw = (self._v_filt - off) * self.scale
        if uvi_raw < 0:
            uvi_raw = 0.0

        # Auto-scale: caler le 95e percentile sur un UVI jour plausible (ex: 8)
        if self.auto_scale and len(self._v_hist) >= int(self.hist_len * 0.7):
            try:
                vals = sorted(self._v_hist)
                p95 = vals[min(len(vals) - 1, int(0.95 * len(vals)))]
                span = p95 - off
                if span > 0.05:  # évite de rescaler dans l'obscurité
                    target = self.target_uvi_day
                    new_scale = target / span
                    # ne pas changer brutalement (> +/- 10%)
                    max_up = self.scale * 1.10
                    max_dn = self.scale * 0.90
                    new_scale = max(min(new_scale, max_up), max_dn)
                    # Appliquer petit pas
                    old_scale = self.scale
                    self.scale = 0.9 * self.scale + 0.1 * new_scale
                    # Sauvegarde occasionnelle si variation notable
                    now = utime.ticks_ms()
                    if abs(self.scale - old_scale) > 0.05 and (self._last_cal_save_ms == 0 or utime.ticks_diff(now, self._last_cal_save_ms) > 60000):
                        print("UV: ajustement d'échelle ->", round(self.scale, 3))
                        self._last_cal_save_ms = now
                        self._save_calibration()
            except Exception:
                pass

        # Lissage UVI
        self._uvi_hist.append(uvi_raw)
        if len(self._uvi_hist) > self.smooth_samples:
            self._uvi_hist.pop(0)
        uvi_smoothed = sum(self._uvi_hist) / len(self._uvi_hist)
        # Plafonner à une plage réaliste (0-12)
        if uvi_smoothed > 12:
            uvi_smoothed = 12.0
        return uvi_smoothed

# --- Helpers BME280/I2C1 ---
def init_bme280_on_i2c1(sda_pin=6, scl_pin=7, freqs=(100000, 50000, 10000)):
    """Initialise le BME280 sur I2C1 (SDA=GP6, SCL=GP7) avec repli de fréquences."""
    chosen_i2c = None
    bme = None
    for f in freqs:
        try:
            i2c = I2C(1, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=f)
            print('I2C: bus=1, SDA=GP{}, SCL=GP{}, freq={}kHz'.format(sda_pin, scl_pin, int(f/1000)))
            utime.sleep_ms(200)
            devices = i2c.scan()
            print('Peripheriques I2C detectes @{}kHz:'.format(int(f/1000)), [hex(d) for d in devices])
            if (0x76 not in devices) and (0x77 not in devices):
                chosen_i2c = i2c  # garder le dernier i2c valide
                continue
            # Essayer auto-détection
            try:
                bme = BME280_Simple(i2c)
                print("BME280 initialise avec succes a l'adresse:", hex(bme.addr))
                chosen_i2c = i2c
                break
            except Exception as e:
                print('Init auto BME280 a echoue @{}kHz:'.format(int(f/1000)), e)
                # Essayer adresses connues
                for addr in (0x76, 0x77):
                    if addr in devices:
                        try:
                            bme = BME280_Simple(i2c, addr=addr)
                            print('BME280 initialise a l\'adresse forcee:', hex(addr))
                            chosen_i2c = i2c
                            break
                        except Exception as e2:
                            print('Init BME280 @{}kHz addr {} echoue:'.format(int(f/1000), hex(addr)), e2)
                if bme is not None:
                    break
                chosen_i2c = i2c
        except Exception as e:
            print('I2C1 init @{}kHz echoue:'.format(int(f/1000)), e)
            chosen_i2c = None
    if chosen_i2c is None:
        # Dernier recours: tenter une derniere fois @100kHz pour garder un bus i2c operationnel
        try:
            chosen_i2c = I2C(1, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)
            utime.sleep_ms(200)
        except Exception:
            chosen_i2c = None
    if bme is None:
        print("ATTENTION: BME280 non detecte sur I2C1 GP6/GP7 apres tentatives (100k/50k/10k).\n"
              " - Verifiez cablage et pull-ups. Adresse attendue: 0x76/0x77.")
    return chosen_i2c, bme

# Programme principal
def connect_wifi(ssid: str, password: str, country: str = 'FR', max_wait: int = 30):
    # Optionnel: definir le pays pour activer la radio sur les bons canaux
    if rp2 is not None:
        try:
            rp2.country(country)
        except Exception:
            pass
    # Certains firmwares supportent network.country()
    try:
        if hasattr(network, 'country'):
            network.country(country)
    except Exception:
        pass

    # Desactiver l'AP au cas ou (evite conflits)
    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
    except Exception:
        pass
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.active(False)
    except Exception:
        pass
    utime.sleep_ms(200)
    # Retente l'activation du chip CYW43 plusieurs fois
    activated = False
    for i in range(1, 6):
        try:
            wlan.active(True)
            # Desactiver power-save (optionnel mais parfois utile)
            try:
                wlan.config(pm=0xa11140)
            except Exception:
                pass
            activated = True
            break
        except Exception as e:
            print('Activation CYW43 tentative', i, 'echec:', e)
            utime.sleep(2)
    if not activated:
        raise RuntimeError('CYW43 non demarre: verifiez firmware Pico W et alimentation USB')

    # Helpers
    def _auth_name(a):
        try:
            names = {0: 'OPEN', 1: 'WEP', 2: 'WPA-PSK', 3: 'WPA2-PSK', 4: 'WPA/WPA2-PSK'}
            return names.get(int(a), str(a))
        except Exception:
            return str(a)

    # Scan et affichage des réseaux disponibles
    def _scan_and_print(tag='SCAN'):
        try:
            nets = wlan.scan()
            parsed = []
            for n in nets:
                try:
                    essid_b = n[0] if len(n) > 0 else b''
                    essid = essid_b.decode('utf-8', 'ignore') if isinstance(essid_b, (bytes, bytearray)) else str(essid_b)
                    chan = n[2] if len(n) > 2 else None
                    rssi = n[3] if len(n) > 3 else None
                    auth = n[4] if len(n) > 4 else None
                    hidden = bool(n[5]) if len(n) > 5 else False
                    parsed.append((essid if essid else '<hidden>', chan, rssi, _auth_name(auth), hidden))
                except Exception:
                    pass
            parsed.sort(key=lambda x: (x[2] is None, -(x[2] or -9999)))
            print('--- Réseaux WiFi disponibles ({}):'.format(tag))
            for i, (ess, ch, rs, au, hid) in enumerate(parsed[:10]):
                mark = ' <- cible' if ess == ssid else ''
                print('  {:2d}. {:20s} | ch={} | RSSI={:>4} dBm | {}{}'.format(i+1, ess, ch, rs if rs is not None else '-', au, mark))
        except Exception as e:
            print('Scan WiFi échoué:', e)

    _scan_and_print(tag='avant connexion')

    try:
        print("Connexion au réseau '{}'...".format(ssid))
        wlan.connect(ssid, password)
    except Exception as e:
        print('wlan.connect a échoué immédiatement:', e)

    # Attente jusqu'à connexion avec logs et un rescan à mi-parcours
    t0 = utime.ticks_ms()
    last_log = 0
    rescanned = False
    while not wlan.isconnected():
        elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
        if elapsed // 1000 != last_log:
            last_log = elapsed // 1000
            print("  ... tentative ({}s)".format(int(last_log)))
        if (not rescanned) and elapsed > (max_wait * 500):
            _scan_and_print(tag='pendant connexion')
            rescanned = True
        if elapsed > max_wait * 1000:
            break
        utime.sleep_ms(250)

    if not wlan.isconnected():
        raise RuntimeError('Connexion WiFi échouée: NO_AP_FOUND ou AUTH_FAIL')

    return wlan.ifconfig()

def get_json(url: str, timeout_s: int = 5):
    if requests is None:
        raise RuntimeError('urequests non disponible sur ce firmware')
    try:
        resp = requests.get(url, timeout=timeout_s)
        code = resp.status_code
        txt = resp.text
        resp.close()
        return code, txt
    except Exception as e:
        return None, str(e)


def build_health_url(api_add_url: str) -> str:
    # Essaie de convertir l'URL /add en /health
    if '/add' in api_add_url:
        return api_add_url.replace('/add', '/health')
    if api_add_url.endswith('/'):
        return api_add_url + 'health'
    return api_add_url + '/health'


def post_json(url: str, payload: dict, timeout_s: int = 5):
    if requests is None:
        raise RuntimeError('urequests non disponible sur ce firmware')
    try:
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, data=ujson.dumps(payload), headers=headers, timeout=timeout_s)
        code = resp.status_code
        txt = resp.text
        resp.close()
        return code, txt
    except Exception as e:
        return None, str(e)


def print_env_info():
    try:
        print('Firmware:', sys.implementation if sys else 'inconnu')
    except Exception:
        pass
    try:
        import os as _os
        print('FS list:', _os.listdir())
    except Exception:
        pass


def main():
    # Infos d'environnement utiles pour debug
    print_env_info()
    # Initialisation du module WiFi (CYW43) mais desactivation pour economiser l'energie
    # Parametres API (adapter SERVER_IP ou nom DNS)
    API_URL = 'http://51.91.141.222:5000/add'
    WIFI_SSID = 'Kanto MK16'
    WIFI_PASS = 'partagedeco'

    # Connexion WiFi (une seule fois, puis on garde la connexion)
    wifi_ok = False
    # Petit delai de stabilisation apres boot USB
    utime.sleep(2)
    try:
        ip = connect_wifi(WIFI_SSID, WIFI_PASS)
        print('WiFi connecte OK, ifconfig =', ip)
        wifi_ok = True
    except Exception as e:
        print('WiFi non connecte ECHEC:', e)
        # On continue mais les requetes HTTP echoueront tant que le WiFi n'est pas disponible

    # Verification de l'accessibilite de l'API au demarrage (uniquement si WiFi OK)
    if wifi_ok:
        health_url = build_health_url(API_URL)
        print('Verification API (GET):', health_url)
        code, msg = get_json(health_url, timeout_s=5)
        if code is not None and 200 <= code < 300:
            print('API joignable OK -> code:', code, 'reponse:', msg)
        else:
            print('API non joignable ECHEC ->', code, msg)
    
    # Initialisation I2C1 + BME280 avec repli de fréquences (100k/50k/10k)
    i2c, bme280 = init_bme280_on_i2c1(sda_pin=6, scl_pin=7, freqs=(100000, 50000, 10000))
    
    # Initialisation du capteur MQ135 (qualite d'air)
    # Rappel: le MQ135 nécessite un temps de chauffe. Une calibration R0 en air propre (~400 ppm)
    # est effectuée automatiquement si aucune valeur n'est sauvegardée.
    mq135 = MQ135(analog_pin=26, digital_pin=14)
    
    # Initialisation du capteur de pluie
    rain_sensor = RainSensor(analog_pin=28, digital_pin=15)
    
    # Initialisation du capteur UV GUVA-S12SD
    uv_sensor = UVSensor(analog_pin=27)
    
    print("Station meteo demarree...")

    # Lecture initiale optionnelle BME pour calibrer MQ135 en air propre si nécessaire
    try:
        init_temp = None
        init_hum = None
        if bme280 is not None:
            _, init_temp, init_hum = bme280.read_data()
        mq135.ensure_calibrated(temperature=init_temp, humidity=init_hum)
    except Exception as e:
        print('MQ135: calibration initiale ignoree:', e)

    # Période d'envoi des données réduite pour un quasi temps réel
    SEND_PERIOD_MS = 30 * 1000  # 30 secondes
    # Forcer un premier envoi immediat en antidatant le dernier envoi
    last_send_ms = utime.ticks_ms() - SEND_PERIOD_MS
    
    warned_no_bme = False
    while True:
        try:
            # Lecture des données BME280 (ou valeurs fictives si indisponible)
            temperature = None
            pressure = None
            humidity = None
            if bme280:
                pressure, temperature, humidity = bme280.read_data()
                print(f"Temperature: {temperature:.1f}°C, Pression: {pressure:.1f}hPa, Humidite: {humidity:.1f}%")
            else:
                # Valeurs fictives plausibles pour debug si BME280 absent
                temperature = 22.0
                pressure = 1013.25
                humidity = 50.0
                print("BME280 non disponible - valeurs fictives: "
                      f"Temperature: {temperature:.1f}°C, Pression: {pressure:.1f}hPa, Humidite: {humidity:.1f}%")
            
            # Lecture de la qualite d'air (MQ135) avec correction T/H si disponibles
            co2_ppm = mq135.get_ppm(temperature=temperature, humidity=humidity)
            air_quality_alert = "OUI" if mq135.is_threshold_reached() else "NON"
            print(f"CO2 (approx): {co2_ppm:.1f}ppm, Alerte qualite air: {air_quality_alert}")
            
            # Lecture du capteur de pluie avec calibration & humidite de surface
            surface_hum = rain_sensor.update()
            is_raining = rain_sensor.is_raining()
            dbg = rain_sensor.get_debug_info()
            if not rain_sensor.calibrated:
                print(f"Pluie: calibration dynamique en cours - humidite surface: {surface_hum:.1f}%")
            else:
                print(f"Pluie: humidite surface: {surface_hum:.1f}%, pluie: {'OUI' if is_raining else 'NON'} (dry_max={int(dbg['dry_max'])} wet_min={int(dbg['wet_min'])})")
            
            # Lecture du capteur UV
            uv_raw = uv_sensor.get_raw_value()
            uv_voltage = uv_sensor.get_voltage()
            uv_index = uv_sensor.get_uv_index()
            print(f"UV: Raw={uv_raw}, Tension={uv_voltage:.2f}V, Indice UV={uv_index:.1f}")
            
            # Envoi periodique vers l'API toutes les 10 minutes
            now_ms = utime.ticks_ms()
            diff_ms = utime.ticks_diff(now_ms, last_send_ms)
            # Afficher un compte a rebours d'envoi
            remaining_seconds = max(0, (SEND_PERIOD_MS - diff_ms) / 1000.0)
            if remaining_seconds > 0:
                print('Prochain envoi dans ~{}s'.format(int(remaining_seconds)))

            if bme280 is None and not warned_no_bme:
                print("BME280 indisponible: envoi active avec valeurs fictives pour temperature/humidite/pression.")
                warned_no_bme = True

            if diff_ms >= SEND_PERIOD_MS:
                # Reassurer la connexion WiFi avant l'envoi
                try:
                    wlan = network.WLAN(network.STA_IF)
                    if not wlan.isconnected():
                        print('WiFi perdu, reconnexion...')
                        connect_wifi(WIFI_SSID, WIFI_PASS)
                        print('WiFi reconnecte OK, ifconfig =', wlan.ifconfig())
                except Exception as e:
                    print('Echec reconnexion WiFi:', e)

                # Construire le payload en toutes circonstances (avec mesures ou valeurs fictives)
                payload = {
                    'temperature': float(temperature),
                    'humidite': float(humidity),
                    'pression': float(pressure),
                    'co2': float(co2_ppm),
                    'humidite_surface': float(surface_hum),
                    'pluie_detectee': bool(is_raining),
                    'indice_uv': float(uv_index),
                }
                print('Envoi vers API (POST) toutes les 30 secondes:', API_URL)
                code, msg = post_json(API_URL, payload)
                if code is not None and 200 <= code < 300:
                    print('POST reussi OK ->', code)
                    last_send_ms = now_ms
                else:
                    print('POST echoue ->', code, msg)

            # Ligne de separation pour la lisibilite
            print("-" * 50)
            
            # Attente de 2 secondes
            utime.sleep(2)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Erreur:", e)
            utime.sleep(2)
    
    print("Station meteo arretee.")

if __name__ == "__main__":
    main()