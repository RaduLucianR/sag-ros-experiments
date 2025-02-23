import csv
import os

def augment_execution_times(path):
    filename = os.path.basename(path) 
    directory = os.path.dirname(path)
    first_row = ""
    rows = []

    # Step 1: Read the CSV file into a list
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        first_row = next(reader)

        for row in reader:
            rows.append(row)

    ROS_overhead = 7000 # microseconds, so 10ms

    for row in rows:
        C_max = int(row[5]) + ROS_overhead
        row[5] = C_max

    # Step 2: Write the updated data back to the CSV file
    output_path = os.path.join(directory, f"aug_{ROS_overhead//1000}ms_{filename}")
    print(output_path)
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(first_row)
        writer.writerows(rows)

augment_execution_times("/home/radu/repos/sag-ros-experiments/data/JiangExp/CaseStudy1/InputToSAG/BCEThalf/task_set_JiangCaseStudy_BCEThalf.csv")