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
BUTTON_PIN = 17
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

# --- Fonts ---
font_label = ImageFont.load_default()  # small font for label
font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)  # larger font for value

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
    ser.write(b'\x01')  # adjust for your firmware
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

def draw_centered(draw, label, value):
    # Measure label size
    w_label, h_label = draw.textsize(label, font=font_label)
    # Measure value size
    w_value, h_value = draw.textsize(value, font=font_value)
    
    # X positions for centering
    x_label = (128 - w_label) // 2
    x_value = (128 - w_value) // 2
    
    # Y positions
    y_label = 0
    y_value = h_label  # start value below label
    
    draw.text((x_label, y_label), label, font=font_label, fill=255)
    draw.text((x_value, y_value), value, font=font_value, fill=255)

# --- Main Loop ---
try:
    while True:
        # --- Button handling ---
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

        # --- Prepare page text ---
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

        # --- Draw ---
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
