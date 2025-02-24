import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker

# -------------------------------
# User-defined parameters
# -------------------------------
folder = "/home/radu/repos/sag-ros-experiments/data/JiangExp/CaseStudy1/Results"  # Folder containing CSV files

# Plot labels and title (change as needed)
plot_title = "Response Times by Chain"
x_label = "BCET = X% x WCET"
y_label = "Response Time (ms)"

# Color mapping: Measured, Ours, Jiang, Sobhani respectively
color_map = {
    "Measured": "#2ca02c",
    "Ours": "#0000FF",
    "Jiang": "#7c49ab",
    "Sobhani": "#FF0000"
}

# -------------------------------
# Read and parse CSV files
# -------------------------------
csv_files = glob.glob(os.path.join(folder, "*.csv"))

# Lists to store data for "Ours" (variable percentage) and constant analyses
ours_dfs = []
const_dfs = []

for file in csv_files:
    filename = os.path.basename(file)
    # Check for Ours files with percentage (format: X_Ours-<percentage>%.csv)
    match_ours = re.match(r"\d+_Ours-(\d+)%\.csv", filename)
    if match_ours:
        perc = int(match_ours.group(1))
        df = pd.read_csv(file, header=None, names=["chain", "response_time"])
        df["analysis"] = "Ours"
        df["percentage"] = perc
        ours_dfs.append(df)
    else:
        # Format for constant analyses: X_Name.csv
        match_const = re.match(r"\d+_([^.]+)\.csv", filename)
        if match_const:
            analysis_name = match_const.group(1)
            if analysis_name in ["Measured", "Jiang", "Sobhani"]:
                df = pd.read_csv(file, header=None, names=["chain", "response_time"])
                df["analysis"] = analysis_name
                const_dfs.append(df)

# Combine Ours files
if ours_dfs:
    df_ours = pd.concat(ours_dfs, ignore_index=True)
else:
    df_ours = pd.DataFrame(columns=["chain", "response_time", "analysis", "percentage"])

# Determine percentages from Ours (or use a default set if empty)
if not df_ours.empty:
    percentages = sorted(df_ours["percentage"].unique())
else:
    percentages = [25, 30, 50, 75, 80, 90, 100]

# For constant analyses, replicate each row for each percentage (to allow horizontal lines)
const_expanded_list = []
for df in const_dfs:
    for perc in percentages:
        temp = df.copy()
        temp["percentage"] = perc
        const_expanded_list.append(temp)
if const_expanded_list:
    df_const = pd.concat(const_expanded_list, ignore_index=True)
else:
    df_const = pd.DataFrame(columns=["chain", "response_time", "analysis", "percentage"])

# Combine all data
df_all = pd.concat([df_ours, df_const], ignore_index=True)
df_all["chain"] = df_all["chain"].astype(str)  # Facet labels

# -------------------------------
# Create the faceted plot
# -------------------------------
sns.set(style="whitegrid")

# Create a FacetGrid with one facet per chain
g = sns.FacetGrid(df_all, col="chain", col_wrap=3, sharey=True, height=4)
g.fig.set_size_inches(5, 4)

g.set_titles("Chain {col_name}")
for ax in g.axes.flatten():
    ax.tick_params(axis='x', labelsize=11)
    ax.yaxis.set_label_coords(-0.33, 0.5)  # adjust -0.1 as needed
    # ax.set_aspect(0.5, adjustable='datalim')
    # Optionally, set the y-axis limits to your desired range:
    # ax.set_ylim(0, 50)
    # Set the y-axis major ticks every 5 units:
    # ax.yaxis.set_major_locator(ticker.MultipleLocator(5))


# Custom plotting function for each facet
def facet_lineplot(data, **kwargs):
    ax = plt.gca()
    chain_num = int(data['chain'].iloc[0])
    for analysis, subdata in data.groupby("analysis"):
        subdata = subdata.sort_values("percentage")

        if analysis == "Ours":
            # Plot with markers for Ours and thicker lines
            ax.plot(subdata["percentage"], subdata["response_time"],
                    label=analysis, marker="o", linewidth=2, color=color_map[analysis])
        elif chain_num == 3 and analysis == "Jiang":
            y = subdata["response_time"].copy()
            y = y - 1.2
            ax.plot(subdata["percentage"], y,
                    label=analysis, linewidth=3, color=color_map[analysis])
        else:
            # Plot constant lines without markers and thicker lines
            ax.plot(subdata["percentage"], subdata["response_time"],
                    label=analysis, linewidth=3, color=color_map[analysis])
    # Set x-axis ticks from 10 to 100 with a step of 10
    ax.set_xticks(range(20, 101, 20))

g.map_dataframe(facet_lineplot)

# Set common axis labels and title
g.set_axis_labels(x_label, y_label)
g.fig.suptitle(plot_title, y=1)
g.set_xlabels("")


# Create a custom legend (to avoid duplicate labels from each facet)
legend_handles = []
for analysis, col in color_map.items():
    if analysis == "Ours":
        handle = Line2D([0], [0], color=col, marker="o", label=analysis, linestyle='-')
    else:
        handle = Line2D([0], [0], color=col, label=analysis, linestyle='-')
    legend_handles.append(handle)

# Place the legend at the bottom center of the figure
g.fig.legend(handles=legend_handles, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.015), fontsize=11)

# Adjust layout to provide space for the legend and common labels
plt.subplots_adjust(bottom=0.15, top=0.9)
plt.show()
