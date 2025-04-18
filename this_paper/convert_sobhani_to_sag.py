import random
import math
import os
import csv
import numpy as np
from tqdm import tqdm

def random_permutation(a, b):
    return random.sample(range(a, b + 1), b - a + 1)

def lcm(numbers):
    result = numbers[0]
    for num in numbers[1:]:
        result = math.lcm(result, num)
    return result

def convert_file_to_tasksets_odd_chains(filename):
    '''
    Converts an input file that is used by PWA_CD.m
    to a Python list of lists, that can be then used
    to generate csv files for the SAG.

    This function doesn't assume that all chains have the same length,
    as convert_file_to_tasksets() does. So it also outputs a list
    of chain lengths.
    '''
    tasksets = []      # This will hold all task sets.
    current_taskset = []  # List for the current task set.
    current_chain = []    # List for the current chain.
    current_chain_id = None  # To keep track of which chain we are processing.
    curr_chain_len = 0
    chain_lengths = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines.
            if not line:
                continue

            # Check for task-set separator.
            if line == "-":
                # End of a task set.
                if current_chain:  # If there's a chain being built, finish it.
                    current_taskset.extend(current_chain)
                    curr_chain_len += 1
                    chain_lengths.append(curr_chain_len)
                    
                    curr_chain_len = 0
                    current_chain = []
                    current_chain_id = None
                if current_taskset:
                    tasksets.append((current_taskset, chain_lengths))
                    chain_lengths = []
                # Reset for the next task set.
                current_taskset = []
                current_chain = []
                current_chain_id = None
                curr_chain_len = 0
                continue

            # Process a line representing a task.
            parts = line.split()
            if len(parts) < 5:
                # Not enough columns; skip this line.
                continue

            # Parse values. (We assume values are integers.)
            period = int(parts[0])
            exec_time = int(parts[1])
            # We ignore parts[2] (deadline) and parts[3] (task id)
            chain_id = int(parts[4])

            # If we are starting a new chain or this line belongs to a different chain.
            if current_chain_id is None or chain_id != current_chain_id:
                # If we already have a chain under construction, finish it.
                if current_chain:
                    current_taskset.extend(current_chain)
                    curr_chain_len += 1
                    chain_lengths.append(curr_chain_len)
                    curr_chain_len = 0
                # Start a new chain.
                # The chain always starts with the period.
                current_chain = [period, exec_time]
                current_chain_id = chain_id
            else:
                # Same chain: just append the execution time.
                current_chain.append(exec_time)
                curr_chain_len += 1

        # End-of-file: finish up any remaining chain or task set.
        if current_chain:
            current_taskset.extend(current_chain)
            curr_chain_len += 1
            chain_lengths.append(curr_chain_len)
        if current_taskset:
            tasksets.append((current_taskset, chain_lengths))
            chain_lengths = []

    return tasksets

