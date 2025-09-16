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

# Fonts (adjust sizes if too big/small for your OLED)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)

# Example data (later replaced with MS + GPS)
pages = [
    ("Coolant °C", "85.0"),
    ("MAT °C", "32.5"),
    ("AFR", "14.7"),
    ("Boost Bar", "1.2"),
    ("Speed MPH", "56.3"),
]

page_index = 0

while True:
    label, value = pages[page_index]

    with canvas(device) as draw:
        # Center label
        w_label, h_label = draw.textbbox((0, 0), label, font=font_small)[2:]
        x_label = (device.width - w_label) // 2
        draw.text((x_label, 0), label, font=font_small, fill=255)

        # Center value
        w_value, h_value = draw.textbbox((0, 0), value, font=font_large)[2:]
        x_value = (device.width - w_value) // 2
        draw.text((x_value, 16), value, font=font_large, fill=255)

    page_index = (page_index + 1) % len(pages)
    time.sleep(2)


