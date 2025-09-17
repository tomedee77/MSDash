import serial
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
ser.write(b'\x01\x00\x00\x00')
reply = ser.read(256)
print(' '.join(f'{b:02X}' for b in reply))
ser.close()
