import serial
import time

# --- Configure your serial port ---
SERIAL_PORT = '/dev/ttyUSB0'  # change if needed
BAUD_RATE = 115200
TIMEOUT = 0.5  # seconds

# Common RT request bytes for MS2/Extra
requests = [b'\x01', b'\x01\x00', b'\x02']

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.\n")
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    exit(1)

for req in requests:
    print(f"Sending request: {req}")
    ser.reset_input_buffer()
    ser.write(req)
    time.sleep(0.1)  # wait briefly for a response
    response = ser.read(32)  # read up to 32 bytes
    if response:
        print(f"Received {len(response)} bytes: {response}\n")
    else:
        print("No response.\n")

ser.close()
