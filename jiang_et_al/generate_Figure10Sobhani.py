from JRTA import *

tasksets = convert_sobhani_synthetic_to_jiang(5, 10, r"C:\Users\20191039\Desktop\repos\sag-ros-experiments\sobhani_et_al\tasksets_util_1.0.txt")
results = []

for m in range(1, 16 + 1):
    ratio = jiang_on_tasksets(tasksets, m)[0]
    print(f"For m={m} threads we have a schedulability ratio of {ratio}")
    results.append((m, ratio))

with open("Figure10_data.csv", "w+", newline="") as f:
    writer = csv.writer(f)

    for elem in results:
        writer.writerow([elem[0], elem[1]])