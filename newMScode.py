import time
import serial
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import board
import busio

# --- Setup OLED ---
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
oled.show()

# --- Setup Button ---
BUTTON_PIN = 17  # GPIO pin for momentary switch
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Setup Serial ---
try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
    ms_connected = True
    print("MegaSquirt detected, live data mode enabled.")
except serial.SerialException:
    print("MegaSquirt not detected. Running in dummy mode.")
    ms_connected = False

# --- Font ---
font = ImageFont.load_default()

# --- Pages ---
pages = ['RPM', 'Coolant', 'MAT', 'AFR', 'TPS']
page_index = 0

# --- Debounce ---
last_button_state = GPIO.input(BUTTON_PIN)
last_press_time = 0

# --- Functions ---
def request_realtime():
    if not ms_connected:
        return None
    # MS2/Extra real-time request (adjust bytes for your firmware)
    ser.write(b'\x01')
    frame = ser.read(32)  # adjust frame length
    return frame

def parse_data(frame):
    if not ms_connected or frame is None or len(frame) < 5:
        return None
    rpm = frame[0] + (frame[1]<<8)
    coolant = frame[2]
    mat = frame[3]
    afr = frame[4] / 10  # adjust scaling for your firmware
    tps = frame[5] if len(frame) > 5 else 0
    return {'RPM': rpm, 'Coolant': coolant, 'MAT': mat, 'AFR': afr, 'TPS': tps}

def get_dummy_data():
    # Dummy values for testing/display
    return {'RPM': 1500, 'Coolant': 75, 'MAT': 30, 'AFR': 14.7, 'TPS': 5}

# --- Main Loop ---
try:
    while True:
        # --- Read button ---
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == 0 and last_button_state == 1 and (time.time() - last_press_time) > 0.3:
            page_index = (page_index + 1) % len(pages)
            last_press_time = time.time()
        last_button_state = button_state

        # --- Read ECU or dummy ---
        frame = request_realtime()
        data = parse_data(frame)
        if not data:
            data = get_dummy_data()

        # --- Draw page ---
        image = Image.new('1', (128, 32))
        draw = ImageDraw.Draw(image)
        page = pages[page_index]

        if page == 'RPM':
            draw.text((0, 0), f"RPM: {data['RPM']}", font=font, fill=255)
        elif page == 'Coolant':
            draw.text((0, 0), f"Coolant: {data['Coolant']}C", font=font, fill=255)
        elif page == 'MAT':
            draw.text((0, 0), f"MAT: {data['MAT']}C", font=font, fill=255)
        elif page == 'AFR':
            draw.text((0, 0), f"AFR: {data['AFR']:.1f}", font=font, fill=255)
        elif page == 'TPS':
            draw.text((0, 0), f"TPS: {data['TPS']}%", font=font, fill=255)

        oled.image(image)
        oled.show()
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    oled.fill(0)
    oled.show()
