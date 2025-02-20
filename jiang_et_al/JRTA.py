import math
import csv
import numpy as np
from scipy.optimize import fixed_point

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

def convert_sobhani_syntethic_odd_to_jiang(input):
    tasksets = convert_file_to_tasksets_odd_chains(input)
    result = []

    for taskset in tasksets:
        ts = taskset[0]
        chain_lengths = taskset[1]
        nrof_chains = len(chain_lengths)

        periods = {}
        exec_times = {}
        exec_time_last_cb = {}

        for chain in range(1, nrof_chains + 1):
            periods[chain] = ts[(chain - 1) * (chain_lengths[chain - 1] + 1)]
            exec_times[chain] = sum(ts[((chain - 1) * (chain_lengths[chain - 1] + 1) + 1):(chain * (chain_lengths[chain - 1] + 1))])
            exec_time_last_cb[chain] = ts[chain * (chain_lengths[chain - 1] + 1) - 1]
        
        one = [periods, exec_times, exec_time_last_cb]
        result.append(one)
    
    return result

def convert_sobhani_synthetic_to_jiang(nrof_chains, nrof_callbacks_per_chain, input):
    tasksets = convert_file_to_tasksets(input)
    result = []

    for taskset in tasksets:
        periods = {}
        exec_times = {}
        exec_time_last_cb = {}

        for chain in range(1, nrof_chains + 1):
            periods[chain] = taskset[(chain - 1) * (nrof_callbacks_per_chain + 1)]
            exec_times[chain] = sum(taskset[((chain - 1) * (nrof_callbacks_per_chain + 1) + 1):(chain * (nrof_callbacks_per_chain + 1))])
            exec_time_last_cb[chain] = taskset[chain * (nrof_callbacks_per_chain + 1) - 1]
        
        ts = [periods, exec_times, exec_time_last_cb]
        result.append(ts)
    
    return result

def jiang_on_tasksets(tasksets, m):
    '''
    Implements Theorem 1 from:
    Xu Jiang, Dong Ji, Nan Guan, Ruoxiang Li, Yue Tang, and Yi Wang. 
    Real-time scheduling and analysis of processing chains on multi-threaded executor in ros 2. 
    In 2022 IEEE Real-TimeSystems Symposium (RTSS)
    '''
    taskset_nr = 1
    sched_task_sets = 0
    reponse_times_per_chain = []

    for taskset in tasksets:
        # print(f"Task set {taskset_nr}")
        schedulable = True
        periods = taskset[0]
        nrof_chains = len(periods)
        exec_times = taskset[1]
        exec_time_last_cb = taskset[2]
        
        for chain in range(1, nrof_chains + 1):
            def n(k, L):
                return math.ceil((L - exec_times[k]) / periods[k]) + 1

            def W(k, L):
                return (n(k, L)  - 1) * exec_times[k] + min((L - exec_times[k]) % periods[k], exec_times[k])
            
            def theorem1_L(L):
                WorkloadSum = 0
                for i in range(1, nrof_chains):
                    if chain != i:
                        WorkloadSum += W(i, L)
                return exec_times[chain] - exec_time_last_cb[chain] + WorkloadSum / m
            
            try:
                max_interf = fixed_point(theorem1_L, 0, xtol=10-6)
            except RuntimeError:
                print(f"Skipping task set {taskset_nr}, chain {chain}")
                continue

            R = max_interf + exec_time_last_cb[chain]   
            D = periods[chain] # implicit deadline
            reponse_times_per_chain.append((taskset_nr, chain, R, D))

            if R > D:
                schedulable = False
        
        if schedulable:
            sched_task_sets += 1

        taskset_nr += 1

    sched_ratio = sched_task_sets / len(tasksets)
    return sched_ratio, reponse_times_per_chain