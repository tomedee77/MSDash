import time
import smbus2
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont

# --- Detect OLED I2C address ---
def detect_i2c_address():
    bus = smbus2.SMBus(1)
    for addr in range(0x03, 0x77):
        try:
            bus.write_quick(addr)
            return addr
        except:
            pass
    raise RuntimeError("No OLED found on I2C bus")

i2c_addr = detect_i2c_address()
print(f"OLED detected at 0x{i2c_addr:02X}")

# --- OLED setup ---
serial = i2c(port=1, address=i2c_addr)
device = sh1106(serial)

# Use built-in font
font = ImageFont.load_default()

# Example data (later replaced with MS + GPS)
pages = [
    ("Coolant", "85.0 °C"),
    ("MAT", "32.5 °C"),
    ("AFR", "14.7"),
    ("Boost", "1.2 Bar"),
    ("Speed", "56.3 MPH"),
]

page_index = 0

while True:
    label, value = pages[page_index]

    device.clear()
    with device.canvas() as draw:
        draw.text((0, 0), f"{label}:", font=font, fill=255)
        draw.text((0, 16), value, font=font, fill=255)

    page_index = (page_index + 1) % len(pages)
    time.sleep(2)

