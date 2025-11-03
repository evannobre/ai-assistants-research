#include <iostream>
#include <vector>
#include <algorithm>
#include <thread>
#include <atomic>
#include <immintrin.h>  // For SIMD instructions
#include <chrono>

class FannkuchRedux {
private:
    const int n;
    std::atomic<int> max_flips{0};
    std::atomic<int> checksum{0};
    
public:
    FannkuchRedux(int n) : n(n) {}
    
    // Count flips for a given permutation
    int count_flips(std::vector<int>& perm) {
        if (perm[0] == 0) return 0;
        
        std::vector<int> temp(n);
        int flips = 0;
        int first = perm[0];
        
        if (perm[first] != 0) {
            std::copy(perm.begin(), perm.end(), temp.begin());
            
            while (true) {
                int middle = first / 2;
                // Manual reversal for better performance
                for (int i = 0; i <= middle; ++i) {
                    std::swap(temp[i], temp[first - i]);
                }
                flips++;
                
                first = temp[0];
                if (first == 0) break;
            }
        }
        
        return flips;
    }
    
    // Worker function for parallel processing
    void worker(int start, int end, const std::vector<int>& initial) {
        std::vector<int> perm = initial;
        std::vector<int> count(n, 0);
        
        // Initialize permutation and counters
        for (int i = 0; i < n; ++i) {
            perm[i] = i;
        }
        
        // Generate permutations using Heap's algorithm optimization
        int local_max = 0;
        int local_checksum = 0;
        int idx = 0;
        
        while (true) {
            if (idx >= start) {
                int flips = count_flips(perm);
                local_max = std::max(local_max, flips);
                local_checksum += (idx % 2 == 0) ? flips : -flips;
            }
            
            idx++;
            if (idx >= end) break;
            
            // Generate next permutation
            int i = 1;
            while (count[i] >= i) {
                count[i] = 0;
                i++;
                if (i >= n) {
                    // Update global values
                    max_flips = std::max(max_flips.load(), local_max);
                    checksum += local_checksum;
                    return;
                }
            }
            count[i]++;
            std::swap(perm[0], perm[i]);
        }
        
        max_flips = std::max(max_flips.load(), local_max);
        checksum += local_checksum;
    }
    
    void solve() {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        const int total_permutations = [this]() {
            int result = 1;
            for (int i = 2; i <= n; ++i) result *= i;
            return result;
        }();
        
        // Determine optimal number of threads
        unsigned int num_threads = std::max(1u, std::thread::hardware_concurrency());
        num_threads = std::min(num_threads, 8u); // Limit to prevent memory issues
        
        std::vector<std::thread> threads;
        int chunk_size = total_permutations / num_threads;
        
        std::cout << "Processing " << total_permutations << " permutations using " 
                  << num_threads << " threads" << std::endl;
        
        // Create and run worker threads
        for (unsigned int i = 0; i < num_threads; ++i) {
            int start = i * chunk_size;
            int end = (i == num_threads - 1) ? total_permutations : (i + 1) * chunk_size;
            
            threads.emplace_back(&FannkuchRedux::worker, this, start, end, 
                               std::vector<int>(n));
        }
        
        // Wait for all threads to complete
        for (auto& t : threads) {
            t.join();
        }
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
            end_time - start_time);
        
        std::cout << checksum << std::endl;
        std::cout << "Pfannkuchen(" << n << ") = " << max_flips << std::endl;
        std::cout << "Time: " << duration.count() << " ms" << std::endl;
        
        // Memory usage report
        size_t memory_used = sizeof(int) * n * 2 * num_threads; // perm + temp arrays
        std::cout << "Estimated memory: " << memory_used / 1024 << " KB" << std::endl;
    }
};

int main(int argc, char* argv[]) {
    int n = 7; // Default value
    
    if (argc > 1) {
        n = std::atoi(argv[1]);
    }
    
    if (n < 1 || n > 12) {
        std::cerr << "Error: n must be between 1 and 12" << std::endl;
        return 1;
    }
    
    FannkuchRedux solver(n);
    solver.solve();
    
    return 0;
}