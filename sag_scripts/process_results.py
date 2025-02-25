#!/usr/bin/env python3
import os
import csv
import argparse

def process_results(input_file, output_file, base_folder=None):
    groups = {}  # Dictionary to hold data per sub-folder (grouping key)

    # Read the result.csv file.
    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        for row in reader:
            if not row or len(row) < 2:
                continue  # Skip empty or malformed lines.
            # row[0] is the file path, row[1] is the value to check.
            file_path = row[0].strip()
            try:
                value = int(row[1].strip())
            except ValueError:
                continue  # Skip rows where the value isn't an integer.

            # Determine grouping key.
            file_dir = os.path.dirname(file_path)
            if base_folder:
                # Calculate relative path from the provided base folder.
                group_key = os.path.relpath(file_dir, start=base_folder)
            else:
                # Fallback: use the immediate parent folder name.
                group_key = os.path.basename(file_dir)

            if group_key not in groups:
                groups[group_key] = {'ones': 0, 'total': 0}
            groups[group_key]['total'] += 1
            if value == 1:
                groups[group_key]['ones'] += 1

    # Write the calculated ratios to the output CSV.
    with open(output_file, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(["subfolder", "ones", "total", "ratio"])
        for subfolder in sorted(groups.keys()):
            ones = groups[subfolder]['ones']
            total = groups[subfolder]['total']
            ratio = ones / total if total else 0
            writer.writerow([subfolder, ones, total, ratio])
            print(f"{subfolder}: {ones}/{total} = {ratio:.2f}")

def main():
    parser = argparse.ArgumentParser(
        description="Process result.csv to calculate the ratio of 1s (2nd column) per sub-folder."
    )
    parser.add_argument("--input", default="result.csv", help="Input CSV file (default: result.csv)")
    parser.add_argument("--output", default="data.csv", help="Output CSV file (default: data.csv)")
    parser.add_argument("--base", default=None, help="Base folder to compute relative path for grouping (optional)")
    args = parser.parse_args()

    process_results(args.input, args.output, base_folder=args.base)

if __name__ == '__main__':
    main()
