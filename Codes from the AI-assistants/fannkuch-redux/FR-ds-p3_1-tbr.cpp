#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>
#include <cstring>

class FannkuchRedux {
public:
    static void run(int n) {
        int64_t checksum = 0;
        int max_flips = 0;
        
        // Create initial permutation
        std::vector<int> perm(n);
        std::vector<int> count(n, 0);
        
        for (int i = 0; i < n; ++i) {
            perm[i] = i;
        }
        
        int r = n;
        int parity = 0;
        
        // Main loop - generate permutations using factorial number system
        while (true) {
            // Skip permutations that don't start with 1 for optimization
            while (r != 1) {
                count[r - 1] = r;
                --r;
            }
            
            // Process current permutation
            int flips = count_flips(perm, n);
            max_flips = std::max(max_flips, flips);
            
            if (parity % 2 == 0) {
                checksum += flips;
            } else {
                checksum -= flips;
            }
            
            // Generate next permutation using factorial number system
            while (true) {
                if (r == n) {
                    std::cout << checksum << "\n";
                    std::cout << "Pfannkuchen(" << n << ") = " << max_flips << "\n";
                    return;
                }
                
                int perm0 = perm[0];
                for (int i = 0; i < r; ++i) {
                    perm[i] = perm[i + 1];
                }
                perm[r] = perm0;
                count[r] = count[r] - 1;
                
                if (count[r] > 0) {
                    parity ^= 1;
                    break;
                }
                ++r;
            }
        }
    }

private:
    static int count_flips(const std::vector<int>& perm, int n) {
        // Make a copy to avoid modifying original
        std::vector<int> temp = perm;
        int first = temp[0];
        int flips = 0;
        
        if (first == 0) return flips;
        
        // Use pointer arithmetic for speed
        int* p = temp.data();
        
        while (first != 0) {
            // Reverse the first 'first+1' elements
            int i = 0;
            int j = first;
            while (i < j) {
                std::swap(p[i], p[j]);
                ++i;
                --j;
            }
            
            ++flips;
            first = p[0];
        }
        
        return flips;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <n>\n";
        return 1;
    }
    
    int n = std::atoi(argv[1]);
    if (n < 1 || n > 20) {  // Practical limit for 8GB RAM
        std::cerr << "n must be between 1 and 20\n";
        return 1;
    }
    
    FannkuchRedux::run(n);
    return 0;
}