import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Set up argument parser to accept one or more CSV files.
    parser = argparse.ArgumentParser(
        description="Plot multiple CSV files (each with 2 columns: X and Y) on a single scatter/line plot."
    )
    parser.add_argument('csv_files', metavar='CSV', type=str, nargs='+',
                        help='CSV files containing two columns: the first for X values and the second for Y values')
    args = parser.parse_args()

    # Create a new plot.
    plt.figure(figsize=(8, 6))
    
    # This list will store all x values from all files to set the x-axis ticks later.
    all_x_values = []

    # Process each CSV file.
    for csv_file in args.csv_files:
        # Read CSV assuming no header; adjust header parameter if your files include headers.
        df = pd.read_csv(csv_file, header=None)
        if df.shape[1] < 2:
            print(f"Warning: File {csv_file} does not have at least two columns; skipping.")
            continue
        
        # Extract the X and Y columns.
        x = df.iloc[:, 0]
        y = df.iloc[:, 1]
        
        # Save the x values for later tick adjustment.
        all_x_values.extend(x.tolist())
        
        # Plot the data with both line and marker.
        plt.plot(x, y, marker='o', linestyle='-', label=csv_file)

    # Remove duplicates and sort the x values so that all points (e.g., 0.4) are shown.
    unique_x = sorted(set(all_x_values))
    plt.xticks(unique_x)
    
    # Labeling the axes and setting the title.
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Combined Scatter/Line Plot from CSV Files")
    plt.legend()
    plt.grid(True)
    
    # Display the plot.
    plt.show()

if __name__ == '__main__':
    main()
