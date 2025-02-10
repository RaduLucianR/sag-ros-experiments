% Script to generate data for Fig 11 of Sobhani et al.
% The script generates Fig 11 itself (only for PWA_CD)
%% Part 1: Generate task sets
% Parameters:
target_sets = 1000;  % number of valid task sets to generate per utilization
N = 10;              % number of callbacks (tasks) per chain
Util = 1.0;

% Number of chains from 1 to 10
cn_values = 1:10;

for CN = cn_values
    % Create a file name that includes the current Util value.
    path = sprintf('tasksets_cn_%d.txt', CN);
    
    % If file already exists, then skip i.e. 
    % FILES ARE NOT REPLACED IF THEY ALREADY EXIST
    if exist(path, 'file')
        continue;
    end
    
    fprintf('Generating task sets for CN = %d\n', CN);
    generateTaskSets(target_sets, Util, N, CN, path);
end

%% Part 2. Analysis: Read files and compute schedulability ratio
% Settings for schedulability analysis (assume PWA_CD is available).
M = 4;          % number of processors
PRIO = 0;       % priority-driven flag (1: priority-driven, 0: non-priority)
CG_enabled = 0; % CG flag (1: mutually-exclusive, 0: reentrant)

cn_values = 1:10;
sched_ratio = zeros(size(cn_values));  % to store schedulability ratio for each U

fprintf('Starting analysis of generated task-set files...\n');
for k = 1:length(cn_values)
    CN = cn_values(k);
    fileName = sprintf('tasksets_cn_%d.txt', CN);
    
    if ~exist(fileName, 'file')
        warning('File %s not found. Skipping number of chains = %d.', fileName, CN);
        sched_ratio(k) = NaN;
        continue;
    end
    
    % Open the file and read it line by line.
    fid = fopen(fileName, 'r');

    data = textscan(fid, '%f%f%f%d%d', 'Delimiter', '-');
    fclose(fid);

    chainset = []; chain = []; resultset = [];
    num_chain = 1;
    for i = 1 : size(data{1, 1}, 1)
        if isnan(data{1, 1}(i))
            if ~isempty(chain)
                chainset = [chainset; chain];
            end

            % Find the response-time
            [R, S, SCHED] = PWA_CD(chainset, M, PRIO,CG_enabled);


            P = []; C = [];
            for c = 1 : size(chainset, 1)
                P = [P; chainset(c).T];
                C = [C; sum(chainset(c).C)];
            end
            result = struct('chainset_id', num_chain, 'SCHED', SCHED, 'R', R, 'S', S, 'P', P, 'C', C);
            resultset = [resultset; result];

            num_chain = num_chain + 1;
            chainset = [];
            chain = [];
        else
            if ~isempty(chain)
                if data{1, 5}(i) == chain.id
                    chain.C = [chain.C data{1, 2}(i)];
                    chain.priority = [chain.priority data{1, 4}(i)];
                else
                    chainset = [chainset; chain];
                    chain = struct('id', data{1, 5}(i), 'T', data{1, 1}(i), 'C', data{1, 2}(i), 'D', data{1, 3}(i), 'priority', data{1, 4}(i));
                end
            else
                chain = struct('id', data{1, 5}(i), 'T', data{1, 1}(i), 'C', data{1, 2}(i), 'D', data{1, 3}(i), 'priority', data{1, 4}(i));
            end

        end
    end
    
    %statistics
    schedulable = 0;
    for i = 1 : size(resultset, 1)
        schedulable = schedulable + resultset(i).SCHED;
    end
    ratio = schedulable/size(resultset, 1);
    sched_ratio(k) = ratio;
    fprintf('  Number of chains = %d, Schedulability Ratio = %.3f\n', CN, ratio);
    
end

%% Part 3. Plotting and saving the Results
figure;
plot(cn_values, sched_ratio, '-o', 'LineWidth', 2, 'MarkerSize',8);
xlabel('Number of chains');
ylabel('Schedulability Ratio');
title('Schedulability Ratio vs. Number of chains');
xticks(cn_values); 
xlim([1, 10]);  % Ensure x-axis limits match
grid on;
saveas(gcf, 'Figure11.png');
results = [cn_values(:) sched_ratio(:)];
writematrix(results, 'Figure11_data.csv');