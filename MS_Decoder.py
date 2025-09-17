# ms2_live_decoder.py
import struct
import textwrap
import serial
import time

# --- CONFIGURE YOUR SERIAL PORT ---
PORT = "COM3"       # change to your actual COM port
BAUD = 115200       # typical for MS2/Extra
RT_REQUEST = b'\x01\x00\x00\x00'  # realtime poll

# --- HELPER FUNCTIONS ---
def hex_to_bytes(s):
    s = s.strip().replace('\n',' ').replace('\r',' ').replace(',', ' ')
    s = s.replace('0x','')
    parts = [p for p in s.split() if p]
    return bytes(int(p,16) for p in parts)

def bytes_to_words_le(b):
    n = (len(b)//2)*2
    return [struct.unpack_from('<H', b, i)[0] for i in range(0, n, 2)]

def pretty_print_hex(b, width=16):
    hexstr = b.hex()
    pairs = textwrap.wrap(hexstr, 2)
    for i in range(0, len(pairs), width):
        print(' '.join(pairs[i:i+width]))

def safe_field(value, min_val=0, max_val=65535):
    """Return value if numeric and in range, else 'N/A'"""
    if not isinstance(value, int) or value < min_val or value > max_val:
        return "N/A"
    return value

def scale(value, divisor):
    return value/divisor if isinstance(value, int) else value

def try_map_common(words):
    """
    MS2/Extra 3.2.5 RT block mapping with engine-off detection.
    """
    out = {}
    if len(words) < 6:
        return out

    rpm     = safe_field(words[0], 0, 16000)
    tps     = scale(safe_field(words[1], 0, 1000), 10.0)
    map_kpa = scale(safe_field(words[2], 0, 2550), 10.0)
    clt     = scale(safe_field(words[3], 0, 2500), 10.0)
    iat     = scale(safe_field(words[4], 0, 2500), 10.0)
    afr     = scale(safe_field(words[5], 0, 2000), 100.0)

    # Mark likely inactive fields if RPM == 0
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
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"Connected to ECU on {PORT} at {BAUD} baud.\n")
    except Exception as e:
        print("Failed to open serial port:", e)
        return

    print("Press Ctrl+C to stop.\nPolling ECU for realtime data...\n")
    try:
        while True:
            ser.write(RT_REQUEST)
            time.sleep(0.05)  # 50ms delay between polls
            reply = ser.read(256)  # read up to 256 bytes
            if reply:
                words = bytes_to_words_le(reply)
                mapped = try_map_common(words)
                # Print live values
                print(f"RPM: {mapped['RPM']}\tTPS: {mapped['TPS_%']}\tMAP: {mapped['MAP_kPa']}"
                      f"\tCLT: {mapped['CLT_C']}\tIAT: {mapped['IAT_C']}\tAFR: {mapped['AFR']}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nPolling stopped.")
        ser.close()

# --- MANUAL DECODE FROM HEX (optional) ---
def manual_decode():
    print("Paste bulk-IN packet hex (or empty to skip):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    if not lines:
        return
    hex_in = ' '.join(lines)
    try:
        b = hex_to_bytes(hex_in)
    except Exception as e:
        print("Error parsing hex:", e)
        return
    print("\n--- RAW BYTES (hex) ---")
    pretty_print_hex(b, width=16)
    words = bytes_to_words_le(b)
    print("\n--- 16-bit little-endian words ---")
    for i,w in enumerate(words):
        print(f"W{i:03d}: {w} (0x{w:04X})")
    print("\n--- Decoded MS2/Extra fields ---")
    mapped = try_map_common(words)
    for k,v in mapped.items():
        print(f"{k}: {v}")

# --- MAIN ---
if __name__ == "__main__":
    manual_decode()  # optional
    live_poll()

