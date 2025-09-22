import os
import glob

# ----------------------------
# CONFIG
# ----------------------------
LOG_DIR = "/home/tomedee77/TunerStudioProjects/VWRX/DataLogs"
EXTENSIONS = ["*.mlg", "*.msl"]  # File types to check

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def find_latest_file():
    """Find the newest file in the folder with given extensions"""
    files = []
    for ext in EXTENSIONS:
        files.extend(glob.glob(os.path.join(LOG_DIR, ext)))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def read_last_data(file_path):
    """Read headers and last data line, ignoring metadata/blank lines"""
    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]  # skip blank lines

        # Find the first line that looks like a header (contains only non-numeric words)
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
        print(f"Latest data from file: {file_path}\n")
        for label, value in zip(header, last_line):
            print(f"{label}: {value}")

# ----------------------------
# MAIN
# ----------------------------
latest_file = find_latest_file()
if latest_file:
    read_last_data(latest_file)
else:
    print("No log files found.")