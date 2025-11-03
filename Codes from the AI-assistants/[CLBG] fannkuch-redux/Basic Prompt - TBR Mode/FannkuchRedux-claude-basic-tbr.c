#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Reverse the first k elements of the array
static inline void reverse(int *arr, int k) {
    for (int i = 0, j = k - 1; i < j; i++, j--) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

// Count flips for a given permutation
static int count_flips(int *perm, int n) {
    int flips = 0;
    int first = perm[0];
    
    if (first == 1) return 0;
    
    // Create a working copy
    int work[n];
    memcpy(work, perm, n * sizeof(int));
    
    while (work[0] != 1) {
        reverse(work, work[0]);
        flips++;
    }
    
    return flips;
}

// Generate next permutation using Heap's algorithm approach
// Returns 1 if there's a next permutation, 0 if we're done
static int next_permutation(int *perm, int *count, int n) {
    int i = 1;
    
    while (i < n) {
        if (count[i] < i) {
            // Swap based on parity of i
            int j = (i & 1) ? count[i] : 0;
            int temp = perm[i];
            perm[i] = perm[j];
            perm[j] = temp;
            count[i]++;
            return 1;
        } else {
            count[i] = 0;
            i++;
        }
    }
    return 0;
}

void fannkuch(int n) {
    // Initialize permutation {1, 2, 3, ..., n}
    int *perm = malloc(n * sizeof(int));
    int *count = calloc(n, sizeof(int));
    
    for (int i = 0; i < n; i++) {
        perm[i] = i + 1;
    }
    
    int checksum = 0;
    int max_flips = 0;
    int perm_count = 0;
    int sign = 1;
    
    // Process first permutation
    int flips = count_flips(perm, n);
    max_flips = flips;
    checksum = sign * flips;
    perm_count++;
    sign = -sign;
    
    // Generate and process all remaining permutations
    while (next_permutation(perm, count, n)) {
        flips = count_flips(perm, n);
        
        if (flips > max_flips) {
            max_flips = flips;
        }
        
        checksum += sign * flips;
        sign = -sign;
        perm_count++;
    }
    
    printf("%d\n", checksum);
    printf("Pfannkuchen(%d) = %d\n", n, max_flips);
    
    free(perm);
    free(count);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <n>\n", argv[0]);
        return 1;
    }
    
    int n = atoi(argv[1]);
    
    if (n < 1 || n > 12) {
        fprintf(stderr, "n must be between 1 and 12\n");
        return 1;
    }
    
    fannkuch(n);
    
    return 0;
}