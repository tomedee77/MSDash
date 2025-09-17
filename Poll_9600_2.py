# ms2_rpi_live_table.py
import serial
import struct
import time
import os

# --- CONFIGURATION ---
PORT = "/dev/ttyUSB0"  # Change if needed
BAUD = 9600
RT_REQUEST = b'\x01\x00\x00\x00'

# --- HELPER FUNCTIONS ---
def bytes_to_words_le(b):
    """Convert bytes to list of 16-bit little-endian words."""
    n = (len(b)//2)*2
    return [struct.unpack_from('<H', b, i)[0] for i in range(0, n, 2)]

def safe_field(value, min_val=0, max_val=65535):
    if not isinstance(value, int) or value < min_val or value > max_val:
        return "N/A"
    return value

def scale(value, divisor):
    return value/divisor if isinstance(value, int) else value

def decode_rt(words):
    """
    Decode MS2/Extra RT block safely.
    CLT, IAT, TPS, AFR always readable.
    RPM and MAP may be N/A if engine not running.
    """
    out = {}
    keys = ['RPM', 'TPS_%', 'MAP_kPa', 'CLT_C', 'IAT_C', 'AFR']
    if len(words) < 6:
        for k in keys:
            out[k] = "N/A"
        return out

    rpm     = safe_field(words[0], 0, 16000)
    tps     = scale(safe_field(words[1], 0, 1000), 10.0)
    map_kpa = scale(safe_field(words[2], 0, 2550), 10.0)
    clt     = scale(safe_field(words[3], 0, 2500), 10.0)
    iat     = scale(safe_field(words[4], 0, 2500), 10.0)
    afr     = scale(safe_field(words[5], 0, 2000), 100.0)

    # Only RPM and MAP depend on engine running
    if rpm == 0 or rpm == "N/A":
        rpm = 0
        map_kpa = "N/A"

    out['RPM']     = rpm
    out['TPS_%']   = tps
    out['MAP_kPa'] = map_kpa
    out['CLT_C']   = clt
    out['IAT_C']   = iat
    out['AFR']     = afr
    return out

# --- MAIN POLLING LOOP ---
def live_poll():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to ECU on {PORT} at {BAUD} baud\n")
    except Exception as e:
        print("Failed to open serial port:", e)
        return

    print("Press Ctrl+C to stop polling.\n")

    # Print header
    header = f"{'RPM':>6} {'TPS_%':>6} {'MAP_kPa':>8} {'CLT_C':>6} {'IAT_C':>6} {'AFR':>6}"
    print(header)
    print("-" * len(header))

    try:
        while True:
            ser.write(RT_REQUEST)
            time.sleep(0.05)
            reply = ser.read(256)
            if reply:
                words = bytes_to_words_le(reply)
                decoded = decode_rt(words)
                # Print in table format
                print(f"{decoded['RPM']:>6} {decoded['TPS_%']:>6} {decoded['MAP_kPa']:>8} "
                      f"{decoded['CLT_C']:>6} {decoded['IAT_C']:>6} {decoded['AFR']:>6}")
            else:
                print("No response")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nPolling stopped")
        ser.close()

if __name__ == "__main__":
    live_poll()
