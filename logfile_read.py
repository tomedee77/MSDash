#!/usr/bin/env python3
import os
import glob

# ----------------------------
# CONFIG
# ----------------------------
LOG_DIR = "/home/tomedee77/TunerStudioProjects/VWRX/DataLogs"  # adjust as needed
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

def read_last_data(file_path):
    """Read headers and last data line, ignoring metadata/blank lines"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = [line.strip() for line in f if line.strip()]  # skip blank lines

        # Find the first line that looks like a header (non-numeric columns)
        header_line = None
        for i, line in enumerate(lines):
            cols = line.split("\t")
            if all(not col.replace(".", "", 1).isdigit() for col in cols):
                header_line = i
                break
        if header_line is None:
            print("No header found in file.")
            return

        header = lines[header_line].split("\t")
        data_lines = lines[header_line + 1:]
        if not data_lines:
            print("No data lines found after header.")
            return

        last_line = data_lines[-1].split("\t")
        print(f"Latest data from file: {os.path.basename(file_path)}\n")
        for label, value in zip(header, last_line):
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