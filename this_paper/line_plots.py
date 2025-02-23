import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

def main():
    # Set up argument parser.
    parser = argparse.ArgumentParser(
        description="Plot multiple CSV files (each with 2 columns: X and Y) on a single scatter/line plot."
    )
    parser.add_argument('csv_files', metavar='CSV', type=str, nargs='+',
                        help='CSV files containing two columns: the first for X values and the second for Y values')
    parser.add_argument("--xlabel", type=str, default="X-axis",
                        help="Label for the X axis (default: 'X-axis')")
    parser.add_argument("--ylabel", type=str, default="Y-axis",
                        help="Label for the Y axis (default: 'Y-axis')")
    parser.add_argument("--title", type=str, default="Combined Scatter/Line Plot from CSV Files",
                        help="Title for the plot (default: 'Combined Scatter/Line Plot from CSV Files')")
    args = parser.parse_args()

    # Set global font properties and colors for high contrast.
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 8,         # Reduced font size for a smaller figure
        'text.color': '#000000',       # strong black text
        'axes.labelcolor': '#000000',  # strong black axis labels
        'xtick.color': '#000000',      # strong black tick labels
        'ytick.color': '#000000'
    })

    # Create a new plot with a smaller figure size.
    plt.figure(figsize=(3, 2.5), dpi=300)
    
    # This list will store all x values from all files to set the x-axis ticks later.
    all_x_values = []
    
    # Define a list of high-contrast colors and create a cycle.
    high_contrast_colors = cycle([
        '#FF0000',  # red
        '#6820ab',  # purple
        '#0000FF',  # blue
        '#964B00',  # brown
    ])
    markers = cycle(['o', 's', '^'])
    # markers = cycle(['$L$', '$L$', '$W$'])

    # Process each CSV file.
    for csv_file in args.csv_files:
        # Read CSV assuming no header; adjust header parameter if needed.
        df = pd.read_csv(csv_file, header=None)
        if df.shape[1] < 2:
            print(f"Warning: File {csv_file} does not have at least two columns; skipping.")
            continue
        
        # Extract the X and Y columns.
        x = df.iloc[:, 0]
        y = df.iloc[:, 1]
        
        # Save the x values for later tick adjustment.
        all_x_values.extend(x.tolist())
        
        # Determine the plot label by extracting the part of the filename before .csv.
        base_name = os.path.basename(csv_file)
        name_without_ext, _ = os.path.splitext(base_name)
        parts = name_without_ext.split('_')
        plot_label = parts[-1] if parts else name_without_ext
        
        # Choose a color from the cycle.
        color = next(high_contrast_colors)
        marker = next(markers)
        
        # Plot the data with reduced sizes:
        # - linewidth: 1.5 for a thinner line on a small canvas
        # - markersize: 4 for smaller markers
        # - marker: 'o' for circles
        # - linestyle: '-' for a solid line
        plt.plot(x, y, marker=marker, linestyle='-', linewidth=1.5, markersize=4,
                 label=plot_label, color=color)

    # Remove duplicates and sort the x values so that all points (e.g., 0.4) are shown.
    unique_x = sorted(set(all_x_values))
    # unique_x = [i for i in range(1, 11)]
    plt.xticks(unique_x)
    # plt.yticks([i / 10 for i in range(1, 11)])
    # Label the axes and set the title using the command-line provided values.
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)
    plt.title(args.title)
    plt.legend(fontsize=8)  # reduce legend font size if needed
    plt.grid(True, linewidth=0.5, color='gray', alpha=0.7)
    plt.tight_layout()  # Adjusts subplot params for a neat fit
    
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', labelsize=8)

    # Save the figure.
    title = "Fig9"
    # output_path = f"/home/radu/repos/sag-ros-experiments/data/SobhaniExp/{title}/tasksets_nrofjobs_max_5k/{title}Tight.png"
    output_path = "./fig.png"
    plt.savefig(output_path,
                bbox_inches="tight", pad_inches=0, dpi=300)

    # Display the plot.
    plt.show()

if __name__ == '__main__':
    main()
