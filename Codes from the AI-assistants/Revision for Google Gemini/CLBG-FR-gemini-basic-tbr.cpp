#include <iostream>
#include <vector>
#include <thread>
#include <future>
#include <algorithm>
#include <cstdlib>

using namespace std;

// Structure to hold the result of each thread's chunk of work
struct Result {
    int max_flips;
    long long checksum;
};

// Worker function that processes a specific chunk of permutations
Result fannkuch_redux_task(int n, long long start_idx, long long num_perms) {
    vector<int> p(n);
    vector<int> count(n, 0);
    vector<long long> fact(n + 1);
    
    // Precompute factorials for generating the initial permutation state
    fact[0] = 1;
    for (int i = 1; i <= n; i++) {
        fact[i] = fact[i - 1] * i;
    }

    // Initialize base permutation: {0, 1, 2, ..., n-1}
    for (int i = 0; i < n; i++) {
        p[i] = i;
    }

    // Reconstruct the permutation and 'count' array for the 'start_idx'
    // This uses the factoradic number system (factorial base)
    long long idx = start_idx;
    for (int i = n - 1; i >= 1; i--) {
        int d = idx / fact[i];
        count[i] = d;
        idx = idx % fact[i];
        
        // Rotate p[0..i] to the left by 'd' positions
        vector<int> temp(i + 1);
        for (int j = 0; j <= i; j++) {
            temp[j] = p[(j + d) % (i + 1)];
        }
        for (int j = 0; j <= i; j++) {
            p[j] = temp[j];
        }
    }

    int max_flips = 0;
    long long checksum = 0;
    vector<int> q(n);

    // Iterate through the assigned number of permutations
    for (long long k = 0; k < num_perms; k++) {
        
        // If the first element is not 0, flips are needed
        if (p[0] != 0) {
            for (int i = 0; i < n; i++) q[i] = p[i];
            
            int flips = 0;
            int first = q[0];
            
            // Flip elements until the first element becomes 0
            while (first != 0) {
                int left = 0;
                int right = first;
                while (left < right) {
                    int temp_val = q[left];
                    q[left] = q[right];
                    q[right] = temp_val;
                    left++;
                    right--;
                }
                flips++;
                first = q[0];
            }
            
            if (flips > max_flips) {
                max_flips = flips;
            }
            
            // Maintain checksum based on whether the permutation index is even or odd
            if ((start_idx + k) % 2 == 0) {
                checksum += flips;
            } else {
                checksum -= flips;
            }
        }

        // Generate the next permutation using the standard lexicographic rotation method
        int i = 1;
        while (i < n) {
            int first = p[0];
            for (int j = 0; j < i; j++) {
                p[j] = p[j + 1];
            }
            p[i] = first;

            count[i]++;
            if (count[i] <= i) {
                break;
            }
            count[i] = 0;
            i++;
        }
    }
    return {max_flips, checksum};
}

int main(int argc, char** argv) {
    int n = 7; // Default value
    if (argc > 1) {
        n = atoi(argv[1]);
    }

    // Calculate total number of permutations (n!)
    long long total_perms = 1;
    for (int i = 1; i <= n; i++) {
        total_perms *= i;
    }

    // Determine the number of hardware threads available
    int num_threads = thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 4; // Fallback

    // Divide the permutations into equal chunks for each thread
    long long chunk_size = total_perms / num_threads;
    long long remainder = total_perms % num_threads;

    vector<future<Result>> futures;
    long long start_idx = 0;

    // Launch threads asynchronously
    for (int i = 0; i < num_threads; i++) {
        long long perms_for_thread = chunk_size + (i < remainder ? 1 : 0);
        if (perms_for_thread > 0) {
            futures.push_back(async(launch::async, fannkuch_redux_task, n, start_idx, perms_for_thread));
            start_idx += perms_for_thread;
        }
    }

    int max_flips = 0;
    long long checksum = 0;

    // Gather results from all threads
    for (auto& f : futures) {
        Result res = f.get();
        if (res.max_flips > max_flips) {
            max_flips = res.max_flips;
        }
        checksum += res.checksum;
    }

    // Output formatted exactly as the benchmark requires
    cout << checksum << "\nPfannkuchen(" << n << ") = " << max_flips << "\n";
    return 0;
}