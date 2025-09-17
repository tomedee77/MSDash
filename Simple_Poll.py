import serial
import time

PORT = "/dev/ttyUSB0"  # adjust if needed
BAUD = 9600             # or 115200 depending on the port

ser = serial.Serial(PORT, BAUD, timeout=1)
ser.write(b'\x01\x00\x00\x00')  # RT request
time.sleep(0.1)
reply = ser.read(256)
print("Raw reply:", reply.hex())
ser.close()
