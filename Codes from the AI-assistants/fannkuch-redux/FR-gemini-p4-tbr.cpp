/*
 * Fannkuch-Redux Implementation
 * Optimized for C++20 on Linux
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <thread>
#include <future>
#include <numeric>
#include <vector>
#include <array>

// Precomputed factorials for N=12 support (12! fits in 32-bit, but we use long for safety)
constexpr std::array<long, 21> FACTORIALS = [] {
    std::array<long, 21> f{};
    f[0] = 1;
    for (int i = 1; i <= 20; ++i) f[i] = f[i - 1] * i;
    return f;
}();

struct Result {
    int max_flips;
    int checksum;
};

// Helper: Calculate the permutation and count array for a specific index
// This allows a thread to "jump" to its assigned start point without running 
// the previous iterations.
void initialize_state(int n, long index, std::vector<int>& perm, std::vector<int>& count) {
    std::iota(perm.begin(), perm.end(), 0); // Fill 0, 1, 2...
    
    for (int i = n - 1; i > 0; --i) {
        long fact = FACTORIALS[i];
        int d = index / fact;
        count[i] = d;
        index = index % fact;
        
        // Rotate the permutation based on the factoradic digit
        std::rotate(perm.begin(), perm.begin() + d, perm.begin() + i + 1);
    }
}

// The Worker Function running on each thread
Result run_chunk(int n, long start_index, long end_index) {
    int max_flips = 0;
    int checksum = 0;

    // Thread-local storage to avoid reallocation
    std::vector<int> perm(n);
    std::vector<int> count(n);
    std::vector<int> current_perm(n); // Work copy for flipping

    // Initialize state at the start_index
    initialize_state(n, start_index, perm, count);

    // Iterate through the assigned chunk
    for (long idx = start_index; idx < end_index; ++idx) {
        
        // 1. Check for Flips
        // We only flip if the first element (perm[0]) is not 0.
        // (Note: Algorithm uses 1-based logic, code uses 0-based, so logic is perm[0] != 0)
        if (perm[0] != 0) {
            // Copy current permutation to work buffer
            std::copy(perm.begin(), perm.end(), current_perm.begin());
            
            int flips = 0;
            // Native logic: flip until first element is 0 (which represents '1' in 1-based)
            while (current_perm[0] != 0) {
                // k is the value of the first element
                int k = current_perm[0];
                // Reverse the first k+1 elements (using native std::reverse)
                std::reverse(current_perm.begin(), current_perm.begin() + k + 1);
                flips++;
            }

            // Update Max Flips
            if (flips > max_flips) max_flips = flips;

            // Update Checksum
            // Logic: if index is even add flips, else subtract
            if (idx % 2 == 0) checksum += flips;
            else checksum -= flips;
        }

        // 2. Generate Next Permutation (Fannkuch-Redux Rotation Algorithm)
        // This is the specific rotation logic required by the benchmark
        if (idx < end_index - 1) { // Don't rotate on the very last step of the chunk
            int i = 1;
            while (true) {
                count[i]++;
                if (count[i] <= i) break;
                count[i] = 0;
                i++;
            }
            // Perform the rotation
            // Rotate the first i+1 elements one step to the left
            int first = perm[0];
            for (int j = 0; j < i; ++j) {
                perm[j] = perm[j + 1];
            }
            perm[i] = first;
        }
    }

    return {max_flips, checksum};
}

int main(int argc, char* argv[]) {
    // 1. Argument Parsing
    int n = (argc > 1) ? std::stoi(argv[1]) : 7;
    if (n < 3 || n > 20) {
        std::cerr << "N must be between 3 and 20 for this implementation." << std::endl;
        return 1;
    }

    // 2. Hardware Detection
    // Use native library to detect CPU cores
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 1; 

    std::cout << "Running Fannkuch-Redux for n=" << n << std::endl;
    std::cout << "Using " << num_threads << " threads on Ubuntu Linux." << std::endl;

    long total_perms = FACTORIALS[n];
    long chunk_size = total_perms / num_threads;

    // 3. Launch Threads (Native std::async)
    std::vector<std::future<Result>> futures;
    
    for (unsigned int i = 0; i < num_threads; ++i) {
        long start = i * chunk_size;
        long end = (i == num_threads - 1) ? total_perms : (start + chunk_size);
        
        futures.push_back(std::async(std::launch::async, run_chunk, n, start, end));
    }

    // 4. Aggregation
    int global_max_flips = 0;
    int global_checksum = 0;

    for (auto& f : futures) {
        Result r = f.get();
        if (r.max_flips > global_max_flips) global_max_flips = r.max_flips;
        global_checksum += r.checksum;
    }

    // 5. Output
    std::cout << global_checksum << "\n";
    std::cout << "Pfannkuchen(" << n << ") = " << global_max_flips << std::endl;

    return 0;
}