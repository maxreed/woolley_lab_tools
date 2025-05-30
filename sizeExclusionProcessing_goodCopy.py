#!/usr/bin/env python3
import os
import re
import csv
import argparse
import numpy as np
import matplotlib.pyplot as plt

# Number of points to use for baseline correction at start and end
BASELINE_WINDOW = 100

# -----------------------------------------------------------------------------
# Function: read_file
# Purpose: Read a single FPLC output text file and extract data series
# Input: path to the text file
# Output:
#   - channels: list of tuples (name, kind, index in row)
#   - times: NumPy array of time values
#   - data: dict of NumPy arrays for each channel (uv, quad, volume)
# -----------------------------------------------------------------------------
def read_file(path):
    lines = open(path, newline='').read().splitlines()

    # Build a map from "QuadTec N" label to its wavelength string (e.g. "360.0")
    wl_map = {}
    for line in lines:
        if line.lower().startswith('quadtec') and '(' in line:
            # Example line: QuadTec 1, (360.0 nm), AU
            m = re.match(r"(QuadTec \d+),\s*\(([\d\.]+)\s*nm\)", line)
            if m:
                label = m.group(1).strip()
                wl_map[label] = m.group(2)  # wavelength, e.g. "360.0"

    # Find where numeric data starts: first line where all comma-separated parts are floats
    data_start = None
    for idx, line in enumerate(lines):
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            continue
        try:
            _ = [float(p) for p in parts]
            data_start = idx
            break
        except ValueError:
            continue
    if data_start is None or data_start == 0:
        raise ValueError(f"No data block found in {path}")

    # The header row is just before the first numeric row
    header_line = lines[data_start - 1]
    col_names = [c.strip() for c in header_line.split(',')]

    # Determine which columns to keep
    # We look for 'uv', 'volume', QuadTec columns (using our wl_map)
    channels = []  # will hold tuples (output_name, kind, column_index)
    for i, name in enumerate(col_names):
        nl = name.lower()
        if nl.startswith('quadtec') and name in wl_map:
            out_name = f"quad_{wl_map[name]}nm"  # e.g. "quad_360.0nm"
            channels.append((out_name, "quad", i))
        elif nl == 'uv':
            channels.append(("uv", "uv", i))
        elif nl == 'volume':
            channels.append(("volume", "volume", i))

    # Prepare storage for each channel
    data = {ch[0]: [] for ch in channels}
    times = []

    # Read the numeric data rows
    reader = csv.reader(lines[data_start:], skipinitialspace=True)
    for row in reader:
        # Skip incomplete rows
        if len(row) < len(col_names):
            continue
        # First column is time
        try:
            t = float(row[0])
        except ValueError:
            continue
        times.append(t)
        # Extract each channel's value by index
        for name, _, idx in channels:
            try:
                val = float(row[idx])
            except Exception:
                val = np.nan
            data[name].append(val)

    # Convert Python lists to NumPy arrays for easier math
    times = np.array(times)
    for k in data:
        data[k] = np.array(data[k])

    return channels, times, data

