#include <iostream>
#include <vector>
#include <algorithm> // contains std::next_permutation, std::reverse
#include <numeric>   // contains std::iota
#include <string>

// Helper to perform the pancake flipping for a specific permutation
// We pass a copy of the permutation because the flipping is destructive
inline int count_flips(const std::vector<int>& perm) {
    // Optimization: If the first element is 1, it's 0 flips immediately.
    // This check is very cheap and saves a copy.
    if (perm[0] == 1) return 0;

    // Use a local working copy for the simulation to preserve the original
    // permutation for the next_permutation step in main.
    std::vector<int> work_buffer = perm;
    int flips = 0;
    int first = work_buffer[0];

    // Repeat until the first element is 1
    while (first != 1) {
        // "Take the first element, here 4, and reverse the order of the first 4 elements"
        // In C++, the end iterator is exclusive, so we reverse from begin() to begin() + first
        std::reverse(work_buffer.begin(), work_buffer.begin() + first);
        
        flips++;
        first = work_buffer[0];
    }
    return flips;
}

int main(int argc, char* argv[]) {
    // 1. Parse Argument
    int n = 7; // Default
    if (argc > 1) {
        n = std::stoi(argv[1]);
    }

    if (n < 1) return 0;

    // 2. Initialization
    // We use a vector for the permutation. 
    // This allows us to use std::next_permutation natively.
    std::vector<int> current_perm(n);
    
    // Fill with 1, 2, ..., n
    std::iota(current_perm.begin(), current_perm.end(), 1);

    long long checksum = 0;
    int max_flips = 0;
    long long index = 0;

    // 3. Main Loop
    // do-while ensures we process the initial sorted state (1,2,3...)
    do {
        // Calculate flips for the current state
        int flips = count_flips(current_perm);

        // Update Max Flips
        if (flips > max_flips) {
            max_flips = flips;
        }

        // Update Checksum
        // Logic: checksum + (if index is even then flips else -flips)
        if (index % 2 == 0) {
            checksum += flips;
        } else {
            checksum -= flips;
        }

        index++;

    // std::next_permutation rearranges the elements in the range [first, last) 
    // into the next lexicographically greater permutation.
    } while (std::next_permutation(current_perm.begin(), current_perm.end()));

    // 4. Output Results
    std::cout << checksum << "\n";
    std::cout << "Pfannkuchen(" << n << ") = " << max_flips << std::endl;

    return 0;
}