#!/bin/bash
# run_analysis.sh
# This script goes through each subfolder named "tasksets_{float}"
# and for each matching pair of CSV files (task_set_X.csv and pred_X.csv)
# runs ./nptest for each -m value from 1 to 16, extracts the first result (0 or 1),
# and counts the number of task sets that are schedulable (i.e. result == 1).
#
# The ratio is then computed as: schedulable tasksets / 1000,
# because the total number of task sets is assumed to be 1000 for each m.
#
# Additionally, the script saves its progress in a file (progress.dat) in each subfolder.
# On subsequent runs, it resumes processing from the last CSV file that was handled.
#
# Usage: ./run_analysis.sh [-v] folder_with_subfolders
#   -v  Enable verbose mode.
#
verbose=0

# Parse options.
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
    echo "Usage: $0 [-v] folder_with_subfolders"
    exit 1
fi

BASE_DIR="$1"

if [ ! -d "$BASE_DIR" ]; then
    echo "Error: $BASE_DIR is not a directory."
    exit 1
fi

# Loop over each subfolder whose name starts with "tasksets_"
for SUBFOLDER in "$BASE_DIR"/tasksets_*; do
    # Skip if not a directory.
    [ -d "$SUBFOLDER" ] || continue

    echo "Processing subfolder: $SUBFOLDER"

    progress_file="$SUBFOLDER/progress.dat"

    # Load previously saved progress if it exists; otherwise, initialize.
    if [ -f "$progress_file" ]; then
        [ $verbose -eq 1 ] && echo "  Loading progress from $progress_file"
        source "$progress_file"
    else
        # LAST_PROCESSED tracks the highest numeric X processed so far.
        LAST_PROCESSED=0
        # For m=1..16, initialize the schedulable count variables.
        for m in {1..16}; do
            printf -v "count$m" '%d' 0
        done
    fi

    # Get an array of task_set CSV files.
    files=( "$SUBFOLDER"/task_set_*.csv )
    if [ ${#files[@]} -eq 0 ]; then
        echo "  No task_set CSV files found in $SUBFOLDER."
        continue
    fi

    # Sort files numerically based on the numeric portion of the filename.
    sorted_files=($(for f in "${files[@]}"; do
        # Extract the number from filename "task_set_X.csv"
        num=$(basename "$f" | sed -E 's/task_set_([0-9]+)\.csv/\1/')
        echo "$num:$f"
    done | sort -t: -k1,1n | cut -d: -f2))

    for TASK_FILE in "${sorted_files[@]}"; do
        [ -e "$TASK_FILE" ] || continue

        base=$(basename "$TASK_FILE")
        # Extract the numeric part X from task_set_X.csv.
        x=$(echo "$base" | sed -E 's/task_set_([0-9]+)\.csv/\1/')

        # Skip if this file has already been processed.
        if [ "$x" -le "$LAST_PROCESSED" ]; then
            [ $verbose -eq 1 ] && echo "  Skipping already processed file: $base"
            continue
        fi

        echo "  Processing file: $base"

        # Define the corresponding prediction file.
        PRED_FILE="$SUBFOLDER/pred_${x}.csv"
        if [ ! -f "$PRED_FILE" ]; then
            echo "    Warning: Pred file $PRED_FILE not found, skipping."
            continue
        fi

        # For each m value from 1 to 16, run ./nptest and update schedulable count.
        for (( m=1; m<=16; m++ )); do
            output=$(./nptest "$TASK_FILE" --merge=no -m "$m" -p "$PRED_FILE")
            # Expected output example:
            # /path/to/task_set_X.csv,  0,  3560,  26,  26,  25,  2,  0.000308,  6.878906,  0,  2
            # Extract the second field (result: 0 or 1).
            result=$(echo "$output" | cut -d',' -f2 | sed 's/^[ \t]*//')
            if [ "$result" = "1" ]; then
                var="count$m"
                current_count=${!var}
                current_count=$(( current_count + 1 ))
                printf -v "$var" '%d' "$current_count"
            fi
        done

        # Update LAST_PROCESSED.
        LAST_PROCESSED=$x

        # Save progress to disk after processing this CSV.
        {
            echo "LAST_PROCESSED=$LAST_PROCESSED"
            for (( m=1; m<=16; m++ )); do
                var="count$m"
                echo "$var=${!var}"
            done
        } > "$progress_file"
    done

    # After processing, print the ratios for each m.
    # The ratio is schedulable task sets (count) divided by 1000.
    echo "Results for subfolder: $SUBFOLDER"
    for (( m=1; m<=16; m++ )); do
        var="count$m"
        countVal=${!var}
        ratio=$(awk -v c="$countVal" 'BEGIN { printf "%.3f", c/1000 }')
        echo "  m=$m: $ratio ( $countVal / 1000 )"
    done
    echo    # Blank line for readability.
done
