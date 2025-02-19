from JRTA import *

path_to_input_file = r"C:\Users\20191039\Desktop\repos\sag-ros-experiments\data\SobhaniExp\Fig10\tasksets_util_1.0.txt"
tasksets = convert_sobhani_synthetic_to_jiang(5, 10, path_to_input_file)
results = []

for m in range(1, 16 + 1):
    ratio = jiang_on_tasksets(tasksets, m)[0]
    print(f"For m={m} threads we have a schedulability ratio of {ratio}")
    results.append((m, ratio))

with open("Figure10_data_Jiang.csv", "w+", newline="") as f:
    writer = csv.writer(f)

    for elem in results:
        writer.writerow([elem[0], elem[1]])