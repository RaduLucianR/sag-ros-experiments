#!/bin/bash
# run_analysis.sh
# This script goes through each subfolder named "tasksets_{float}"
# and for each matching pair of CSV files (task_set_x.csv and pred_x.csv)
# runs ./nptest, extracts the first result number (0 or 1), counts the ones,
# and prints the ratio (as a fraction) for each subfolder.
#
# Usage: ./run_analysis.sh [-v] folder_with_subfolders
#   -v  Enable verbose mode to display progress information.
#

verbose=0

# Parse options
while getopts ":v" opt; do
    case $opt in
        v)
            verbose=1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

shift $((OPTIND -1))

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [-v] folder"
    exit 1
fi

BASE_DIR="$1"

if [ ! -d "$BASE_DIR" ]; then
    echo "Error: $BASE_DIR is not a directory."
    exit 1
fi

if [ $verbose -eq 1 ]; then
    echo "Processing folder: $BASE_DIR"
fi

count=0
total=0
SUBFOLDER=$BASE_DIR
echo $SUBFOLDER

# Get an array of task_set CSV files to determine the total count.
files=( "$SUBFOLDER"/task_set_*.csv )
total_files=${#files[@]}
if [ $verbose -eq 1 ]; then
    echo "Found $total_files task_set CSV files in $SUBFOLDER."
fi

current=0
# Loop over each task_set CSV file in the subfolder.
for TASK_FILE in "${files[@]}"; do
    # If no file is found, skip to next folder.
    [ -e "$TASK_FILE" ] || continue

    current=$((current + 1))
    if [ $verbose -eq 1 ]; then
        echo "  [$current/$total_files] Processing file: $(basename "$TASK_FILE")"
    fi

    # Extract the numeric part (x) from task_set_x.csv.
    base=$(basename "$TASK_FILE")
    # Remove prefix and .csv extension.
    x=${base#task_set_}
    x=${x%.csv}

    # Define corresponding pred file.
    PRED_FILE="$SUBFOLDER/pred_${x}.csv"
    if [ ! -f "$PRED_FILE" ]; then
        echo "Warning: Pred file $PRED_FILE not found, skipping."
        continue
    fi

    NROF_CORES=4
    # Run the program. (Adjust the path to nptest if necessary.)
    output=$(./nptest "$TASK_FILE" --merge=no -m 4 -p "$PRED_FILE")

    # The output is expected to be like:
    # /path/to/task_set_x.csv,  0,  3560,  26,  26,  25,  2,  0.000308,  6.878906,  0,  2
    # We want the first number (after the file path), so we split by comma.
    result=$(echo "$output" | cut -d',' -f2 | sed 's/^[ \t]*//')

    # If the result is "1", increment the counter.
    if [ "$result" = "1" ]; then
        count=$((count + 1))
    fi
    total=$((total + 1))
done

if [ $total -gt 0 ]; then
    # Calculate the ratio (as a fraction) of runs that output 1.
    ratio=$(awk -v c="$count" -v t="$total" 'BEGIN { printf "%.3f", c/t }')
    echo "$SUBFOLDER $ratio"
else
    echo "$SUBFOLDER has no task_set CSV files."
fi
