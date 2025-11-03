// N is the input value (e.g., 12)
int N = 12;

// Global results
long long checksum = 0;
int max_flips = 0;

// State arrays (using native C++ structures)
std::vector<int> P(N); // The permutation {1, 2, ..., N}
std::vector<int> Count(N, 0); // Count array for permutation generation
std::vector<int> Dir(N, -1);  // Direction array (-1 left, 1 right)
long long perm_index = 0;

// --- Function to perform the flips and count them ---
int Flips(std::vector<int>& p_in) {
    // Create a working copy for the flip process (avoid modifying P directly if needed,
    // though the Fannkuch algorithm *requires* an in-place change for the *current* flip count).
    // The main loop will restore/generate the next initial permutation.
    // For maximum speed, use a second, local array copy for p_in in a real implementation.
    std::vector<int> p = p_in; // Fast copy is better than constantly restoring the original.

    int flips_count = 0;
    while (p[0] != 1) {
        int k = p[0];
        
        // Native C++: std::reverse on a sub-range (in-place)
        std::reverse(p.begin(), p.begin() + k);
        
        flips_count++;
    }
    return flips_count;
}

// --- Main Algorithm ---

// 1. Initialization
std::iota(P.begin(), P.end(), 1); // P = {1, 2, ..., N}

// 2. Main Iteration Loop
// We only need to iterate n! - 1 times after the first permutation is processed.
while (perm_index < factorial(N)) { // factorial(N) is N!
    
    // A. Process Current Permutation
    int flips = Flips(P);
    
    // Update results
    max_flips = std::max(max_flips, flips);
    if (perm_index % 2 == 0) {
        checksum += flips;
    } else {
        checksum -= flips;
    }

    perm_index++;
    if (perm_index == factorial(N)) break; // Check termination after last processed.
    
    // B. Find Largest Mobile Element (Simplified Counter-Based Generator)
    // The generation logic is often more complex than a simple counter but 
    // for this problem, we can use a direct iterative approach.
    
    int i = N - 1; 
    while (i > 0) {
        Count[i]++;
        if (Count[i] <= i) break; // Found the element to move
        
        // Reset and flip direction for 'i' if max moves reached
        Count[i] = 0;
        Dir[i] *= -1; 
        i--;
    }
    
    if (i == 0) break; // All permutations generated (should be redundant if loop condition is N!)

    // C. Perform Swap based on Count/Dir logic (i corresponds to the index to swap)
    int j = i + Dir[i];
    std::swap(P[i], P[j]); // Native C++: std::swap
}

// Final output: max_flips, checksum