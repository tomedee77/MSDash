#!/usr/bin/env python3
import os
import glob

# ----------------------------
# CONFIG
# ----------------------------
LOG_DIR = "/home/tomedee77/TunerStudioProjects/VWRX/DataLogs"
LOG_EXTENSIONS = ["*.mlg", "*.msl"]

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

def read_last_data(file_path):
    """Read headers and last numeric data line"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Skip metadata until we find a header line (non-numeric) followed by a numeric line
        header = None
        last_data = None
        for i in range(len(lines) - 1):
            cols = lines[i].split("\t")
            next_cols = lines[i + 1].split("\t")
            if any(not is_numeric(c) for c in cols) and all(is_numeric(c) for c in next_cols):
                header = cols
                # Now find the last numeric line in the remainder of the file
                for line in lines[i + 1:]:
                    data_cols = line.split("\t")
                    if all(is_numeric(c) or c == '' for c in data_cols):
                        last_data = data_cols
                break

        if not header or not last_data:
            print("No valid data found in file.")
            return

        print(f"Latest data from file: {os.path.basename(file_path)}\n")
        for label, value in zip(header, last_data):
            print(f"{label}: {value}")

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

# ----------------------------
# MAIN
# ----------------------------
latest_file = find_latest_log(LOG_DIR, LOG_EXTENSIONS)
if latest_file:
    read_last_data(latest_file)
else:
    print("No log files found.")