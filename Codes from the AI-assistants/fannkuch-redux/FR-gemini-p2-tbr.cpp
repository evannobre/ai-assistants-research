/*
 * Fannkuch-Redux Implementation
 * Optimized for C++ Standard Library (Native Pthreads)
 * * Strategy:
 * 1. Divide N! work units across std::thread hardware contexts.
 * 2. Use factoradic number system to jump to permutation indices.
 * 3. Minimize heap allocations to respect cache locality.
 */

#include <iostream>
#include <vector>
#include <thread>
#include <algorithm>
#include <numeric>
#include <array>
#include <future>
#include <vector>

// Fast type for indices
using Permutation = std::vector<int>;

// Calculations for factorials up to n=20 (sufficient for this problem)
constexpr int MAX_N = 16;
int64_t FACT[MAX_N + 1];

void precompute_factorials() {
    FACT[0] = 1;
    for (int i = 1; i <= MAX_N; ++i) {
        FACT[i] = FACT[i - 1] * i;
    }
}

// Optimized function to count flips for a single permutation
// This is the "hot loop" of the application.
inline int count_flips(const int* current_perm, int n) {
    // We use a local stack buffer to avoid malloc overhead in the hot path
    int perm[MAX_N];
    std::copy(current_perm, current_perm + n, perm);

    int flips = 0;
    int first = perm[0];
    
    // Repeat until the first element is 0 (normalized form of 1)
    while (first != 0) {
        // Reverse the first 'k' elements (where k is the value of the first element)
        // std::reverse is often optimized to SIMD by modern compilers
        std::reverse(perm, perm + first + 1);
        flips++;
        first = perm[0];
    }
    return flips;
}

// The worker function executed by each thread
void worker(int n, int64_t index_start, int64_t chunk_size, 
            int& max_flips_out, int& checksum_out) {
    
    // Thread-local storage to prevent false sharing between CPU cores
    int max_flips = 0;
    int checksum = 0;
    
    // Permutation state buffers
    std::vector<int> p(n);
    std::vector<int> count(n);
    std::vector<int> current_perm(n);

    // Initialize the permutation at 'index_start' using Factoradic system
    // This allows us to "jump" to the middle of the permutation sequence
    int64_t idx = index_start;
    for (int i = 0; i < n; ++i) p[i] = i;
    for (int i = n - 1; i > 0; --i) {
        int64_t d = idx / FACT[i];
        count[i] = d;
        idx = idx % FACT[i];
        
        std::rotate(p.begin(), p.begin() + d, p.begin() + i + 1);
    }
    current_perm = p;

    // Iterate through this thread's chunk
    int64_t steps = 0;
    while (steps < chunk_size) {
        // 1. Core Logic: Perform the flips
        if (current_perm[0] != 0) {
            int flips = count_flips(current_perm.data(), n);
            if (flips > max_flips) max_flips = flips;
            
            // Fannkuch checksum logic: add if index is even, sub if odd
            if ((index_start + steps) % 2 == 0) checksum += flips;
            else checksum -= flips;
        }

        // 2. Generator Logic: Generate next permutation
        // This simulates the recursive rotation without recursion
        // (Standard Fannkuch rotation algorithm)
        bool next_perm_found = false;
        for (int i = 1; i < n; ++i) {
            // Rotate the first i+1 elements
            int first = p[0];
            for (int j = 0; j < i; ++j) p[j] = p[j+1];
            p[i] = first;
            
            count[i]++;
            if (count[i] <= i) {
                next_perm_found = true;
                break;
            }
            count[i] = 0;
        }
        
        if (!next_perm_found) break; // Should effectively not happen within chunk bounds
        current_perm = p;
        steps++;
    }

    // Write back results
    max_flips_out = max_flips;
    checksum_out = checksum;
}

int main(int argc, char* argv[]) {
    // Default to n=12 if no argument provided
    int n = (argc > 1) ? std::stoi(argv[1]) : 12;
    if (n < 3 || n >= MAX_N) {
        std::cerr << "n must be between 3 and " << MAX_N - 1 << std::endl;
        return 1;
    }

    precompute_factorials();
    
    // Native hardware concurrency detection
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 2; // Fallback

    std::cout << "Solving Fannkuch-Redux for n=" << n << " using " << num_threads << " threads.\n";

    int64_t total_permutations = FACT[n];
    int64_t chunk_size = total_permutations / num_threads;
    
    std::vector<std::thread> threads;
    std::vector<int> max_flips_results(num_threads);
    std::vector<int> checksum_results(num_threads);

    // Launch threads
    for (unsigned int i = 0; i < num_threads; ++i) {
        int64_t start = i * chunk_size;
        int64_t size = (i == num_threads - 1) ? (total_permutations - start) : chunk_size;
        
        threads.emplace_back(worker, n, start, size, 
                           std::ref(max_flips_results[i]), 
                           std::ref(checksum_results[i]));
    }

    // Join threads and aggregate results
    int final_max_flips = 0;
    int final_checksum = 0;

    for (unsigned int i = 0; i < num_threads; ++i) {
        threads[i].join();
        final_max_flips = std::max(final_max_flips, max_flips_results[i]);
        final_checksum += checksum_results[i];
    }

    std::cout << final_checksum << "\n";
    std::cout << "Pfannkuch(" << n << ") = " << final_max_flips << std::endl;

    return 0;
}