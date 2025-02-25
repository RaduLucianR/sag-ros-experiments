import random
from drs import drs
import os
import math

def sample_period_log_uniform(T_min, T_max, T_g):
    """
    Samples a task period T_i based on a log-uniform distribution.
    
    Parameters:
        T_min (float): Minimum task period.
        T_max (float): Maximum task period.
        T_g (float): Granularity; task periods are multiples of T_g.
    
    Returns:
        float: A sampled task period T_i.
    """
    # Sample r from a uniform distribution between log(T_min) and log(T_max + T_g)
    r = random.uniform(math.log(T_min), math.log(T_max + T_g))
    
    # Compute the task period T_i using the floor operation as described
    T_i = math.floor(math.exp(r) / T_g) * T_g
    return T_i

def round_and_scale(values, target):
    """
    Convert a list of floats (values) that sum to some total into a list of integers
    that sum exactly to target, preserving the relative proportions.
    """
    total = sum(values)
    if total == 0:
        return [0] * len(values)
    scaled = [v / total * target for v in values]
    ints = [int(x) for x in scaled]
    remainder = target - sum(ints)
    # Get fractional remainders
    fractions = [x - int(x) for x in scaled]
    # Distribute the remaining units to parts with largest fractional remainders
    indices = sorted(range(len(values)), key=lambda i: fractions[i], reverse=True)
    for i in range(remainder):
        ints[indices[i]] += 1
    return ints

def partition_integer_min1(E, C):
    """
    Partition an integer E into C positive integers (each at least 1)
    while preserving the proportions given by drs.
    
    The approach is to reserve 1 unit for each task, then partition the remainder
    E - C using drs (and round/scale the resulting floats), finally adding 1 to each part.
    """
    if E < C:
        E = C  # Ensure E is at least C
    remainder = E - C
    if remainder == 0:
        return [1] * C
    # Partition the remainder into C parts (these parts can be zero)
    raw_parts = drs(C, remainder)
    parts = round_and_scale(raw_parts, remainder)
    # Add back the reserved 1 unit for each task
    return [part + 1 for part in parts]

