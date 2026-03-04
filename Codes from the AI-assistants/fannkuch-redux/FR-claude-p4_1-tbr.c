/* The Computer Language Benchmarks Game
 * https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
 *
 * Contributed by: Backend optimization specialist
 * Fannkuch-redux benchmark implementation
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Inline flip operation for maximum performance
static inline int flip(int* restrict arr, int n) {
    int flips = 0;
    int first = arr[0];
    
    while (first != 0) {
        // Reverse first 'first+1' elements
        int* left = arr;
        int* right = arr + first;
        
        while (left < right) {
            int temp = *left;
            *left++ = *right;
            *right-- = temp;
        }
        
        flips++;
        first = arr[0];
    }
    
    return flips;
}

// Generate next permutation in lexicographic order
static inline int next_permutation(int* restrict perm, int* restrict count, int n) {
    int first = 1;
    
    while (1) {
        // Rotate the first 'first' elements
        int temp = perm[0];
        for (int i = 0; i < first; i++) {
            perm[i] = perm[i + 1];
        }
        perm[first] = temp;
        
        count[first]--;
        
        if (count[first] > 0) {
            return 1;
        }
        
        count[first] = first + 1;
        first++;
        
        if (first >= n) {
            return 0;
        }
    }
}

void fannkuch(int n) {
    // Allocate arrays
    int* perm = malloc(n * sizeof(int));
    int* perm_copy = malloc(n * sizeof(int));
    int* count = malloc(n * sizeof(int));
    
    // Initialize
    for (int i = 0; i < n; i++) {
        perm[i] = i;
        count[i] = i + 1;
    }
    
    int max_flips = 0;
    int checksum = 0;
    int perm_index = 0;
    
    // Process first permutation
    memcpy(perm_copy, perm, n * sizeof(int));
    int flips = flip(perm_copy, n);
    max_flips = flips;
    checksum = flips;
    perm_index++;
    
    // Generate and process all remaining permutations
    while (next_permutation(perm, count, n)) {
        // Copy for flipping (preserve original permutation)
        memcpy(perm_copy, perm, n * sizeof(int));
        
        // Only flip if first element is not 0
        if (perm[0] != 0) {
            flips = flip(perm_copy, n);
            
            if (flips > max_flips) {
                max_flips = flips;
            }
            
            // Toggle sign based on permutation index
            if (perm_index & 1) {
                checksum -= flips;
            } else {
                checksum += flips;
            }
        }
        
        perm_index++;
    }
    
    // Output results
    printf("%d\n", checksum);
    printf("Pfannkuchen(%d) = %d\n", n, max_flips);
    
    // Cleanup
    free(perm);
    free(perm_copy);
    free(count);
}

int main(int argc, char* argv[]) {
    int n = (argc > 1) ? atoi(argv[1]) : 7;
    
    if (n < 3 || n > 12) {
        fprintf(stderr, "n should be between 3 and 12\n");
        return 1;
    }
    
    fannkuch(n);
    
    return 0;
}