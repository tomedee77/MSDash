import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 17
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pages = ["RPM","Coolant","MAT","AFR","TPS","GPS"]
page_index = 0
last_button_state = GPIO.input(BUTTON_PIN)
last_press_time = 0

while True:
    button_state = GPIO.input(BUTTON_PIN)
    if button_state == GPIO.LOW and last_button_state == GPIO.HIGH:
        if (time.time() - last_press_time) > 0.3:
            page_index = (page_index + 1) % len(pages)
            print("Page:", pages[page_index])
            last_press_time = time.time()
    last_button_state = button_state
    time.sleep(0.01)
