#!/usr/bin/env python3
import os
import glob
import time

# ----------------------------
# CONFIG
# ----------------------------
LOG_DIR = "/home/tomedee77/TunerStudioProjects/VWRX/DataLogs"
LOG_EXTENSIONS = ["*.mlg", "*.msl"]
POLL_INTERVAL = 0.2  # seconds between checks

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def find_latest_log(log_dir, extensions):
    """Return the path of the most recent log file"""
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(log_dir, ext)))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def is_numeric(s):
    """Check if string can be interpreted as a number"""
    try:
        float(s)
        return True
    except ValueError:
        return False

def tail_log(file_path):
    """Continuously read new lines from the log file"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            # Skip first 4 lines (metadata + labels)
            for _ in range(4):
                next(f, None)

            # Capture headers from line 3
            f.seek(0)
            lines = f.readlines()
            header = lines[2].strip().split("\t")

            # Move to the end for tailing new lines
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(POLL_INTERVAL)
                    continue

                line = line.strip()
                if not line:
                    continue

                cols = line.split("\t")
                # Only process numeric lines
                if all(is_numeric(c) or c == '' for c in cols):
                    print("\nLatest data:")
                    for h, v in zip(header, cols):
                        print(f"{h}\n{v}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

# ----------------------------
# MAIN
# ----------------------------
latest_file = find_latest_log(LOG_DIR, LOG_EXTENSIONS)
if latest_file:
    print(f"Tailing log: {os.path.basename(latest_file)}")
    tail_log(latest_file)
else:
    print("No log files found.")