import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(17) == 0:
            print("Button pressed")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
