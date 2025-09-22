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
    """Read headers and last numeric data line starting from row 5"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 5:
            print("File too short to contain data.")
            return

        header = lines[2].split("\t")   # third row: labels
        data_lines = lines[4:]          # start reading from row 5

        # Find last numeric row
        last_data = None
        for line in data_lines:
            cols = line.split("\t")
            if all(is_numeric(c) or c == '' for c in cols):
                last_data = cols

        if not last_data:
            print("No numeric data found in file.")
            return

        print(f"Latest data from file: {os.path.basename(file_path)}\n")
        for label, value in zip(header, last_data):
            print(f"{label}\n{value}\n")

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