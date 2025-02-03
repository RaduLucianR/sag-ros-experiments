from drs import drs 
import random
import math
import csv
import os
import numpy as np

def snap_period(period_ns):
    """
    Snap a given period (in ns) to an allowed period.
    
    Here, the allowed periods (in ms) are all multiples of 5 in the interval [50, 200].
    For example: 50, 55, 60, 65, …, 200 ms.
    The function returns the snapped period in ns.
    """
    # Convert period from nanoseconds to milliseconds.
    period_ms = period_ns / 1e6

    # Clip period_ms to the desired interval [50, 200] ms.
    period_ms = max(50, min(period_ms, 200))

    # Define the allowed set with finer granularity: every 5 ms between 50 and 200.
    allowed = list(range(50, 201, 10))
    
    # Find the allowed value that is closest to period_ms.
    snapped_ms = min(allowed, key=lambda v: abs(v - period_ms))
    
    # Convert back to nanoseconds.
    return int(snapped_ms * 1e6)

def random_permutation(a, b):
    return random.sample(range(a, b + 1), b - a + 1)

def lcm(numbers):
    result = numbers[0]
    for num in numbers[1:]:
        result = math.lcm(result, num)
    return result

def float_list_to_ns(values, scale=1e9):
    ns_values = [int(round(v * scale)) for v in values]
    target = int(round(sum(values) * scale))
    discrepancy = target - sum(ns_values)
    ns_values[0] += discrepancy

    return ns_values

def period_distribution():
    scale = 1e9
    return int(round(random.uniform(0.05 * scale, 0.2 * scale))) # seconds to nanoseconds. These numbers are 50ms, 200ms

def generate_task_set(U, k, chain_length_range):
    """
    Generate synthetic task sets with k chains where the total utilization sums to U.
    Each chain:
      - Gets a utilization value from the DRS partition: drs(n=k, sumu=U)
      - Has a randomly chosen length between chain_length_range[0] and chain_length_range[1]
      - Has a first (periodic) task with a generated period T; the total execution time for the chain is u_i * T
      - Splits its total execution time among its tasks using drs.
    
    Parameters:
      U: Total utilization over all chains.
      k: Number of chains.
      chain_length_range: Tuple (min_length, max_length) for the number of tasks per chain.
      
    Returns:
      A list of chains, where each chain is a list of tasks (dictionaries).
    """
    chain_utils = drs(n = k, sumu = U) # Partition overall utilization among k chains using drs
    
    task_set = []
    
    # Iterate over chains
    for i in range(k):
        L = random.randint(chain_length_range[0], chain_length_range[1]) # Choose the number of tasks for chain i randomly within the provided range.
        T = snap_period(period_distribution()) # Generate a period for the first (periodic) task in this chain.
        total_exec = chain_utils[i] * T # Compute the total execution time required for chain i
        total_exec = int(round(total_exec)) # Convert to int nanoseconds
        task_execs = drs(n = L, sumu = total_exec) # Partition total_exec among L tasks using drs.
        task_execs = [int(round(x)) for x in task_execs]
        discrepancy = total_exec - sum(task_execs)
        task_execs[0] += discrepancy 
        chain = [T, *task_execs]

        for element in chain:
            task_set.append(element)
    
    return task_set

def generate_n_task_sets(nrof_sets: int, U: float, nrof_chains: int, nrof_callbacks_per_chain: int):
    '''
    Generates n task sets of nrof_chains INDEPENDENT chains.
    '''
    chain_length = nrof_callbacks_per_chain
    task_sets = []
    nrof_jobs_interval = (500, 1000)

    for s in range(nrof_sets):
        synthetic_task_set = generate_task_set(U, nrof_chains, (chain_length, chain_length)) # given nrof_chains chains
        periods = [synthetic_task_set[i] for i in range(0, len(synthetic_task_set), nrof_callbacks_per_chain + 1)]
        hyperperiod = lcm(periods)
        nrof_jobs = sum([(hyperperiod // period )* chain_length for period in periods])

        while nrof_jobs < nrof_jobs_interval[0] or nrof_jobs > nrof_jobs_interval[1]:
            synthetic_task_set = generate_task_set(U, nrof_chains, (chain_length, chain_length))
            periods = [synthetic_task_set[i] for i in range(0, len(synthetic_task_set), nrof_callbacks_per_chain + 1)]
            hyperperiod = lcm(periods)
            nrof_jobs = sum([(hyperperiod // period) * chain_length for period in periods])

        task_sets.append(synthetic_task_set)

        # print("--- Task set ----")
        # for i in range(0, len(synthetic_task_set), chain_length + 1):
        #     wcets = synthetic_task_set[i + 1: i + 1 + chain_length]
        #     print(f"Chain with period {synthetic_task_set[i]} and WCETs: {wcets}, Total WCET of chain: {sum(wcets)}")
    
    return task_sets


def generate_csv_n_task_sets(nrof_task_sets: int, U: float, nrof_chains: int, nrof_callbacks_per_chain: int, path = ""):
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
    task_sets = generate_n_task_sets(nrof_task_sets, U, nrof_chains, nrof_callbacks_per_chain)

    for task_set in task_sets:
        periods = [task_set[i] for i in range(0, len(task_set), nrof_callbacks_per_chain + 1)]
        hyperperiod = lcm(periods)
        nrof_jobs = sum([(hyperperiod // period)* nrof_callbacks_per_chain for period in periods])

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

        jobs_csv_name = os.path.join(path, f"task_set_{task_set_idx}.csv")
        pred_csv_name = os.path.join(path, f"pred_{task_set_idx}.csv")
        
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
                bcet = wcet
                task_period = tasks_by_p[i][3]
                INF = int(1e12)
                deadline = INF
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
                    row = [task_priority, job_id, r_min, r_max, bcet, wcet, deadline, job_id]
                    writer.writerow(row)

                    if pred_job_idx > 0: # If the job has a predecessor, i.e. not timer
                        row2 = [pred, pred_job_idx, task_priority, job_id]
                        writer2.writerow(row2)
                        pred_job_idx += 1
                    # print(f"Task id: {task_priority}, job id: {job_id}, ri_min: {r_min}, ri_max: {r_max}, Ci_min: {bcet}, Ci_max: {wcet}, p: {job_id}")
                    job_id += 1

        task_set_idx +=1

def sobhaniFig9(path):
    '''
    Generates synthetic task sets that are used for Figure 9 of the paper:

    H. Sobhani, H. Choi and H. Kim, 
    "Timing Analysis and Priority-driven Enhancements of ROS 2 Multi-threaded Executors," 
    2023 IEEE 29th Real-Time and Embedded Technology and Applications Symposium (RTAS), 
    San Antonio, TX, USA, 2023, pp. 106-118, doi: 10.1109/RTAS58335.2023.00016.
    keywords: {Job shop scheduling;Service robots;Operating systems;Interference;
    Solids;Real-time systems;Behavioral sciences}, 
    '''
    nrof_task_sets = 1000
    nrof_chains = 5
    nrof_callbacks_per_chain = 10

    values = np.arange(0.8, 4.1, 0.4)
    values = [round(v, 1) for v in values] 

    for U in values:
        subfolder = os.path.join(path, f"util{U}")
        os.makedirs(subfolder, exist_ok=True) 
        generate_csv_n_task_sets(nrof_task_sets, U, nrof_chains, nrof_callbacks_per_chain, subfolder)


if __name__ == '__main__':
    sobhaniFig9("./sobhani/")