def generate_csv_n_task_sets_odd_chains(input = "", output = ""):
    '''
    Generates CSVs that can be processed by the SAG framework for tasks with the following specifications:
    - The generated tasks that are used to generate jobs reflect ROS callback chains
    - All generated task sets have the same number of chains and the same number of callbacks per chain
    - The chains are INDEPENDENT
    - All tasks have NO execution time variability, i.e. BCET == WCET
    - All tasks have NO release jitter, i.e. r_min[i] == r_max[i] for all jobs i
    - U represents the total utilization across all tasks
        - U is split among chains, and periods are randomly picked for each chain
        - Then the WCET of a chain is calculated, and this is split among the tasks of the chain

    There are 2 CSVs per task set:
    - A CSV with all jobs, and their timing and priority parameters
    - A CSV with the precedence constraints between jobs
    '''
    # nrof_chains also corresponds to the number of timers, since there is 1 timer per chain

    task_set_idx = 0
    task_sets = convert_file_to_tasksets_odd_chains(input)
    
    for task_set in task_sets:
        ts, chain_lengths = task_set
        nrof_tasks = sum(chain_lengths)
        nrof_chains = len(chain_lengths)

        periods = []
        period_idx = 0
        for chain_length in chain_lengths:
            periods.append(ts[period_idx])
            period_idx += chain_length + 1
        periods_extended = [period for i in range(len(periods)) for period in [periods[i]] * chain_lengths[i]]

        hyperperiod = lcm(periods)

        period_idx = 0
        chain_idx = 0
        wcets = []
        for i in range(0, len(ts)):
            if i < period_idx:
                wcets.append(ts[i])
            elif i == period_idx:
                # print(period_idx, chain_idx)
                period_idx += chain_lengths[chain_idx] + 1
                chain_idx += 1

        priority = [0 for i in range(nrof_tasks)]
        timer_priorities = random_permutation(1, nrof_chains)
        subs_prorities = random_permutation(nrof_chains + 1, nrof_tasks)

        period_idx = 0
        timer_index= 0
        subs_index = 0
        for i in range(0, nrof_tasks):
            if i == period_idx:
                priority[i] = timer_priorities[timer_index]
                period_idx += chain_lengths[timer_index]
                timer_index += 1
            else:
                priority[i] = subs_prorities[subs_index]
                subs_index += 1
        
        period_idx = 0
        timer_index = 0
        pred = [0 for i in range(nrof_tasks)]
        for i in range(0, nrof_tasks):
            if i == period_idx:
                period_idx += chain_lengths[timer_index]
                timer_index += 1
                continue
            else:
                pred[i] = priority[i - 1]
        
        tasks = list(zip(priority, wcets, pred, periods_extended))
        # print(tasks)

        tasks_by_p = sorted(tasks, key=lambda t: t[0])

        jobs_csv_name = os.path.join(output, f"task_set_{task_set_idx}.csv")
        pred_csv_name = os.path.join(output, f"pred_{task_set_idx}.csv")
        
        with open(jobs_csv_name, "+w", newline='') as f, open(pred_csv_name, "+w", newline='') as g:
            writer = csv.writer(f)
            writer2 = csv.writer(g)
            first_row = ["Task ID","Job ID","Arrival min","Arrival max","Cost min","Cost max","Deadline","Priority"]
            first_row2 = ["PredTaskID", "PredJobID", "SuccTaskID", "SuccJobID"]
            writer.writerow(first_row)
            writer2.writerow(first_row2)

            job_id = 1
            for i in range(0, nrof_tasks):
                task_priority = tasks_by_p[i][0]
                wcet = tasks_by_p[i][1]
                pred = tasks_by_p[i][2]
                bcet = wcet // 2 ################################ BCET = WCET / 2
                task_period = tasks_by_p[i][3]
                # INF = int(1e12)
                # deadline = INF
                nrof_jobs_of_task = hyperperiod // task_period

                pred_job_idx = -1
                if i >= nrof_chains:
                    pred_job_idx = 1
                    # All jobs with higher priority than the jobs of the predecessor
                    for j in range(0, pred - 1): # pred - 1 because the priorities/ids start from 1, not from 0 
                        pred_job_idx += hyperperiod // tasks_by_p[j][3] # the period 
                
                for j in range(nrof_jobs_of_task):
                    r_min = j * task_period
                    r_max = r_min
                    deadline = r_min + task_period
                    row = [task_priority, job_id, r_min, r_max, bcet, wcet, deadline, job_id]
                    writer.writerow(row)

                    if pred_job_idx > 0: # If the job has a predecessor, i.e. not timer
                        row2 = [pred, pred_job_idx, task_priority, job_id]
                        writer2.writerow(row2)
                        pred_job_idx += 1
                    # print(f"Task id: {task_priority}, job id: {job_id}, ri_min: {r_min}, ri_max: {r_max}, Ci_min: {bcet}, Ci_max: {wcet}, p: {job_id}")
                    job_id += 1

        task_set_idx +=1

