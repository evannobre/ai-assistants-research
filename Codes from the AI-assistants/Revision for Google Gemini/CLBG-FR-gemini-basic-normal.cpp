#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <string>

using namespace std;

int main(int argc, char* argv[]) {
    // Default to 12 as requested, overrideable via command line
    int n = 12;
    if (argc > 1) {
        n = stoi(argv[1]);
    }

    // Use native vectors for automatic memory management
    vector<int> p(n);
    iota(p.begin(), p.end(), 0); // Natively fills array with 0, 1, 2... n-1

    vector<int> count(n, 0);
    vector<int> q(n);

    int max_flips = 0;
    int checksum = 0;
    int sign = 1;

    // Loop through all n! permutations
    while (true) {
        // Copy current permutation state to work array
        q = p;
        int flips = 0;

        // Flip until the first element is 0 (which represents '1' in 0-based indexing)
        if (q[0] != 0) {
            do {
                int k = q[0];
                // Natively reverse the first k + 1 elements
                reverse(q.begin(), q.begin() + k + 1);
                flips++;
            } while (q[0] != 0);
        }

        // Keep running totals natively
        max_flips = max(max_flips, flips);
        checksum += sign * flips;
        
        // Toggle sign for the next permutation's checksum (even vs odd index parity)
        sign = -sign;

        // Generate the next permutation using Fannkuch's shift-rotation algorithm
        int i = 1;
        while (i < n) {
            int first = p[0];
            // Shift elements left by 1
            for (int j = 0; j < i; ++j) {
                p[j] = p[j + 1];
            }
            p[i] = first;

            count[i]++;
            if (count[i] <= i) break;
            
            // Reset counter and move to the next position
            count[i] = 0;
            i++;
        }
        
        // If we have shifted all the way to the end, all n! permutations are done
        if (i == n) break; 
    }

    // Output strictly matching the benchmark game's format
    cout << checksum << "\n";
    cout << "Pfannkuchen(" << n << ") = " << max_flips << "\n";

    return 0;
}