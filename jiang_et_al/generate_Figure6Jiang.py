import csv
import numpy as np
from JRTA import *

import sys
sys.path.insert(0, "/home/radu/repos/sag-ros-experiments/this_paper")
from generate_data_for_Jiang_synthetic import generate_data_for_Fig6_Jiang

def jiang_Figure6a():
    values = np.arange(0.1, 1.0, 0.1)
    values = [round(v, 1) for v in values]
    results = []
    m = 4 # Number of executor-threads

    for Unorm in values:
        path = fr"/home/radu/repos/sag-ros-experiments/JiangFig6/vary_Unorm/tasksets_unorm_{Unorm}.txt"
        tasksets = convert_sobhani_syntethic_odd_to_jiang(path)
        r = jiang_on_tasksets(tasksets, m)[0]
        print(f"Unorm={Unorm}, schedulability={r}")
        results.append((Unorm, r))

    with open("Figure6a_data_Jiang.csv", "w+", newline="") as f:
        writer = csv.writer(f)

        for elem in results:
            writer.writerow([elem[0], elem[1]])

def jiang_Figure6b():
    m = 4 # Number of executor-threads
    results = []

    for n in range(2, 9):
        path = fr"/home/radu/repos/sag-ros-experiments/JiangFig6/vary_n/tasksets_n_{n}.txt"
        tasksets = convert_sobhani_syntethic_odd_to_jiang(path)
        r = jiang_on_tasksets(tasksets, m)[0]
        print(f"n={n}, schedulability={r}")
        results.append((n, r))

    with open("Figure6b_data_Jiang.csv", "w+", newline="") as f:
        writer = csv.writer(f)

        for elem in results:
            writer.writerow([elem[0], elem[1]])

def jiang_Figure6c():
    m = 4 # Number of executor-threads
    results = []

    for b in range(2, 7):
        path = fr"/home/radu/repos/sag-ros-experiments/JiangFig6/vary_b/tasksets_b_{b}.txt"
        tasksets = convert_sobhani_syntethic_odd_to_jiang(path)
        r = jiang_on_tasksets(tasksets, m)[0]
        print(f"b={b}, schedulability={r}")
        results.append((b, r))

    with open("Figure6c_data_Jiang.csv", "w+", newline="") as f:
        writer = csv.writer(f)

        for elem in results:
            writer.writerow([elem[0], elem[1]])

def jiang_Figure6f():
    results = []

    for m in range(2, 9):
        path = fr"/home/radu/repos/sag-ros-experiments/JiangFig6/vary_m/tasksets_m_{m}.txt"
        tasksets = convert_sobhani_syntethic_odd_to_jiang(path)
        r = jiang_on_tasksets(tasksets, m)[0]
        print(f"m={m}, schedulability={r}")
        results.append((m, r))

    with open("Figure6f_data_Jiang.csv", "w+", newline="") as f:
        writer = csv.writer(f)

        for elem in results:
            writer.writerow([elem[0], elem[1]])

if __name__ == "__main__":
    generate_data_for_Fig6_Jiang()
    jiang_Figure6a()
    jiang_Figure6b()
    jiang_Figure6c()
    jiang_Figure6f()