def generate_task_set(U, NC, C):
    """
    Generate one task set with:
      U  : total utilization for the task set,
      NC : number of chains,
      C  : number of tasks per chain.
      
    For each chain:
      - Uses the external drs function to split U into chain utilizations (each ≤ 1).
      - Picks a period randomly from allowed values in [50, 200] (multiples of 50 or 20).
      - Computes the chain's total execution time as period * chain_utilization (rounded to an integer).
      - Partitions the execution time into C positive integers (one per task) while preserving utilization.
    
    Each task is output as a row with:
         period <tab> execution time <tab> deadline (same as period) <tab> task id <tab> chain id.
    A line with a single '-' terminates the task set.
    """
    # Generate NC chain utilizations that sum to U (each ≤ 1)
    # chain_utils = drs(NC, U, [1.0] * NC) ######### For Jiang
    chain_utils = drs(NC, U) ########### For Sobhani
    
    # Allowed periods: numbers in [50,200] that are multiples of 50 or 20.
    # allowed_periods = [50, 60, 80, 100, 120, 140, 150, 160, 180, 200]
    # allowed_periods = [i for i in range(50, 201, 10)]
    # allowed_periods = [i * 100 for i in range(1, 11)]
    nrof_jobs = 0
    periods = []

    while nrof_jobs < 1000 or nrof_jobs > 5000:
        # periods = [random.choice(allowed_periods) for i in range(NC)]
        periods = [sample_period_log_uniform(10000, 100000, 5000) for i in range(NC)] # Log-uniform
        hyperperiod = math.lcm(*periods)
        nrof_jobs = sum([hyperperiod // t * 10 for t in periods])
    
    output_lines = []
    task_id = 1
    
    for chain_index in range(NC):
        # period = random.choice(allowed_periods)
        period = periods[chain_index]
        # Compute chain's total execution time E (as an integer)
        E = int(round(period * chain_utils[chain_index]))
        # Ensure E is at least C so it can be partitioned into C positive integers.
        if E < C:
            E = C
        # Partition E into C positive integers using partition_integer_min1.
        exec_times = partition_integer_min1(E, C)
        for exec_time in exec_times:
            # Each row: period, execution time, deadline (same as period), task id, chain id.
            line = f"{period}\t{exec_time}\t{period}\t{task_id}\t{chain_index+1}"
            output_lines.append(line)
            task_id += 1

    # End the task set with a single '-' line.
    output_lines.append("-")
    return "\n".join(output_lines)

def generate_file(nrof_task_sets, n, b, Unorm, m, filename="tasksets.txt"):
    """
    Generate a file with multiple task sets.
    
    For each task set:
      - NC (number of chains) is randomly chosen from [2, n].
      - C (number of tasks per chain) is randomly chosen from [2, b].
      - m is a random integer from [2, 8] and Upper = m * Unorm.
      - U is a random float from (0, min(Upper, NC)] ensuring no chain utilization exceeds 1.
    
    Each task set is generated by generate_task_set(U, NC, C) and written to the specified file.
    """
    with open(filename, "w") as f:
        for _ in range(nrof_task_sets):
            NC = random.randint(2, n)
            C = random.randint(2, b)
            Upper = m * Unorm
            # U is chosen in (0, U_max] with U_max ensuring each chain's utilization ≤ 1.
            U_max = min(Upper, NC)
            U = random.uniform(0.1, U_max)
            task_set = generate_task_set(U, NC, C)
            f.write(task_set + "\n")

def generate_data_for_Fig6_Jiang():
    # Base configuration:
    nrof_task_sets = 500
    m = 4
    n = 8
    b = 5
    Unorm = 0.3
    g = 0 # Not used here, but it is used in Jiang et al.
    alfa = 0 # Not used here, but it is used in Jiang et al.

    # Vary Unorm
    output_folder = "./JiangFig6/vary_Unorm"
    os.makedirs(output_folder)
    for i in range(1, 10):
        new_Unorm = i / 10
        output_file = f"tasksets_unorm_{new_Unorm}.txt"
        output_file = os.path.join(output_folder, output_file)
        generate_file(nrof_task_sets, n, b, new_Unorm, m, output_file)
        print(f"Task sets have been generated in {output_file}")
    
    # Vary n, i.e., number of chains
    output_folder = "./JiangFig6/vary_n"
    os.makedirs(output_folder)
    for i in range(2, 9):
        new_n = i
        output_file = f"tasksets_n_{new_n}.txt"
        output_file = os.path.join(output_folder, output_file)
        generate_file(nrof_task_sets, new_n, b, Unorm, m, output_file)
        print(f"Task sets have been generated in {output_file}")
    
    # Vary b, i.e., number of callbacks per chain
    output_folder = "./JiangFig6/vary_b"
    os.makedirs(output_folder)
    for i in range(2, 7):
        new_b = i
        output_file = f"tasksets_b_{new_b}.txt"
        output_file = os.path.join(output_folder, output_file)
        generate_file(nrof_task_sets, n, new_b, Unorm, m, output_file)
        print(f"Task sets have been generated in {output_file}")
    
    # Vary m, i.e., number of executor-threads
    output_folder = "./JiangFig6/vary_m"
    os.makedirs(output_folder)
    for i in range(2, 9):
        new_m = i
        output_file = f"tasksets_m_{new_m}.txt"
        output_file = os.path.join(output_folder, output_file)
        generate_file(nrof_task_sets, n, b, Unorm, new_m, output_file)
        print(f"Task sets have been generated in {output_file}")
    
def generate_Sobhani_Fig9_lite(nrof_task_sets, n, b, filename="tasksets.txt"):
    """
    Generate a file with multiple task sets.
    """
    name = "tasksets"

    for i in range(8, 41, 4):
        U = i / 10
        full_name = f"{name}_{U}.txt"

        with open(full_name, "w") as f:
            for _ in range(nrof_task_sets):
                NC = n
                C = b
                task_set = generate_task_set(U, NC, C)
                f.write(task_set + "\n")

def generate_Sobhani_b(nrof_task_sets, n, filename="tasksets.txt"):
    """
    Generate a file with multiple task sets.
    """
    name = "tasksets"
    U = 1.0

    for b in range(11, 21, 1):
        full_name = f"{name}_{b}.txt"

        with open(full_name, "w") as f:
            for _ in range(nrof_task_sets):
                NC = n
                C = b
                task_set = generate_task_set(U, NC, C)
                f.write(task_set + "\n")

if __name__ == "__main__":
    # generate_data_for_Fig6_Jiang()
    # generate_file(5, 8, 5, 0.3, 4)
    generate_Sobhani_Fig9_lite(200, 5, 10)
    # generate_Sobhani_b(200, 5)
