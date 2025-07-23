from machine import Pin, I2C
from pico_i2c_lcd import I2cLcd
import time

# Reduced frequency and added debug prints
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=25000)  # Even lower frequency

def scan_i2c():
    print("Scanning I2C bus...")
    devices = i2c.scan()
    if devices:
        for device in devices:
            print(f"Found device at: 0x{device:x}")
            print(f"Testing basic I2C communication...")
            try:
                # Try to write a simple command
                i2c.writeto(device, b'\x00')
                print("Basic I2C write successful")
            except Exception as e:
                print(f"Basic I2C write failed: {e}")
        return devices[0]
    return None

try:
    print("Starting I2C initialization...")
    time.sleep(2)  # Longer initial wait
    
    addr = scan_i2c()
    if addr:
        print(f"Attempting LCD initialization at address 0x{addr:x}")
        time.sleep(1)
        
        # Initialize with extra delay between operations
        lcd = I2cLcd(i2c, addr, 2, 16)
        time.sleep(1)
        
        print("LCD initialized, attempting to clear display...")
        lcd.clear()
        time.sleep(0.5)
        
        print("Writing test message...")
        lcd.putstr("Test LCD")
        print("Message sent!")
    else:
        print("No I2C devices found!")
    
except Exception as e:
    print(f"Error details: {str(e)}")