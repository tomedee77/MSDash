import time
import serial
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import board
import busio
import os

# --- GPS support ---
try:
    import gps
    gps_session = gps.gps(mode=gps.WATCH_ENABLE)
    gps_connected = True
    print("GPS detected, live speed enabled.")
except ImportError:
    print("GPS module not installed, using dummy GPS speed.")
    gps_connected = False

# --- Setup OLED ---
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
oled.show()

# --- Setup Button ---
BUTTON_PIN = 17  # BCM pin 17 (physical pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Button callback ---
def button_pressed(channel):
    global page_index
    page_index = (page_index + 1) % len(pages)

# --- Remove any previous events and add callback safely ---
try:
    GPIO.remove_event_detect(BUTTON_PIN)
except RuntimeError:
    pass  # no previous event
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=500)

# --- Setup Serial (MegaSquirt) ---
try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
    ms_connected = True
    print("MegaSquirt detected, live data mode enabled.")
except serial.SerialException:
    print("MegaSquirt not detected. Running in dummy mode.")
    ms_connected = False

# --- Fonts ---
font_label = ImageFont.load_default()
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(font_path):
    font_value = ImageFont.truetype(font_path, 16)
else:
    font_value = ImageFont.load_default()

# --- Pages ---
pages = ['RPM', 'Coolant', 'MAT', 'AFR', 'TPS', 'GPS']
page_index = 0

# --- Functions ---
def request_realtime():
    if not ms_connected:
        return None
    ser.write(b'\x01')  # adjust for your MS2/Extra firmware
    frame = ser.read(32)
    return frame

def parse_data(frame):
    if not ms_connected or frame is None or len(frame) < 5:
        return None
    rpm = frame[0] + (frame[1]<<8)
    coolant = frame[2]
    mat = frame[3]
    afr = frame[4] / 10
    tps = frame[5] if len(frame) > 5 else 0
    return {'RPM': rpm, 'Coolant': coolant, 'MAT': mat, 'AFR': afr, 'TPS': tps}

def get_dummy_data():
    return {'RPM': 1500, 'Coolant': 75, 'MAT': 30, 'AFR': 14.7, 'TPS': 5}

def get_gps_speed():
    if not gps_connected:
        return 0.0
    try:
        report = gps_session.next()
        if report['class'] == 'TPV':
            speed_m_s = getattr(report, 'speed', 0.0)  # m/s
            return speed_m_s * 2.23694  # convert to MPH
    except StopIteration:
        return 0.0
    except KeyError:
        return 0.0
    return 0.0

def draw_centered(draw, label, value):
    bbox_label = draw.textbbox((0, 0), label, font=font_label)
    w_label = bbox_label[2] - bbox_label[0]
    h_label = bbox_label[3] - bbox_label[1]

    bbox_value = draw.textbbox((0, 0), value, font=font_value)
    w_value = bbox_value[2] - bbox_value[0]
    h_value = bbox_value[3] - bbox_value[1]

    x_label = (128 - w_label) // 2
    x_value = (128 - w_value) // 2

    y_label = 0
    y_value = h_label

    draw.text((x_label, y_label), label, font=font_label, fill=255)
    draw.text((x_value, y_value), value, font=font_value, fill=255)

# --- Main Loop ---
try:
    while True:
        # Read ECU or dummy
        frame = request_realtime()
        data = parse_data(frame)
        if not data:
            data = get_dummy_data()

        # Read GPS speed
        gps_speed = get_gps_speed()

        # Determine page content
        page = pages[page_index]
        if page == 'RPM':
            label = "RPM"
            value = f"{data['RPM']}"
        elif page == 'Coolant':
            label = "Coolant"
            value = f"{data['Coolant']}C"
        elif page == 'MAT':
            label = "MAT"
            value = f"{data['MAT']}C"
        elif page == 'AFR':
            label = "AFR"
            value = f"{data['AFR']:.1f}"
        elif page == 'TPS':
            label = "TPS"
            value = f"{data['TPS']}%"
        elif page == 'GPS':
            label = "GPS Speed"
            value = f"{gps_speed:.1f} MPH"

        # Draw to OLED
        image = Image.new('1', (128, 32))
        draw = ImageDraw.Draw(image)
        draw_centered(draw, label, value)
        oled.image(image)
        oled.show()
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    oled.fill(0)
    oled.show()
