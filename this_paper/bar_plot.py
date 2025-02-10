#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Parse command-line arguments: one or more CSV files.
    parser = argparse.ArgumentParser(
        description="Create a grouped bar plot from CSV files. Each CSV should have two columns: X and Y."
    )
    parser.add_argument("csv_files", metavar="CSV", type=str, nargs="+",
                        help="CSV files with two columns (first: X values, second: Y values)")
    args = parser.parse_args()

    # Read the first CSV to extract the X-axis categories.
    first_df = pd.read_csv(args.csv_files[0], header=None)
    x_categories = first_df.iloc[:, 0].tolist()
    num_categories = len(x_categories)

    # Initialize lists to store Y-values and labels from each CSV file.
    y_data = []    # will be a list of lists (one per CSV)
    labels = []    # to store CSV filenames as labels

    for csv_file in args.csv_files:
        df = pd.read_csv(csv_file, header=None)
        if len(df) != num_categories:
            print(f"Warning: File '{csv_file}' has a different number of rows than the first file.")
        # Assume the Y-values are in the second column.
        y_values = df.iloc[:, 1].tolist()
        y_data.append(y_values)
        labels.append(csv_file)

    # Convert y_data to a NumPy array for easier indexing.
    # y_data will have shape (n_files, num_categories)
    y_data = np.array(y_data)
    n_files = len(args.csv_files)

    # Determine positions for the groups and width for each bar.
    ind = np.arange(num_categories)         # the x locations for the groups
    total_width = 0.8                         # total width for all bars in a group
    width = total_width / n_files             # width for each individual bar

    # Create the bar plot.
    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(n_files):
        # Compute an offset so that the bars are grouped together
        offset = (i - (n_files - 1) / 2) * width
        ax.bar(ind + offset, y_data[i], width, label=labels[i])

    # Set x-axis ticks and labels.
    ax.set_xticks(ind)
    ax.set_xticklabels(x_categories)
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Grouped Bar Plot from CSV Files")
    ax.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
