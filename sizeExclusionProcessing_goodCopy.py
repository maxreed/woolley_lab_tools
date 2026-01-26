#!/usr/bin/env python3
import os
import re
import csv
import argparse
import numpy as np
import matplotlib.pyplot as plt

# Number of points used for local averaging at baseline start and end
BASELINE_WINDOW = 300

def read_file(path):
    """Parses a single FPLC data file and returns extracted channel metadata, times, and data arrays."""
    lines = open(path, newline='').read().splitlines()
    wl_map = {}

    # Extract mapping from QuadTec labels to wavelengths (e.g., "QuadTec 1" → "280")
    for line in lines:
        if line.lower().startswith('quadtec') and '(' in line:
            m = re.match(r"(QuadTec \d+),\s*\(([-]+)\s*nm\)", line)
            if m:
                label = m.group(1).strip()
                wl_map[label] = m.group(2)

    # Identify the line where numeric data begins
    data_start = None
    for idx, line in enumerate(lines):
        parts = [p.strip() for p in line.split(',')]
        try:
            _ = [float(p) for p in parts]
            data_start = idx
            break
        except ValueError:
            continue
    if data_start is None:
        raise ValueError(f"No data block found in {path}")

    # Parse header and identify columns of interest
    header_line = lines[data_start - 1]
    col_names = [c.strip() for c in header_line.split(',')]
    channels = []
    for i, name in enumerate(col_names):
        nl = name.lower()
        if nl.startswith('quadtec') and name in wl_map:
            out_name = f"quad_{wl_map[name]}nm"
            channels.append((out_name, "quad", i))
        elif nl == 'uv':
            channels.append(("uv", "uv", i))
        elif nl == 'volume':
            channels.append(("volume", "volume", i))

    # Read time series and associated data for each selected channel
    data = {ch[0]: [] for ch in channels}
    times = []
    reader = csv.reader(lines[data_start:], skipinitialspace=True)
    for row in reader:
        if len(row) < len(col_names):
            continue
        try:
            t = float(row[0])
        except ValueError:
            continue
        times.append(t)
        for name, _, idx in channels:
            try:
                val = float(row[idx])
            except Exception:
                val = np.nan
            data[name].append(val)

    # Convert lists to numpy arrays for processing
    times = np.array(times)
    for k in data:
        data[k] = np.array(data[k])

    return channels, times, data

def process_all(input_dir, start_vol=5.0, end_vol=10.0):
    """Processes all FPLC files in a directory, applies baseline correction, and standardizes volume."""
    files = sorted(f for f in os.listdir(input_dir) if not f.startswith('.'))
    names, times_list, data_list = [], [], []
    common_channels = None

    for fn in files:
        path = os.path.join(input_dir, fn)
        channels, times, data = read_file(path)

        # Ensure channel consistency across files
        if common_channels is None:
            common_channels = channels
        else:
            if [c[0] for c in channels] != [c[0] for c in common_channels]:
                raise ValueError(f"Channel mismatch in {fn}")

        vol = data['volume']

        # Locate indices corresponding to start and end volume for baseline region.
        # These initial arrays have the indices of ALL instances of start_vol and end_vol volumes.
        idx_start = np.where(np.isclose(vol, start_vol, atol=0.01))[0]
        idx_end = np.where(np.isclose(vol, end_vol, atol=0.01))[0]
        if idx_start.size == 0 or idx_end.size == 0:
            raise ValueError(f"Missing baseline volume points ({start_vol} or {end_vol}) in {fn}")
        start_idx = idx_start[0] # the first time we see start_vol
        end_idx = idx_end[0] # the first time we see end_vol
        N = vol.size

        # Construct corrected volume axis so that all traces are aligned in volume space
        region_len = end_idx - start_idx
        delta = (end_vol - start_vol) / float(region_len)
        # The reason why we take 0.05 away from start_vol is because start_idx is the index of the FIRST time we see start_vol. The program
        # rounds volumes to the nearest 0.1 mL, meaning the first time we see start_vol the program is rounding up - meaning the actual volume
        # will be about 0.05 mL BELOW start_vol.
        new_vol = (start_vol - 0.05) + delta * (np.arange(N) - start_idx)

        # Apply linear baseline correction for each absorbance channel
        for name, kind, _ in channels:
            if kind in ('uv', 'quad'):
                arr = data[name]
                s0 = max(start_idx - BASELINE_WINDOW//2, 0)
                s1 = min(start_idx + BASELINE_WINDOW//2, N)
                e0 = max(end_idx - BASELINE_WINDOW//2, 0)
                e1 = min(end_idx + BASELINE_WINDOW//2, N)

                start_avg = np.nanmean(arr[s0:s1])
                end_avg = np.nanmean(arr[e0:e1])

                # Fit and subtract linear baseline between start and end points
                slope = (end_avg - start_avg) / float(end_idx - start_idx) if end_idx != start_idx else 0.0
                baseline = start_avg + slope * (np.arange(N) - start_idx)
                data[name] = arr - baseline

        data['volume'] = new_vol
        names.append(os.path.splitext(fn)[0])
        times_list.append(times)
        data_list.append(data)

    return names, times_list, data_list, common_channels

def write_output(out_path, names, data_list, channels):
    """Writes corrected and aligned data to a tab-separated file."""
    lengths = [len(data['volume']) for data in data_list]
    num_rows = min(lengths)

    # Create header by combining run names and channel labels
    header = [f"{nm}__{ch[0]}" for nm in names for ch in channels]
    with open(out_path, 'w', newline='') as outf:
        writer = csv.writer(outf, delimiter='\t')
        writer.writerow(header)
        for i in range(num_rows):
            row = []
            for data in data_list:
                for ch_name, _, _ in channels:
                    row.append(f"{data[ch_name][i]:.6g}")
            writer.writerow(row)

def plot_all(names, times_list, data_list, channels, xaxis='time'):
    """Plots all absorbance traces using either time or corrected volume as x-axis."""
    plt.figure(figsize=(8,6))
    for nm, times, data in zip(names, times_list, data_list):
        x = data['volume'] if xaxis == 'volume' else times
        for ch_name, kind, _ in channels:
            if kind in ('uv', 'quad'):
                plt.plot(x, data[ch_name], label=f"{nm}:{ch_name}")
    plt.legend()
    plt.xlabel('Volume (mL)' if xaxis == 'volume' else 'Time (s)')
    plt.ylabel('Absorbance (AU)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    """Main entry point: handles argument parsing, runs processing pipeline, and saves results."""
    parser = argparse.ArgumentParser(description="Process FPLC data with custom baseline correction and plotting")
    parser.add_argument('-i', '--input-dir', required=True, help='Folder containing FPLC text files')
    parser.add_argument('-o', '--output', required=True, help='Output TSV file')
    parser.add_argument('--baseline-start-vol', type=float, default=5.0, help='Start volume for baseline correction')
    parser.add_argument('--baseline-end-vol', type=float, default=10.0, help='End volume for baseline correction')
    parser.add_argument('--xaxis', choices=['time', 'volume'], default='time', help='X-axis for plot: time or volume')
    parser.add_argument('--no-plot', action='store_true', help='Skip the QC plot')
    args = parser.parse_args()

    names, times_list, data_list, channels = process_all(
        args.input_dir,
        start_vol=args.baseline_start_vol,
        end_vol=args.baseline_end_vol
    )
    write_output(args.output, names, data_list, channels)
    print(f"Wrote processed data to {args.output}")

    if not args.no_plot:
        plot_all(names, times_list, data_list, channels, xaxis=args.xaxis)

if __name__ == '__main__':
    main()
