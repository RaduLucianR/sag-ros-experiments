from JRTA import *

results = []

def jiang_case_study_1():
    ratio, rt = jiang_on_tasksets([[{1: 100, 2: 100, 3: 160}, {1: 31.0, 2: 45.1, 3: 27.2}, {1: 7.9, 2: 6.6, 3: 7.9}]], 2)
    results = rt
    print(ratio)

    with open("JiangCaseStudy1_data.csv", "w+", newline="") as f:
        writer = csv.writer(f)

        for elem in results:
            writer.writerow([*elem])

jiang_case_study_1()