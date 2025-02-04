function generateTaskSets(target_sets, Util, N, CN, path)
    %GENERATETASKSETS Generate task sets with chain configurations.
    %
    %   generateTaskSets(target_sets, Util, N, CN, path)
    %
    %   Generates target_sets task sets where:
    %     - There are CN chains.
    %     - Each chain has N tasks (callbacks).
    %     - Each task's period is the same within a chain. For chain t, the 
    %       period is a random number uniformly drawn from [1, 1000] (the CN
    %       draws are sorted in ascending order).
    %     - Task execution times are computed from a UUniFast-generated vector
    %       of utilizations for all N*CN tasks.
    %
    %   This version does not impose any extra constraint on the per‐chain
    %   utilization. (Even if some chains have utilization > 1, the set is saved.)
    %
    %   The resulting task set is stored in the file specified by path.
    %
    %   Each row in the output file contains:
    %       [T  C  T  task_id  chain_idx]
    %
    %   A line containing just '-' is written as a separator after each task set.
    
    num_sets = 0;
    
    while num_sets < target_sets
        % Generate one period for each chain (uniformly from 1 to 1000)
        T_chain = 1 + (1000 - 1)*rand(1, CN);
        T_chain = sort(T_chain);  % sort in ascending order
    
        % Initialize the period and chain-index vectors for all tasks
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
        
        % Compute the execution times (C) for tasks:
        %   C = period * utilization
        C = T .* util_tasks;
        
        % Assemble the task set matrix:
        %   Column 1: Task period
        %   Column 2: Task execution time
        %   Column 3: Task period (again, e.g., for deadline assignment)
        %   Column 4: Task id (from 1 to N*CN)
        %   Column 5: Chain id
        task_ids = (1:(N*CN))';
        taskset = [T', C', T', task_ids, chain_idx'];
        
        % Save this task set to file (append to file)
        dlmwrite(path, taskset, '-append', 'delimiter', '\t');
        dlmwrite(path, '-', '-append');
        
        num_sets = num_sets + 1;
    end
end