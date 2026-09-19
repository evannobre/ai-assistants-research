#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>

void fannkuch_redux(int n) {
    // 1. Native memory management and array structure
    std::vector<int> p(n);
    std::vector<int> count(n, 0);
    std::vector<int> q(n);

    // 2. std::iota (from <numeric>) fills the array natively with 1, 2, ..., n
    std::iota(p.begin(), p.end(), 1);

    int max_flips = 0;
    int checksum = 0;
    int sign = 1;

    while (true) {
        // --- PANCAKE FLIPPING ---
        // We only need to flip if the first element isn't already 1
        if (p[0] != 1) {
            q = p; 
            int flips = 0;
            while (q[0] != 1) {
                // 3. std::reverse natively handles the core "pancake flip" logic
                // It reverses elements from index 0 up to the value of the first element.
                std::reverse(q.begin(), q.begin() + q[0]);
                flips++;
            }
            
            // 4. std::max natively calculates the maximum flips seen so far
            max_flips = std::max(max_flips, flips);
            checksum += sign * flips;
        }

        // --- PERMUTATION GENERATION ---
        // Fannkuch-redux requires a specific rotation sequence, not lexicographical.
        sign = -sign;
        int i = 1;
        while (i < n) {
            // 5. std::rotate natively handles the exact cyclic left-shift required 
            // by the Fannkuch benchmark algorithm.
            std::rotate(p.begin(), p.begin() + 1, p.begin() + i + 1);
            
            count[i]++;
            if (count[i] <= i) {
                break;
            }
            count[i] = 0;
            i++;
        }

        // If we've rotated the largest outer bound, we've generated all permutations
        if (i == n) {
            break;
        }
    }

    std::cout << checksum << "\nPfannkuchen(" << n << ") = " << max_flips << "\n";
}

int main() {
    int n = 7; // Change this to test larger numbers (e.g., 10 or 11)
    fannkuch_redux(n);
    return 0;
}