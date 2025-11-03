#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>

class Fannkuch {
private:
    int n;
    int64_t checksum;
    int max_flips;
    std::vector<int> perm;
    std::vector<int> count;
    
public:
    Fannkuch(int n) : n(n), checksum(0), max_flips(0), 
                      perm(n), count(n, 0) {
        for (int i = 0; i < n; ++i) {
            perm[i] = i + 1;
        }
    }
    
    void run() {
        if (n < 1) return;
        
        int r = n;
        int perm_sign = 1;
        
        while (true) {
            // Count flips for current permutation
            int flips = count_flips();
            max_flips = std::max(max_flips, flips);
            checksum += perm_sign * flips;
            
            // Generate next permutation
            while (r != 1 && count[r - 1] == r - 1) {
                count[r - 1] = 0;
                --r;
            }
            
            if (r == 1) break;
            
            int pos = r - 1;
            count[pos]++;
            
            // Swap elements
            if (perm_sign == 1) {
                std::swap(perm[0], perm[pos]);
            } else {
                std::swap(perm[pos - 1], perm[pos]);
            }
            
            perm_sign = -perm_sign;
            
            if (r < n) ++r;
        }
    }
    
    int count_flips() {
        if (perm[0] == 1) return 0;
        
        // Work on a copy to avoid modifying the original
        std::vector<int> temp = perm;
        int flips = 0;
        int first = temp[0];
        
        while (first != 1) {
            // Reverse first 'first' elements
            int i = 1, j = first - 1;
            while (i < j) {
                std::swap(temp[i], temp[j]);
                ++i;
                --j;
            }
            ++flips;
            first = temp[0];
        }
        
        return flips;
    }
    
    int64_t get_checksum() const { return checksum; }
    int get_max_flips() const { return max_flips; }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <n>" << std::endl;
        return 1;
    }
    
    int n = std::atoi(argv[1]);
    if (n < 0 || n > 12) {
        std::cerr << "Error: n must be between 0 and 12" << std::endl;
        return 1;
    }
    
    Fannkuch fannkuch(n);
    fannkuch.run();
    
    std::cout << fannkuch.get_checksum() << std::endl;
    std::cout << "Pfannkuchen(" << n << ") = " << fannkuch.get_max_flips() << std::endl;
    
    return 0;
}
