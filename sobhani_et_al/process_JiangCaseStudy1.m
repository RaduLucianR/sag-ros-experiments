% Script to analyze Jiang et al.'s Case Study 1
% with Sobhani et al.'s Theorem 1

%% Part 2. Analysis: Read files and compute schedulability ratio
% Settings for schedulability analysis (assume PWA_CD is available).
M = 2;          % number of processors
PRIO = 0;       % priority-driven flag (1: priority-driven, 0: non-priority)
CG_enabled = 0; % CG flag (1: mutually-exclusive, 0: reentrant)
results = zeros(3);

fprintf('Starting analysis of the file...\n');
fileName = sprintf('jiang_case_study_1.txt');

if ~exist(fileName, 'file')
    warning('File %s not found.', fileName);
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
        results = R;
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

%% Part 3. Saving the Results
chain_id = 1:3;
results_save = [chain_id(:) results(:)];
writematrix(results_save, 'JiangCaseStudy1_data.csv');