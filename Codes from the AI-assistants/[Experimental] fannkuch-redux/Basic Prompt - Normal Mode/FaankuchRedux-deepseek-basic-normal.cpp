#include <iostream>
#include <vector>
#include <algorithm>
#include <thread>
#include <future>
#include <numeric>

class Fannkuch {
private:
    int n;
    int total_perms;
    
    int factorial(int x) {
        int result = 1;
        for (int i = 2; i <= x; ++i) {
            result *= i;
        }
        return result;
    }
    
    struct Result {
        int max_flips;
        int checksum;
    };
    
    Result process_slice(int start, int end) {
        std::vector<int> count(n, 0);
        std::vector<int> perm(n);
        std::iota(perm.begin(), perm.end(), 0);
        
        Result result{0, 0};
        
        // Skip to starting permutation
        for (int i = 0; i < start; ++i) {
            int j = 1;
            while (j < n && count[j] >= j) {
                count[j] = 0;
                ++j;
            }
            if (j >= n) break;
            count[j] += 1;
            std::reverse(perm.begin(), perm.begin() + j + 1);
        }
        
        // Process the slice
        for (int idx = start; idx < end; ++idx) {
            int first = perm[0];
            if (first > 0) {
                int flips = 0;
                std::vector<int> temp_perm = perm;
                int k = first;
                
                while (k) {
                    std::reverse(temp_perm.begin(), temp_perm.begin() + k + 1);
                    ++flips;
                    k = temp_perm[0];
                }
                
                if (flips > result.max_flips) {
                    result.max_flips = flips;
                }
                
                result.checksum += (idx % 2 == 0) ? flips : -flips;
            }
            
            // Generate next permutation
            int j = 1;
            while (j < n && count[j] >= j) {
                count[j] = 0;
                ++j;
            }
            if (j >= n) break;
            count[j] += 1;
            std::reverse(perm.begin(), perm.begin() + j + 1);
        }
        
        return result;
    }

public:
    Fannkuch(int n) : n(n) {
        total_perms = factorial(n);
    }
    
    std::pair<int, int> compute() {
        if (n == 0) return {0, 0};
        
        unsigned int num_threads = std::thread::hardware_concurrency();
        if (num_threads == 0) num_threads = 1;
        
        int chunk_size = std::max(1, total_perms / (num_threads * 4));
        std::vector<std::future<Result>> futures;
        
        for (int start = 0; start < total_perms; start += chunk_size) {
            int end = std::min(start + chunk_size, total_perms);
            futures.push_back(std::async(std::launch::async, 
                [this, start, end]() { return process_slice(start, end); }));
        }
        
        int max_flips = 0;
        int checksum = 0;
        
        for (auto& future : futures) {
            Result result = future.get();
            if (result.max_flips > max_flips) {
                max_flips = result.max_flips;
            }
            checksum += result.checksum;
        }
        
        return {checksum, max_flips};
    }
};

int main(int argc, char* argv[]) {
    int n = (argc > 1) ? std::atoi(argv[1]) : 7;
    
    Fannkuch fannkuch(n);
    auto [checksum, max_flips] = fannkuch.compute();
    
    std::cout << checksum << std::endl;
    std::cout << "Pfannkuchen(" << n << ") = " << max_flips << std::endl;
    
    return 0;
}