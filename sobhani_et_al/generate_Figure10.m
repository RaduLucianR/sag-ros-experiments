% Script to generate data for Fig 9 of Sobhani et al.
% The script generates Fig 9 itself (only for PWA_CD)
%% Part 1: Generate task sets
% Parameters:
target_sets = 1000;  % number of valid task sets to generate per utilization
N = 10;              % number of callbacks (tasks) per chain
CN = 5;              % number of chains
Util = 1.0;          % fixed utilization of 1.0
dataFile = 'tasksets_util_1.0.txt';
path = sprintf(dataFile);
    
% If file already exists, then skip i.e. 
% FILES ARE NOT REPLACED IF THEY ALREADY EXIST
if exist(path, 'file')
    fprintf('File already exists, not generating...\n');
else
    fprintf('Generating task sets for Util = %.1f\n', Util);
    generateTaskSets(target_sets, Util, N, CN, path);
end

%% Part 2. Analysis: Read files and compute schedulability ratio
% Settings for schedulability analysis (assume PWA_CD is available).
PRIO = 0;       % priority-driven flag (1: priority-driven, 0: non-priority)
CG_enabled = 0; % CG flag (1: mutually-exclusive, 0: reentrant)

M_values = 1:16;
sched_ratio = zeros(size(M_values));  % to store schedulability ratio for each U

fprintf('Starting analysis of generated task-set files...\n');
for k = 1:length(M_values)
    M = M_values(k);
    fileName = sprintf(dataFile);
    
    if ~exist(fileName, 'file')
        warning('File %s not found. Skipping...', fileName);
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
    fprintf('  Number of executor-threads = %.1f, Schedulability Ratio = %.3f\n', M, ratio);
    
end

%% Part 3. Plotting and saving the Results
figure;
plot(M_values, sched_ratio, '-o', 'LineWidth', 2, 'MarkerSize',8);
xlabel('Number of executor-threads');
ylabel('Schedulability Ratio');
title('Schedulability Ratio vs. Number of executor-threads');
xticks(M_values); 
xlim([1, 16]);  % Ensure x-axis limits match
grid on;
saveas(gcf, 'Figure10.png');
results = [M_values(:) sched_ratio(:)];
writematrix(results, 'Figure10_data.csv');