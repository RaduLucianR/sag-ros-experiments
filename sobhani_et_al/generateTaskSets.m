function generateTaskSets(target_sets, Util, N, CN, path)
%GENERATETASKSETS Generate task sets with chain configurations.
%
%   generateTaskSets(target_sets, Util, N, CN, path)
%
%   Generates target_sets task sets where:
%     - There are CN chains.
%     - Each chain has N tasks (callbacks).
%     - For each chain, the period is a random multiple of 10 in the interval
%       [10, 1000]. (The CN periods are sorted in ascending order.)
%     - Task execution times are computed using UUniFast such that the total
%       utilization of the task set is Util. Execution times are rounded to
%       integers.
%
%   Additionally, for each candidate task set the hyper-period is computed as 
%   the LCM of all chain periods. For each chain i, the number of jobs is computed as:
%
%           s = (hyperperiod / T_chain(i)) * N
%
%   The task set is accepted and saved only if the number of jobs is in the interval [a, b].
%   This is done in order to prevent a big number of jobs that will lead to
%   big computation times.
%
%   The resulting task set is stored in the file specified by path.
%
%   Each row in the output file contains:
%       [T  C  T  task_id  chain_idx]
%
%   A line containing just '-' is written as a separator after each task set.
%
%   (Note: You can modify the values of 'a' and 'b' as needed.)

    % Define the acceptable interval for s values.
    a = 1;   % lower bound (adjust as needed)
    b = 5000;  % upper bound (adjust as needed)
    
    num_sets = 0;
    
    while num_sets < target_sets
        % Generate one period for each chain (multiples of 10 between 10 and 1000)
        T_chain = 10 * randi([1, 100], 1, CN); 
        T_chain = sort(T_chain);  % sort in ascending order
        
        % --- Compute the hyper-period (LCM of all chain periods) ---
        hyperperiod = T_chain(1);
        for t = 2:CN
            hyperperiod = lcm(hyperperiod, T_chain(t));
        end
        
        % Compute s for each chain: s = (hyperperiod / chain period) * N.
        s_values = (hyperperiod ./ T_chain) * N;
        
        % Reject the task set if any s is not in the interval [a, b]
        if any(s_values < a | s_values > b)
            continue;  % Skip to next iteration (do not count this candidate)
        end
        
        % --- Proceed to generate the rest of the task set ---
        
        % Initialize the period and chain-index vectors for all tasks.
        T = zeros(1, N*CN);         % period vector for each task
        chain_idx = zeros(1, N*CN);   % chain number for each task
    
        % For each chain assign its period to all its tasks.
        for t = 1:CN
            idx = (t-1)*N + (1:N);
            T(idx) = T_chain(t);
            chain_idx(idx) = t;
        end
    
        % Generate task utilizations (for all tasks) that sum to Util.
        util_tasks = UUniFast(N*CN, Util);
        
        % Compute the execution times (C) for tasks as floats.
        C_float = T .* util_tasks;
        
        % Round the values but ensure no element falls below 1.
        C = max(round(C_float), 1);
        
        % Adjust execution times to maintain total utilization.
        scaling_factor = Util / sum(C ./ T);  % Compute adjustment factor
        C = max(round(C * scaling_factor), 1);  % Scale and enforce a minimum of 1.
        
        % Assemble the task set matrix:
        %   Column 1: Task period
        %   Column 2: Task execution time
        %   Column 3: Task period (again, e.g., for deadline assignment) i.e. implicit deadlines
        %   Column 4: Task id (from 1 to N*CN)
        %   Column 5: Chain id
        task_ids = (1:(N*CN))';
        taskset = [T', C', T', task_ids, chain_idx'];
        
        % Save this task set to file (append to file)
        dlmwrite(path, taskset, '-append', 'delimiter', '\t');
        dlmwrite(path, '-', '-append');
        
        num_sets = num_sets + 1;
        fprintf('Set number = %d\n', num_sets);
    end
end