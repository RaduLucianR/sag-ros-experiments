#!/usr/bin/env python3
import argparse
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle, islice

# Fixed colors at the start and end
first_color = '#2ca02c'  # Green
last_two_colors = ['#7c49ab', '#FF0000']  # Purple, Red

# Get the 'tab20' colormap colors
tab20_colors = list(plt.get_cmap('tab20').colors)

# Define the function to generate the cycle
def custom_color_cycle(n_intermediate):
    yield first_color  # First color
    intermediate_colors = islice(cycle(tab20_colors), n_intermediate)  # Take n_intermediate colors from tab20
    yield from intermediate_colors
    yield from last_two_colors  # Last two colors

def main():
    # Parse command-line arguments: either one or more CSV files, or a single directory.
    parser = argparse.ArgumentParser(
        description="Create a grouped bar plot from CSV files. Each CSV should have two columns: X and Y."
    )
    parser.add_argument("paths", metavar="PATH", type=str, nargs="+",
                        help="One or more CSV files or a directory containing CSV files")
    args = parser.parse_args()

    # If the single argument provided is a directory, get all CSV files inside it.
    if len(args.paths) == 1 and os.path.isdir(args.paths[0]):
        folder = args.paths[0]
        csv_files = glob.glob(os.path.join(folder, "*.csv"))
        if not csv_files:
            print(f"No CSV files found in directory '{folder}'.")
            return
    else:
        csv_files = args.paths

    # Sort files for consistent ordering.
    csv_files.sort()

    # Read the first CSV to extract the X-axis categories.
    first_df = pd.read_csv(csv_files[0], header=None)
    x_categories = first_df.iloc[:, 0].tolist()
    num_categories = len(x_categories)

    # Initialize lists to store Y-values and labels from each CSV file.
    y_data = []    # List of lists (one per CSV)
    labels = []    # To store CSV filenames as labels

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, header=None)
        if len(df) != num_categories:
            print(f"Warning: File '{csv_file}' has a different number of rows than the first file.")
        # Assume Y-values are in the second column.
        y_values = df.iloc[:, 1].tolist()
        y_data.append(y_values)
        bn = os.path.basename(csv_file)
        label, extension = os.path.splitext(bn)
        # If label contains an underscore, take the part after it.
        label = label.split('_', 1)[1] if '_' in label else label
        labels.append(label)

    # Convert y_data to a NumPy array for easier indexing.
    # y_data will have shape (n_files, num_categories)
    y_data = np.array(y_data)
    n_files = len(csv_files)

    # Determine positions for the groups and width for each bar.
    ind = np.arange(num_categories)  # the x locations for the groups
    total_width = 0.5                  # total width reserved for all bars in a group
    width = total_width / n_files      # computed width for each bar if they touch

    # To introduce a small gap (roughly equivalent to ~2 pixels), use 95% of the computed width.
    bar_width = width * 0.65
    
    contrast_colors = cycle([  '#2ca02c',  # a solid green (not too lime)
                               '#0000FF',
                               '#7c49ab', # purple
                               '#FF0000', # a strong red
                              ])

    # contrast_colors = cycle(plt.get_cmap('tab20').colors)
    # contrast_colors = cycle(custom_color_cycle(7))

    # Create the bar plot.
        # Set global font properties and colors for high contrast.
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 6,         # Reduced font size for a smaller figure
        'text.color': '#000000',       # strong black text
        'axes.labelcolor': '#000000',  # strong black axis labels
        'xtick.color': '#000000',      # strong black tick labels
        'ytick.color': '#000000'
    })

    # fig, ax = plt.subplots(figsize=(10, 6))
    fig, ax = plt.subplots(figsize=(3, 2.5), dpi=300)
    for i in range(n_files):
        # Compute an offset so that the bars in each group are centered.
        offset = (i - (n_files - 1) / 2) * width
        color = next(contrast_colors)
        ax.bar(ind + offset, y_data[i], bar_width,
               label=labels[i],
               color=color,
               edgecolor='black',
               linewidth=0.7
            ) 

    # Set x-axis ticks and labels.
    x_category_labels = [f"Chain {i}" for i in x_categories]
    ax.set_xticks(ind)
    # ax.set_yticks([i for i in range(10, 180, 5)])
    # ax.set_yticks([i for i in range(10, 110, 10)])
    ax.set_xticklabels(x_category_labels)
    ax.set_xlabel("")
    ax.set_ylabel("Response Time (ms)")
    ax.set_title("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)  # Ensure grid lines are drawn below other plot elements
    ax.grid(True, axis='y', linewidth=0.5, color='gray', alpha=0.7)

    # Place the legend outside the plot at the bottom center.
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=n_files, fontsize=6)

    plt.tight_layout()
    plt.savefig("JiangCaseStudy.png", bbox_inches="tight", pad_inches=0, dpi=300)
    plt.show()

if __name__ == '__main__':
    main()
