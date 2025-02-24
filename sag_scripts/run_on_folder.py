#!/usr/bin/env python3
import os
import re
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def process_pair(task):
    task_file, pred_file = task
    cmd = [
        "/home/radu/repos/schedule_abstraction-ros2/build/nptest",
        task_file,
        "-m", "4",
        "-p", pred_file
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Expected output is one CSV-formatted line from stdout.
        return (task_file, result.stdout.strip(), True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Error processing {task_file} and {pred_file}: {e.stderr.strip()}"
        return (task_file, error_msg, False)
    except Exception as e:
        error_msg = f"Exception processing {task_file} and {pred_file}: {str(e)}"
        return (task_file, error_msg, False)

def main():
    parser = argparse.ArgumentParser(
        description="Process CSV files in sub-folders in lexicographic order with parallel execution and immediate saving."
    )
    parser.add_argument("folder", help="Path to the folder containing sub-folders with CSVs")
    parser.add_argument("--output", default="results.csv",
                        help="Output CSV file to append results (default: results.csv)")
    args = parser.parse_args()

    # Read existing results to check which task files have already been processed.
    processed_files = set()
    if os.path.exists(args.output):
        with open(args.output, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if parts:
                    processed_files.add(parts[0].strip())

    tasks = []      # List of tuples: (task_file, pred_file)
    subfolders = [] # For CLI feedback on sub-folder traversal

    # Traverse directories in lexicographic order.
    for root, dirs, files in os.walk(args.folder):
        dirs.sort()    # Sort sub-folders lexicographically
        files.sort()   # Sort files lexicographically
        subfolders.append(root)
        for file in files:
            match = re.match(r'^task_set_(.+)\.csv$', file)
            if match:
                identifier = match.group(1)
                task_file = os.path.join(root, file)
                pred_file = os.path.join(root, f"pred_{identifier}.csv")
                if os.path.exists(pred_file):
                    if task_file in processed_files:
                        tqdm.write(f"Skipping already processed file: {task_file}")
                    else:
                        tasks.append((task_file, pred_file))
                else:
                    tqdm.write(f"Missing predecessor file for: {task_file} (expected {pred_file})")

    # Display progress for sub-folders (just reporting the count)
    with tqdm(total=len(subfolders), desc="Sub-folders", unit="folder") as pbar:
        for _ in subfolders:
            pbar.update(1)

    # Sort tasks lexicographically by task file path.
    tasks.sort(key=lambda t: t[0])

    # Open the output file in append mode.
    with open(args.output, 'a') as out_file:
        # Process CSV pairs concurrently using 6 processes.
        with ProcessPoolExecutor(max_workers=6) as executor:
            for task_file, output, success in tqdm(
                    executor.map(process_pair, tasks),
                    total=len(tasks), desc="Processing CSV pairs", unit="pair"):
                out_file.write(output + "\n")
                out_file.flush()
                if not success:
                    tqdm.write(output)

if __name__ == '__main__':
    main()
