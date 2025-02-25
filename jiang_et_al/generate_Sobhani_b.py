from JRTA import *

m = 4
results = []

for nrof_tasks in range(2, 20 + 1):
    path = fr"/home/radu/repos/sag-ros-experiments/Sobhani_input_b_200sets/tasksets_{nrof_tasks}.txt"
    tasksets = convert_sobhani_synthetic_to_jiang(5, nrof_tasks, path)
    ratio = jiang_on_tasksets(tasksets, m)[0]
    print(f"For {nrof_tasks} tasks per chain we have a schedulability ratio of {ratio}")
    results.append((nrof_tasks, ratio))

with open("Figure_b_data.csv", "w+", newline="") as f:
    writer = csv.writer(f)

    for elem in results:
        writer.writerow([elem[0], elem[1]])