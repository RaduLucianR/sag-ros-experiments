import pandas as pd
import sys

def compute_max_difference(csv1, csv2, task_pairs):
    # Load the CSV files
    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)

    # Strip any leading/trailing spaces from column names
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Store results for each pair
    results = {}

    for a, b in task_pairs:
        # Filter rows based on task IDs
        df_a = df1[df1['Task ID'] == a]
        df_b = df2[df2['Task ID'] == b]

        # Initialize the maximum difference for this pair
        max_diff = float('-inf')

        # Ensure both task a and task b have the same number of rows
        if len(df_a) != len(df_b):
            print(f"Error: Task ID {a} has {len(df_a)} rows, but Task ID {b} has {len(df_b)} rows.")
            continue
        
        # print(df_a, df_b)
        # For corresponding rows, calculate WCRT(row_b) - Arrival min(row_a)
        for row_a, row_b in zip(df_a.iterrows(), df_b.iterrows()):
            _, row_a = row_a
            _, row_b = row_b
            # Calculate the difference WCRT(row_b) - Arrival min(row_a)
            diff = row_b['WCRT'] - row_a['Arrival min']
            max_diff = max(max_diff, diff)

        results[(a, b)] = max_diff

    return results

if __name__ == "__main__":
    # Ensure that two CSV file paths are passed as arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv1_path> <csv2_path>")
        sys.exit(1)

    # Get the CSV paths from arguments
    csv1 = sys.argv[1]
    csv2 = sys.argv[2]

    # Example task pairs
    # task_pairs = [(1, 2), (1, 5), (6, 8), (9, 12)] # Sobhani

    # task_pairs = [(1, 4), (2, 7), (3, 9)] # Jiang
    task_pairs = [(1, 2), (1,5)] # small
    # Run the function
    max_differences = compute_max_difference(csv1, csv2, task_pairs)

    # Display the results
    for pair, diff in max_differences.items():
        print(f"Max difference for pair {pair}: {diff}")
