function utilizations = UUniFast(n, U_total)
% UUNIFAST Generates n task utilizations with a total sum U_total.
%
%   utilizations = uunifast(n, U_total)
%
%   Inputs:
%       n       - Number of tasks.
%       U_total - Total utilization (e.g., 1.0 for 100% CPU).
%
%   Output:
%       utilizations - 1 x n vector of utilizations summing to U_total.
%
%   Reference:
%       Bini, R., Buttazzo, G. C., & Stankovic, L. (2004). Scheduling Algorithms
%       for Real-Time Systems. In the book Real-Time Systems (pp. 291-320).

    % Preallocate the utilizations vector.
    utilizations = zeros(1, n);
    
    % Initialize the sum of remaining utilizations.
    sumU = U_total;
    
    % Generate n-1 random utilizations.
    for i = 1:(n-1)
        % Draw a random number from U(0,1) and compute the next remaining sum.
        nextSumU = sumU * rand()^(1/(n - i));
        % The current task's utilization is the difference.
        utilizations(i) = sumU - nextSumU;
        % Update the sum for the remaining tasks.
        sumU = nextSumU;
    end
    
    % The last task gets the remaining utilization.
    utilizations(n) = sumU;
end
