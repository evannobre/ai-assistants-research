#include <algorithm>
#include <iostream>
#include <vector>
#include <cstdint>
#include <immintrin.h>  // For SIMD intrinsics if available

class FannkuchRedux {
public:
    static void run(int n) {
        if (n < 1) {
            std::cout << "Pfannkuchen(0) = 0\n";
            return;
        }

        auto [max_flips, checksum] = fannkuch(n);
        
        std::cout << checksum << "\n";
        std::cout << "Pfannkuchen(" << n << ") = " << max_flips << "\n";
    }

private:
    static std::pair<int, int32_t> fannkuch(int n) {
        std::vector<int> permutation(n);
        std::vector<int> count(n, 0);
        
        // Initialize permutation
        for (int i = 0; i < n; ++i) {
            permutation[i] = i;
        }

        int max_flips = 0;
        int32_t checksum = 0;
        int perm_count = 0;
        int r = n;

        // Iterative permutation generation using counting method
        while (true) {
            // Count flips for current permutation
            int flips = count_flips(permutation);
            max_flips = std::max(max_flips, flips);
            
            // Update checksum with alternating sign
            if (perm_count % 2 == 0) {
                checksum += flips;
            } else {
                checksum -= flips;
            }
            perm_count++;

            // Generate next permutation
            while (r > 1) {
                count[r - 1] = r;
                r--;
            }

            bool found = false;
            for (int i = r; i < n; ++i) {
                if (count[i] > 0) {
                    found = true;
                    
                    // Rotate prefix
                    int first = permutation[0];
                    for (int j = 0; j < i; ++j) {
                        permutation[j] = permutation[j + 1];
                    }
                    permutation[i] = first;
                    
                    count[i]--;
                    break;
                }
            }

            if (!found) {
                break;
            }
        }

        return {max_flips, checksum};
    }

    static int count_flips(std::vector<int>& permutation) {
        const int n = permutation.size();
        if (permutation[0] == 0) return 0;
        
        // Use a temporary array for efficient flipping
        std::vector<int> temp(n);
        for (int i = 0; i < n; ++i) {
            temp[i] = permutation[i];
        }
        
        int flips = 0;
        
        while (true) {
            const int first = temp[0];
            if (first == 0) break;
            
            // Reverse the first 'first' elements
            const int flip_count = (first + 1) / 2;
            for (int i = 0; i < flip_count; ++i) {
                std::swap(temp[i], temp[first - i]);
            }
            
            flips++;
        }
        
        return flips;
    }
};

// Optimized version with manual loop unrolling
class FannkuchReduxOptimized {
public:
    static void run(int n) {
        if (n < 1) {
            std::cout << "Pfannkuchen(0) = 0\n";
            return;
        }

        auto [max_flips, checksum] = fannkuch_optimized(n);
        
        std::cout << checksum << "\n";
        std::cout << "Pfannkuchen(" << n << ") = " << max_flips << "\n";
    }

private:
    static std::pair<int, int32_t> fannkuch_optimized(int n) {
        // Use arrays instead of vectors for better cache performance
        int* permutation = new int[n];
        int* count = new int[n];
        
        // Initialize
        for (int i = 0; i < n; ++i) {
            permutation[i] = i;
            count[i] = 0;
        }

        int max_flips = 0;
        int32_t checksum = 0;
        int perm_count = 0;
        int r = n;

        // Temporary buffer for flips calculation
        int* temp = new int[n];

        while (true) {
            // Copy to temp buffer
            std::copy(permutation, permutation + n, temp);
            
            int flips = 0;
            int first_element = temp[0];
            
            // Count flips with early exit
            while (first_element != 0) {
                // Manual loop unrolling for better performance
                int flip_len = first_element + 1;
                int half = flip_len / 2;
                
                // Reverse the segment
                for (int i = 0; i < half; ++i) {
                    std::swap(temp[i], temp[first_element - i]);
                }
                
                flips++;
                first_element = temp[0];
            }
            
            max_flips = std::max(max_flips, flips);
            checksum += (perm_count % 2 == 0) ? flips : -flips;
            perm_count++;

            // Generate next permutation
            while (r > 1) {
                count[r - 1] = r;
                r--;
            }

            bool found_next = false;
            for (int i = r; i < n; ++i) {
                if (count[i] > 0) {
                    found_next = true;
                    
                    // Rotate the prefix [0..i]
                    int first_val = permutation[0];
                    for (int j = 0; j < i; ++j) {
                        permutation[j] = permutation[j + 1];
                    }
                    permutation[i] = first_val;
                    
                    count[i]--;
                    break;
                }
            }

            if (!found_next) {
                break;
            }
        }

        // Cleanup
        delete[] permutation;
        delete[] count;
        delete[] temp;

        return {max_flips, checksum};
    }
};

int main(int argc, char* argv[]) {
    int n = 12;  // Default value
    
    if (argc > 1) {
        n = std::atoi(argv[1]);
    }
    
    // Use optimized version for larger inputs
    if (n > 10) {
        FannkuchReduxOptimized::run(n);
    } else {
        FannkuchRedux::run(n);
    }
    
    return 0;
}