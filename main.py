from machine import Pin, I2C
from utime import sleep
import bme280
from pico_i2c_lcd import I2cLcd
from websocket import WebSocket # type: ignore

# Initialisation des LEDs
pins = [Pin(6, Pin.OUT), Pin(7, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT), Pin(10, Pin.OUT)]

try:
    # Initialisation du WebSocket
    ws = WebSocket()
    ws.start()

    print("Initialisation du BME280...")
    # I2C0 pour BME280 - Utilisation des broches I2C0 dédiées
    i2c_bme = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)
    bme = bme280.BME280(i2c=i2c_bme)
    print("BME280 initialisé avec succès")

    print("Initialisation du LCD...")
    # I2C1 pour LCD - Utilisation des broches I2C1 dédiées
    i2c_lcd = I2C(1, scl=Pin(19), sda=Pin(18), freq=25000)
    addrs = i2c_lcd.scan()
    if not addrs:
        print("LCD non détecté !")
        raise Exception("LCD non trouvé")
    
    addr = addrs[0]
    print(f"LCD trouvé à l'adresse: 0x{addr:x}")
    
    lcd = I2cLcd(i2c_lcd, addr, 2, 16)
    sleep(1)  # Attente après initialisation
    
    lcd.clear()
    lcd.putstr("Demarrage...")
    sleep(2)

    print("Début de la boucle principale")
    while True:
        try:

            # Lecture BME280
            temp = float(bme.temperature[:-1])
            hum = float(bme.humidity[:-1])
            pres = float(bme.pressure[:-3])

            # Envoi des données via WebSocket
            ws.handle_connections()  # Gère les nouvelles connexions
            ws.broadcast({
                'temperature': temp,
                'humidity': hum,
                'pressure': pres
            })

            # Mise à jour LCD
            lcd.clear()
            lcd.putstr("T:{:.1f}C H:{:.0f}%".format(temp, hum))
            lcd.move_to(0, 1)
            lcd.putstr("P:{:.0f}hPa".format(pres))

            # Mise à jour LEDs
            pins[0].value(1 if temp > 28 else 0)
            pins[1].value(1 if temp > 30 else 0)
            pins[2].value(1 if temp > 35 else 0)
            pins[3].value(1 if temp > 40 else 0)
            pins[4].value(1 if temp > 45 else 0)

            sleep(1)

        except Exception as e:
            print(f"Erreur dans la boucle: {e}")
            lcd.clear()
            lcd.putstr("Erreur lecture")
            sleep(2)

except Exception as e:
    print(f"Erreur d'initialisation: {e}")
    # Éteindre toutes les LEDs en cas d'erreur
    for pin in pins:
        pin.off()

finally:
    # Nettoyage
    print("Arrêt du programme")
    for pin in pins:
        pin.off()