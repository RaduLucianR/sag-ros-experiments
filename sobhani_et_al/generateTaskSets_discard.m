function generateTaskSets_discard(target_sets, Util, N, CN, path)
    %GENERATETASKSETS_DISCARD Generate task sets where every chain's utilization <= 1.
    %
    %   generateTaskSets_discard(target_sets, Util, N, CN, path)
    %
    %   This function works similarly to generateTaskSets except that it
    %   accepts (writes to file) only those task sets for which, in each chain,
    %   the total execution time does not exceed the chain’s period (i.e. the
    %   chain’s total utilization is at most 1).
    %
    %   The task set is saved in the file specified by path.
    %
    %   Each row in the output file contains:
    %       [T  C  T  task_id  chain_idx]
    %
    %   A line containing just '-' is written as a separator after each valid set.
    
    num_sets = 0;
    
    while num_sets < target_sets
        valid = true;
        
        % Generate one period for each chain (uniformly from 1 to 1000)
        T_chain = 1 + (1000 - 1) * rand(1, CN);
        T_chain = sort(T_chain);
    
        % Initialize the period and chain-index vectors for all tasks
        T = zeros(1, N*CN);
        chain_idx = zeros(1, N*CN);
        
        for t = 1:CN
            idx = (t-1)*N + (1:N);
            T(idx) = T_chain(t);
            chain_idx(idx) = t;
        end
        
        % Generate task utilizations for all tasks that sum to Util.
        util_tasks = UUniFast(N*CN, Util);
        
        % Compute execution times for tasks.
        C = T .* util_tasks;
        
        % Check that in every chain, the total execution time does not exceed
        % the (common) period for that chain.
        for t = 1:CN
            idx = (t-1)*N + (1:N);
            if sum(C(idx)) > T(idx(1))
                valid = false;
                break;
            end
        end
        
        if valid
            task_ids = (1:(N*CN))';
            taskset = [T', C', T', task_ids, chain_idx'];
            
            dlmwrite(path, taskset, '-append', 'delimiter', '\t');
            dlmwrite(path, '-', '-append');
            
            num_sets = num_sets + 1;
        end
    end
end