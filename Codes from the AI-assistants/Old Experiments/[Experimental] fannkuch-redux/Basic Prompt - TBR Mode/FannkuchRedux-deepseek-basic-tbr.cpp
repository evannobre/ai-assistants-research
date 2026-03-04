#include <algorithm>
#include <vector>
#include <iostream>
#include <numeric>

int count_flips(std::vector<int>& perm) {
    int count = 0;
    int first = perm[0];
    
    if (first == 0) return count;
    
    std::vector<int> current = perm;
    
    while (current[0] != 0) {
        int k = current[0] + 1;
        // Reverse first k elements
        std::reverse(current.begin(), current.begin() + k);
        count++;
    }
    
    return count;
}

std::pair<int, int> fannkuch_redux(int n) {
    int max_flips = 0;
    int checksum = 0;
    
    std::vector<int> perm(n);
    std::iota(perm.begin(), perm.end(), 0);
    
    int index = 0;
    do {
        int flips = count_flips(perm);
        
        if (flips > max_flips) {
            max_flips = flips;
        }
        
        if (index % 2 == 0) {
            checksum += flips;
        } else {
            checksum -= flips;
        }
        
        index++;
    } while (std::next_permutation(perm.begin(), perm.end()));
    
    return {max_flips, checksum};
}

int main() {
    int n = 7;
    auto [max_flips, checksum] = fannkuch_redux(n);
    std::cout << "Pfannkuchen(" << n << ") = " << max_flips << std::endl;
    std::cout << "Checksum = " << checksum << std::endl;
    return 0;
}