import time
import threading
import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

# --- OLED setup ---
serial_i2c = i2c(port=1, address=0x3C)
oled = ssd1306(serial_i2c)

# Use a bigger truetype font (adjust size if needed)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)

def display_text(text):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(text, font=font)
    draw.text(((oled.width - w) // 2, (oled.height - h) // 2),
              text, font=font, fill=255)
    oled.display(image)

# --- Button setup ---
BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Globals ---
current_screen = 0
ms_data = {"clt": 90, "iat": 32, "afr": 14.7, "boost": 10}
gps_speed_kmh = 50.0  # fake test value

# --- Button handler ---
def button_callback(channel):
    global current_screen
    current_screen = (current_screen + 1) % 5  # cycle 0–4

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

# --- Fake data updater (for testing without MS or GPS) ---
def fake_data():
    global ms_data, gps_speed_kmh
    while True:
        ms_data["clt"] += 1
        if ms_data["clt"] > 110:
            ms_data["clt"] = 90
        gps_speed_kmh += 2
        if gps_speed_kmh > 120:
            gps_speed_kmh = 50
        time.sleep(1)

threading.Thread(target=fake_data, daemon=True).start()

# --- Main loop ---
while True:
    if current_screen == 0:
        display_text(f"CLT {ms_data['clt']}C")
    elif current_screen == 1:
        display_text(f"IAT {ms_data['iat']}C")
    elif current_screen == 2:
        display_text(f"AFR {ms_data['afr']:.1f}")
    elif current_screen == 3:
        display_text(f"BOOST {ms_data['boost']}psi")
    elif current_screen == 4:
        mph = gps_speed_kmh * 0.621371
        display_text(f"SPEED {mph:.1f}")
    time.sleep(0.2)