def convert_file_to_tasksets(filename):
    '''
    Converts an input file that is used by PWA_CD.m
    to a Python list of lists, that can be then used
    to generate csv files for the SAG.
    '''
    tasksets = []      # This will hold all task sets.
    current_taskset = []  # List for the current task set.
    current_chain = []    # List for the current chain.
    current_chain_id = None  # To keep track of which chain we are processing.

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines.
            if not line:
                continue

            # Check for task-set separator.
            if line == "-":
                # End of a task set.
                if current_chain:  # If there's a chain being built, finish it.
                    current_taskset.extend(current_chain)
                    current_chain = []
                    current_chain_id = None
                if current_taskset:
                    tasksets.append(current_taskset)
                # Reset for the next task set.
                current_taskset = []
                current_chain = []
                current_chain_id = None
                continue

            # Process a line representing a task.
            parts = line.split()
            if len(parts) < 5:
                # Not enough columns; skip this line.
                continue

            # Parse values. (We assume values are integers.)
            period = int(parts[0])
            exec_time = int(parts[1])
            # We ignore parts[2] (deadline) and parts[3] (task id)
            chain_id = int(parts[4])

            # If we are starting a new chain or this line belongs to a different chain.
            if current_chain_id is None or chain_id != current_chain_id:
                # If we already have a chain under construction, finish it.
                if current_chain:
                    current_taskset.extend(current_chain)
                # Start a new chain.
                # The chain always starts with the period.
                current_chain = [period, exec_time]
                current_chain_id = chain_id
            else:
                # Same chain: just append the execution time.
                current_chain.append(exec_time)

        # End-of-file: finish up any remaining chain or task set.
        if current_chain:
            current_taskset.extend(current_chain)
        if current_taskset:
            tasksets.append(current_taskset)

    return tasksets

