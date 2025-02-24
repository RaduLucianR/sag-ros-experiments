#!/usr/bin/env python3
import os
import csv
import argparse

def process_results(input_file, output_file):
    groups = {}  # Dictionary to hold data per sub-folder

    # Read the result.csv file.
    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        for row in reader:
            if not row or len(row) < 2:
                continue  # Skip empty or malformed lines.
            # row[0] is the file path, row[1] is the value to check.
            file_path = row[0]
            try:
                # Convert the value to integer.
                value = int(row[1])
            except ValueError:
                continue  # Skip rows where the value isn't an integer.

            # Extract sub-folder name.
            # e.g. from "SAG_input_SobhaniFig11/tasksets_01/task_set_1.csv",
            # os.path.dirname returns "SAG_input_SobhaniFig11/tasksets_01",
            # and os.path.basename returns "tasksets_01".
            subfolder = os.path.basename(os.path.dirname(file_path))

            if subfolder not in groups:
                groups[subfolder] = {'ones': 0, 'total': 0}
            groups[subfolder]['total'] += 1
            if value == 1:
                groups[subfolder]['ones'] += 1

    # Open the output CSV and write results.
    with open(output_file, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(["subfolder", "ones", "total", "ratio"])
        # Process sub-folders in sorted order.
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
    args = parser.parse_args()

    process_results(args.input, args.output)

if __name__ == '__main__':
    main()
