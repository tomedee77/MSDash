import serial
import struct
import time

# --- CONFIGURE SERIAL PORT ---
PORT = "/dev/ttyUSB0"  # change if needed
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
    Decode MS2/Extra RT block safely. Returns N/A if data unavailable.
    """
    out = {}
    if len(words) < 6:
        # Packet too short, fill with N/A
        keys = ['RPM', 'TPS_%', 'MAP_kPa', 'CLT_C', 'IAT_C', 'AFR']
        for k in keys:
            out[k] = "N/A"
        return out

    rpm     = safe_field(words[0], 0, 16000)
    tps     = scale(safe_field(words[1], 0, 1000), 10.0)
    map_kpa = scale(safe_field(words[2], 0, 2550), 10.0)
    clt     = scale(safe_field(words[3], 0, 2500), 10.0)
    iat     = scale(safe_field(words[4], 0, 2500), 10.0)
    afr     = scale(safe_field(words[5], 0, 2000), 100.0)

    # Engine off detection
    if rpm == 0 or rpm == "N/A":
        tps = map_kpa = clt = iat = afr = "N/A"

    out['RPM']     = rpm
    out['TPS_%']   = tps
    out['MAP_kPa'] = map_kpa
    out['CLT_C']   = clt
    out['IAT_C']   = iat
    out['AFR']     = afr
    return out

# --- LIVE POLLING ---
def live_poll():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to ECU on {PORT} at {BAUD} baud")
    except Exception as e:
        print("Failed to open serial port:", e)
        return

    print("Press Ctrl+C to stop polling.\n")
    try:
        while True:
            ser.write(RT_REQUEST)
            time.sleep(0.05)
            reply = ser.read(256)
            if reply:
                # Show raw bytes in hex
                print("Raw bytes:", ' '.join(f'{b:02X}' for b in reply))
                # Decode words
                words = bytes_to_words_le(reply)
                decoded = decode_rt(words)
                print(f"Decoded: RPM={decoded['RPM']} TPS={decoded['TPS_%']} MAP={decoded['MAP_kPa']} "
                      f"CLT={decoded['CLT_C']} IAT={decoded['IAT_C']} AFR={decoded['AFR']}\n")
            else:
                print("No response")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nPolling stopped")
        ser.close()

if __name__ == "__main__":
    live_poll()
