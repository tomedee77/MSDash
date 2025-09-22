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
COLUMN_WIDTH = 10    # width of each column for display

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def find_latest_log(log_dir, extensions):
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(log_dir, ext)))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def is_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tail_log(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            # Read all lines for headers
            lines = f.readlines()
            if len(lines) < 3:
                print("Not enough lines to parse headers")
                return

            header = lines[2].strip().split("\t")  # row 3 = labels

            # Print header in columns
            header_fmt = "".join(f"{h:<{COLUMN_WIDTH}}" for h in header)
            print(header_fmt)
            print("-" * len(header_fmt))

            # Move to end for tailing
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
                    row_fmt = "".join(f"{v:<{COLUMN_WIDTH}}" for v in cols)
                    print(row_fmt)
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