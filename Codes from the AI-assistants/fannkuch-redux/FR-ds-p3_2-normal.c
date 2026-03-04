#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    int max_flips;
    int checksum;
} Result;

Result fannkuch_redux(int n) {
    Result result = {0, 0};
    
    if (n < 1) {
        return result;
    }
    
    // Allocate memory on stack for speed (fits within 8GB constraint for n<=12)
    int permutation[12];
    int temp[12];
    int count[12] = {0};
    
    // Initialize permutation
    for (int i = 0; i < n; i++) {
        permutation[i] = i + 1;
    }
    
    int r = n;
    int perm_count = 0;
    
    while (1) {
        // Count flips for current permutation
        while (r != 1) {
            count[r-1] = r;
            r--;
        }
        
        int first = permutation[0];
        if (first != 1) {
            // Make a copy for flipping
            memcpy(temp, permutation, n * sizeof(int));
            
            int flips = 0;
            int k = first;
            
            while (k != 1) {
                // Reverse first k elements
                int i = 0, j = k - 1;
                while (i < j) {
                    int t = temp[i];
                    temp[i] = temp[j];
                    temp[j] = t;
                    i++;
                    j--;
                }
                flips++;
                k = temp[0];
            }
            
            if (flips > result.max_flips) {
                result.max_flips = flips;
            }
            
            if (perm_count % 2 == 0) {
                result.checksum += flips;
            } else {
                result.checksum -= flips;
            }
        }
        
        // Generate next permutation
        while (1) {
            if (r == n) {
                return result;
            }
            
            // Permute
            int perm0 = permutation[0];
            int i = 0;
            while (i < r) {
                permutation[i] = permutation[i + 1];
                i++;
            }
            permutation[r] = perm0;
            
            count[r]--;
            if (count[r] > 0) break;
            r++;
        }
        
        perm_count++;
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <n>\n", argv[0]);
        return 1;
    }
    
    int n = atoi(argv[1]);
    if (n < 0 || n > 12) {
        fprintf(stderr, "Error: n must be between 0 and 12\n");
        return 1;
    }
    
    Result result = fannkuch_redux(n);
    printf("%d\nPfannkuchen(%d) = %d\n", result.checksum, n, result.max_flips);
    
    return 0;
}