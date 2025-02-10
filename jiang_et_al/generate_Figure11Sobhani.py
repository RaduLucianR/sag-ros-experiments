from JRTA import *

m = 4
results = []

for nrof_chains in range(1, 10 + 1):
    path = fr"C:\Users\20191039\Desktop\repos\sag-ros-experiments\sobhani_et_al\tasksets_cn_{nrof_chains}.txt"
    tasksets = convert_sobhani_synthetic_to_jiang(nrof_chains, 10, path)
    ratio = jiang_on_tasksets(tasksets, m)[0]
    print(f"For {nrof_chains} chains we have a schedulability ratio of {ratio}")
    results.append((nrof_chains, ratio))

with open("Figure11_data.csv", "w+", newline="") as f:
    writer = csv.writer(f)

    for elem in results:
        writer.writerow([elem[0], elem[1]])