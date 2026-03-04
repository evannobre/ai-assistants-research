#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>

class FannkuchReduxOptimized {
public:
    static void run(int n) {
        int64_t checksum = 0;
        int max_flips = 0;
        
        // Use arrays for better cache locality
        std::vector<int> perm(n);
        std::vector<int> count(n);
        
        // Initialize permutation
        for (int i = 0; i < n; ++i) {
            perm[i] = i;
        }
        
        int r = n;
        bool even = true;
        int* perm_ptr = perm.data();
        
        // Main processing loop
        while (true) {
            // Reset counters
            while (r != 1) {
                count[r - 1] = r;
                --r;
            }
            
            // Calculate flips for current permutation
            if (perm_ptr[0] != 0 && perm_ptr[n - 1] != 0) {
                int flips = count_flips_fast(perm_ptr, n);
                max_flips = std::max(max_flips, flips);
                checksum += even ? flips : -flips;
            }
            
            // Generate next permutation
            while (true) {
                if (r == n) {
                    std::cout << checksum << "\n";
                    std::cout << "Pfannkuchen(" << n << ") = " << max_flips << "\n";
                    return;
                }
                
                // Rotate prefix
                int perm0 = perm_ptr[0];
                for (int i = 0; i < r; ++i) {
                    perm_ptr[i] = perm_ptr[i + 1];
                }
                perm_ptr[r] = perm0;
                
                // Update count
                if (--count[r] > 0) {
                    even = !even;
                    break;
                }
                ++r;
            }
        }
    }

private:
    static int count_flips_fast(int* perm, int n) {
        int flips = 0;
        int first = perm[0];
        
        if (first == 0) return flips;
        
        // Working array
        int* work = (int*)alloca(n * sizeof(int));
        std::copy(perm, perm + n, work);
        
        while (first != 0) {
            // Reverse first 'first+1' elements in place
            int i = 0;
            int j = first;
            while (i < j) {
                std::swap(work[i], work[j]);
                ++i;
                --j;
            }
            
            ++flips;
            first = work[0];
        }
        
        return flips;
    }
};

// Quick benchmark and validation for n=12
int main(int argc, char* argv[]) {
    int n = 12;
    if (argc > 1) {
        n = std::atoi(argv[1]);
    }
    
    FannkuchReduxOptimized::run(n);
    return 0;
}