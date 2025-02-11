import csv
import numpy as np
from JRTA import *

def sobhani_figure9():
    values = np.arange(0.8, 4.1, 0.4)
    values = [round(v, 1) for v in values]
    results = []

    for U in values:
        path = fr"/home/radu/repos/sag-ros-experiments/data/SobhaniExp/Fig9/tasksets_nrofjobs_max_5k/tasksets_util_{U}.txt"
        tasksets = convert_sobhani_synthetic_to_jiang(5, 10, path)
        r = jiang_on_tasksets(tasksets, 4)[0]
        print(f"U={U}, schedulability={r}")
        results.append((U, r))

    with open("Figure9_data_Jiang.csv", "w+", newline="") as f:
        writer = csv.writer(f)

        for elem in results:
            writer.writerow([elem[0], elem[1]])

sobhani_figure9()