def generate_csv_n_task_sets(nrof_task_sets: int, U: float, nrof_chains: int, nrof_callbacks_per_chain: int, input = "", output = ""):
    '''
    Generates CSVs that can be processed by the SAG framework for tasks with the following specifications:
    - The generated tasks that are used to generate jobs reflect ROS callback chains
    - All generated task sets have the same number of chains and the same number of callbacks per chain
    - The chains are INDEPENDENT
    - All tasks have NO execution time variability, i.e. BCET == WCET
    - All tasks have NO release jitter, i.e. r_min[i] == r_max[i] for all jobs i
    - U represents the total utilization across all tasks
        - U is split among chains, and periods are randomly picked for each chain
        - Then the WCET of a chain is calculated, and this is split among the tasks of the chain

    There are 2 CSVs per task set:
    - A CSV with all jobs, and their timing and priority parameters
    - A CSV with the precedence constraints between jobs
    '''
    # nrof_chains also corresponds to the number of timers, since there is 1 timer per chain

    nrof_tasks = nrof_chains * nrof_callbacks_per_chain
    task_set_idx = 1
    task_sets = convert_file_to_tasksets(input)

    for task_set in tqdm(task_sets, desc="Task Sets"):
        periods = [task_set[i] for i in range(0, len(task_set), nrof_callbacks_per_chain + 1)]
        hyperperiod = lcm(periods)

        periods_extended = [period for i in range(len(periods)) for period in [periods[i]] * nrof_callbacks_per_chain]
        wcets = [task_set[i] for i in range(0, len(task_set)) if i % (nrof_callbacks_per_chain + 1) != 0]
        priority = [0 for i in range(nrof_tasks)]
        timer_priorities = random_permutation(1, nrof_chains)
        subs_prorities = random_permutation(nrof_chains + 1, nrof_tasks)

        timer_index= 0
        subs_index = 0
        for i in range(0, nrof_tasks):
            if i % nrof_callbacks_per_chain == 0:
                priority[i] = timer_priorities[timer_index]
                timer_index += 1
            else:
                priority[i] = subs_prorities[subs_index]
                subs_index += 1
        
        pred = [0 for i in range(nrof_tasks)]
        for i in range(0, nrof_tasks):
            if i % nrof_callbacks_per_chain == 0:
                continue
            else:
                pred[i] = priority[i - 1]
        
        tasks = list(zip(priority, wcets, pred, periods_extended))
        # print(tasks)
        tasks_by_p = sorted(tasks, key=lambda t: t[0])

        jobs_csv_name = os.path.join(output, f"task_set_{task_set_idx}.csv")
        pred_csv_name = os.path.join(output, f"pred_{task_set_idx}.csv")
        
        with open(jobs_csv_name, "+w", newline='') as f, open(pred_csv_name, "+w", newline='') as g:
            writer = csv.writer(f)
            writer2 = csv.writer(g)
            first_row = ["Task ID","Job ID","Arrival min","Arrival max","Cost min","Cost max","Deadline","Priority"]
            first_row2 = ["PredTaskID", "PredJobID", "SuccTaskID", "SuccJobID"]
            writer.writerow(first_row)
            writer2.writerow(first_row2)

            job_id = 1
            for i in tqdm(range(nrof_tasks), desc="Tasks", leave=False):
                task_priority = tasks_by_p[i][0]
                wcet = tasks_by_p[i][1]
                pred = tasks_by_p[i][2]
                # bcet = max(wcet // 2, 1)
                bcet = wcet
                task_period = tasks_by_p[i][3]
                # INF = int(1e12)
                # deadline = INF
                nrof_jobs_of_task = hyperperiod // task_period

                pred_job_idx = -1
                if i >= nrof_chains:
                    pred_job_idx = 1
                    # All jobs with higher priority than the jobs of the predecessor
                    for j in range(0, pred - 1): # pred - 1 because the priorities/ids start from 1, not from 0 
                        pred_job_idx += hyperperiod // tasks_by_p[j][3] # the period 
                
                for j in range(nrof_jobs_of_task):
                    r_min = j * task_period
                    r_max = r_min
                    deadline = r_min + task_period
                    row = [task_priority, job_id, r_min, r_max, bcet, wcet, deadline, job_id]
                    writer.writerow(row)

                    if pred_job_idx > 0: # If the job has a predecessor, i.e. not timer
                        row2 = [pred, pred_job_idx, task_priority, job_id]
                        writer2.writerow(row2)
                        pred_job_idx += 1
                    # print(f"Task id: {task_priority}, job id: {job_id}, ri_min: {r_min}, ri_max: {r_max}, Ci_min: {bcet}, Ci_max: {wcet}, p: {job_id}")
                    job_id += 1

        task_set_idx +=1

