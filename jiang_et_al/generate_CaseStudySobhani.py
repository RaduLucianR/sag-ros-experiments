from JRTA import *

def sobhani_case_study():
    # sobhani_case_study_fig4_task_set = [{1: 50, 2: 50, 3: 100, 4: 200}, {1: 6, 2: 14, 3: 35.8, 4: 130}, {1: 3.0, 2: 4.1, 3: 12.4, 4: 23.0}]
    sobhani_case_study_actual_values = [{1: 50000, 2: 50000, 3: 100000, 4: 200000}, # Periods of chains
                                        {1: 6242,  2: 17914, 3: 35279, 4: 126159}, # Total Execution time of each *CHAIN*
                                        {1: 3119, 2: 5928, 3: 12088, 4: 22069} # Execution time of the *last callback* in each chain!!!
                                        ]
    print(jiang_on_tasksets([sobhani_case_study_actual_values], 2)) # 2 executor-threads
    print(jiang_on_tasksets([sobhani_case_study_actual_values], 4)) # 4 executor-threads

sobhani_case_study()