# -----------------------------------------------------------------------------
# Function: process_all
# Purpose: Process every file in a directory, apply volume correction & baseline
# Input: directory path containing text files
# Output:
#   - names: list of file basenames
#   - times_list: list of NumPy time arrays
#   - data_list: list of dicts with corrected data arrays
#   - channels: the channel definition from the first file
# -----------------------------------------------------------------------------
def process_all(input_dir):
    # List all non-hidden files, sorted for consistency
    files = sorted(f for f in os.listdir(input_dir) if not f.startswith('.'))
    names, times_list, data_list = [], [], []
    common_channels = None

    for fn in files:
        path = os.path.join(input_dir, fn)
        channels, times, data = read_file(path)
        # Ensure all files share the same channel order
        if common_channels is None:
            common_channels = channels
        else:
            if [c[0] for c in channels] != [c[0] for c in common_channels]:
                raise ValueError(f"Channel mismatch in {fn}")

        # Correct volume and absorbances
        vol = data['volume']
        # Find last index at 5.0 mL and last index at 10.0 mL
        idx5  = np.where(np.isclose(vol, 5.0))[0]
        idx10 = np.where(np.isclose(vol, 10.0))[0]
        if idx5.size == 0 or idx10.size == 0:
            raise ValueError(f"Missing 5.0 or 10.0 mL point in {fn}")
        start_idx = idx5[-1]
        end_idx   = idx10[-1]
        N = vol.size

        # Build a continuous volume series for all data points
        # Compute step size (delta) from the 5→10 region
        region_len = end_idx - start_idx + 1
        delta = (10.05 - 5.05) / float(region_len - 1)
        # new_vol[i] = 5.05 + delta * (i - start_idx)
        new_vol = 5.05 + delta * (np.arange(N) - start_idx)

        # Baseline correction for UV and QuadTec
        for name, kind, _ in channels:
            if kind in ('uv', 'quad'):
                arr = data[name]
                # Compute average of the first and last BASELINE_WINDOW points
                s0, s1 = start_idx, min(start_idx + BASELINE_WINDOW, N)
                start_avg = np.nanmean(arr[s0:s1])
                e0, e1 = max(N - BASELINE_WINDOW, 0), N
                end_avg = np.nanmean(arr[e0:e1])
                dp0, dp1 = start_idx, N - 1
                slope = (end_avg - start_avg) / float(dp1 - dp0) if dp1 != dp0 else 0.0
                # Create linear baseline over the full trace
                baseline = start_avg + slope * (np.arange(N) - dp0)
                # Subtract baseline from original data
                data[name] = arr - baseline

        # Replace raw volume with smooth continuous volume
        data['volume'] = new_vol

        # Store results for this file
        names.append(os.path.splitext(fn)[0])
        times_list.append(times)
        data_list.append(data)

    return names, times_list, data_list, common_channels

# -----------------------------------------------------------------------------
# Function: write_output
# Purpose: Write combined, tab-separated output for all samples
# -----------------------------------------------------------------------------
def write_output(out_path, names, data_list, channels):
    # Determine how many rows to write: the shortest trace length across samples
    lengths = [len(data['volume']) for data in data_list]
    num_rows = min(lengths)

    # Header row: sample__channel for each sample and channel
    header = [f"{nm}__{ch[0]}" for nm in names for ch in channels]
    with open(out_path, 'w', newline='') as outf:
        writer = csv.writer(outf, delimiter='\t')
        writer.writerow(header)
        # Write each timepoint index i across all samples
        for i in range(num_rows):
            row = []
            for data in data_list:
                for ch_name, _, _ in channels:
                    row.append(f"{data[ch_name][i]:.6g}")
            writer.writerow(row)

# -----------------------------------------------------------------------------
# Function: plot_all
# Purpose: Quick QC plot of all UV/QuadTec traces over time
# -----------------------------------------------------------------------------
def plot_all(names, times_list, data_list, channels):
    plt.figure(figsize=(8,6))
    for nm, times, data in zip(names, times_list, data_list):
        for ch_name, kind, _ in channels:
            if kind in ('uv', 'quad'):
                plt.plot(times, data[ch_name], label=f"{nm}:{ch_name}")
    plt.legend()
    plt.xlabel('Time (s)')
    plt.ylabel('Absorbance (AU)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Main: parse CLI arguments and run the processing pipeline
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Process FPLC data: baseline-correct UV/QuadTec and rescale volume"
    )
    parser.add_argument('-i', '--input-dir', required=True,
                        help='Folder containing FPLC text files')
    parser.add_argument('-o', '--output', required=True,
                        help='Tab-separated output filename')
    parser.add_argument('--no-plot', action='store_true',
                        help='Skip the QC plot')
    args = parser.parse_args()

    names, times_list, data_list, channels = process_all(args.input_dir)
    write_output(args.output, names, data_list, channels)
    print(f"Wrote processed data to {args.output}")

    if not args.no_plot:
        plot_all(names, times_list, data_list, channels)

if __name__ == '__main__':
    main()