def generate_data_SobhaniFigure9():
    # path_in = "/home/radu/repos/sag-ros-experiments/data/SobhaniExp/Fig9/tasksets_nrofjobs_max_5k"
    # path_in = "/home/radu/repos/sag-ros-experiments/SAG_input_SobhaniFig9_200sets"
    # path_in = "/home/radu/repos/sag-ros-experiments/Sobhani_input_Fig9_UUdiscard"
    path_in = "/home/radu/repos/sag-ros-experiments/Sobhani_input_Fig9_logUniform"
    path_out = f"./SAG_input_Fig9_logUniform_BCET=WCET"
    nrof_task_sets = 200
    nrof_chains = 5
    nrof_callbacks_per_chain = 10

    values = np.arange(0.8, 4.1, 0.4)
    values = [round(v, 1) for v in values] 

    for U in values:
        print(f"Generating for U={U}")
        # file_in = os.path.join(path_in, f"tasksets_util_{U}.txt")
        file_in = os.path.join(path_in, f"tasksets_{U}.txt")
        folder_out = os.path.join(path_out, f"tasksets_{U}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets(nrof_task_sets, U, nrof_chains, nrof_callbacks_per_chain, file_in, folder_out)

def generate_data_SobhaniFigure10():
    path_in = "/home/radu/repos/sag-ros-experiments/data/SobhaniExp/Fig10/tasksets_util_1.0.txt"
    path_out = f"./SAG_input_SobhaniFig10"
    nrof_task_sets = 1000
    nrof_chains = 5
    nrof_callbacks_per_chain = 10
    U = 1.0

    folder_out = os.path.join(path_out, f"tasksets_{U}")
    os.makedirs(folder_out, exist_ok=True) 
    generate_csv_n_task_sets(nrof_task_sets, U, nrof_chains, nrof_callbacks_per_chain, path_in, folder_out)

def generate_data_SobhaniFigure11():
    path_in = "/home/radu/repos/sag-ros-experiments/data/SobhaniExp/Fig11"
    path_out = f"./SAG_input_SobhaniFig11"
    nrof_task_sets = 1000
    nrof_callbacks_per_chain = 10
    U = 1.0

    for nrof_chains in range(1, 11):
        print(f"Generating for {nrof_chains} chains")
        file_in = os.path.join(path_in, f"tasksets_cn_{nrof_chains}.txt")
        folder_out = os.path.join(path_out, f"tasksets_{nrof_chains}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets(nrof_task_sets, U, nrof_chains, nrof_callbacks_per_chain, file_in, folder_out)

def generate_data_JiangFigure6():
    path_in = ""
    path_out_main = f"./SAG_input_JiangFig6_BCET"

    path_out = f"./{path_out_main}/vary_Unorm"
    values = np.arange(0.1, 1.0, 0.1)
    values = [round(v, 1) for v in values]
    for Unorm in values:
        path_in = fr"/home/radu/repos/sag-ros-experiments/data/JiangExp/Figure6/InputToSobhani/vary_Unorm/tasksets_unorm_{Unorm}.txt"
        folder_out = os.path.join(path_out, f"tasksets_{Unorm}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets_odd_chains(path_in, folder_out)
    
    path_out = f"./{path_out_main}/vary_n"
    for n in range(2, 9):
        path_in = fr"/home/radu/repos/sag-ros-experiments/data/JiangExp/Figure6/InputToSobhani/vary_n/tasksets_n_{n}.txt"
        folder_out = os.path.join(path_out, f"tasksets_{n}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets_odd_chains(path_in, folder_out)
    
    path_out = f"./{path_out_main}/vary_b"
    for b in range(2, 7):
        path_in = fr"/home/radu/repos/sag-ros-experiments/data/JiangExp/Figure6/InputToSobhani/vary_b/tasksets_b_{b}.txt"
        folder_out = os.path.join(path_out, f"tasksets_{b}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets_odd_chains(path_in, folder_out)
    
    path_out = f"./{path_out_main}/vary_m"
    for m in range(2, 9):
        path_in = fr"/home/radu/repos/sag-ros-experiments/data/JiangExp/Figure6/InputToSobhani/vary_m/tasksets_m_{m}.txt"
        folder_out = os.path.join(path_out, f"tasksets_{m}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets_odd_chains(path_in, folder_out)

def generate_data_Sobhani_b():
    path_in = "/home/radu/repos/sag-ros-experiments/Sobhani_input_b_200sets"
    path_out = f"./SAG_input_Sobhani_b"
    nrof_task_sets = 200
    nrof_chains = 5
    U = 1.0

    for nrof_callbacks_per_chain in range(2, 21):
        print(f"Generating for {nrof_callbacks_per_chain} tasks per chain")
        file_in = os.path.join(path_in, f"tasksets_{nrof_callbacks_per_chain}.txt")
        folder_out = os.path.join(path_out, f"tasksets_{nrof_callbacks_per_chain}")
        os.makedirs(folder_out, exist_ok=True) 
        generate_csv_n_task_sets(nrof_task_sets, U, nrof_chains, nrof_callbacks_per_chain, file_in, folder_out)

if __name__ == "__main__":
    # path_in = "/home/radu/repos/sag-ros-experiments/tasksets.txt"
    # folder_out = "./exam"
    # generate_csv_n_task_sets_odd_chains(path_in, folder_out)
    # generate_data_JiangFigure6()
    generate_data_SobhaniFigure9()
    # generate_data_Sobhani_b()