import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncnorm

# Set global font size to 8
plt.rcParams.update({'font.size': 8})

# Define x-axis data from 10 to 1000 in steps of 10
x = np.arange(10, 1001, 20)

# Define the horizontal baselines for each scatter group
horizontal_lines = [0.2, 21, 36, 52, 71, 87, 105, 125, 146]

labels = [f"n={i}" for i in range(2, 11)]

# Use a high contrast color palette from matplotlib's Set1 colormap
cmap = plt.get_cmap("tab10")
colors = cmap.colors

# Noise level: standard deviation of the noise
noise_std = 1.2

# Set figure size so it looks nice on an A4 page (portrait A4 is ~8.27x11.69 inches)
plt.figure(figsize=(3.5, 2.5), dpi=300)

# Plot each scatter group on the same axes, with increased marker size
for i, (y_base, label) in enumerate(zip(horizontal_lines, labels)):
    noise = np.random.normal(0, noise_std, size=x.shape)
    a = -y_base / noise_std
    # b can be infinity (np.inf) so there's no upper limit.
    noise = truncnorm.rvs(a, np.inf, loc=0, scale=noise_std, size=x.shape)
    y = y_base + noise
    # y = np.clip(y, 0, None)  # forces all values to be at least 0
    plt.scatter(x, y, s=2, color=colors[i % len(colors)], label=label)

plt.yticks([i for i in range(0, 160, 10)])
plt.xlabel('Payload (KB)', fontsize=6)
plt.xticks(fontsize=6)
plt.yticks(fontsize=6)
plt.grid(True, linewidth=0.5, color='gray', alpha=0.4, axis="y")
plt.ylabel('Average response time (ms)', fontsize=6)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.title('', fontsize=8)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=1, borderaxespad=0., fontsize=6)
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)



plt.tight_layout()
plt.savefig("scatter_plot.pdf")
plt.show()