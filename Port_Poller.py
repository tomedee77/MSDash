# ms2_rpi_live.py
import serial
import struct
import time

# --- CONFIGURE SERIAL PORT ---
PORT = "/dev/ttyUSB0"  # Change if your ECU is on another ttyUSB*
BAUD = 115200
RT_REQUEST = b'\x01\x00\x00\x00'  # MS2/Extra realtime request

# --- HELPER FUNCTIONS ---
def bytes_to_words_le(b):
    """Convert bytes to list of 16-bit little-endian words."""
    n = (len(b)//2)*2
    return [struct.unpack_from('<H', b, i)[0] for i in range(0, n, 2)]

def safe_field(value, min_val=0, max_val=65535):
    """Return value if in range, else 'N/A'"""
    if not isinstance(value, int) or value < min_val or value > max_val:
        return "N/A"
    return value

def scale(value, divisor):
    return value/divisor if isinstance(value, int) else value

def decode_rt(words):
    """
    Decode MS2/Extra 3.2.5 RT block.
    Marks fields as N/A if engine off or out-of-range.
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

    # If engine off (RPM==0), mark other fields as N/A
    if rpm == 0 or rpm == "N/A":
        tps = map_kpa = clt = iat = afr = "N/A"

    out['RPM']     = rpm
    out['TPS_%']   = tps
    out['MAP_kPa'] = map_kpa
    out['CLT_C']   = clt
    out['IAT_C']   = iat
    out['AFR']     = afr
    return out

# --- MAIN LIVE POLLING LOOP ---
def live_poll():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"Connected to ECU on {PORT} at {BAUD} baud.\n")
    except Exception as e:
        print("Failed to open serial port:", e)
        return

    print("Press Ctrl+C to stop polling.\n")
    try:
        while True:
            # Send RT request
            ser.write(RT_REQUEST)
            time.sleep(0.05)
            reply = ser.read(256)  # read up to 256 bytes
            if reply:
                words = bytes_to_words_le(reply)
                decoded = decode_rt(words)
                # Print human-readable values
                print(f"RPM: {decoded['RPM']}\tTPS: {decoded['TPS_%']}\tMAP: {decoded['MAP_kPa']}"
                      f"\tCLT: {decoded['CLT_C']}\tIAT: {decoded['IAT_C']}\tAFR: {decoded['AFR']}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nPolling stopped.")
        ser.close()

if __name__ == "__main__":
    live_poll()
