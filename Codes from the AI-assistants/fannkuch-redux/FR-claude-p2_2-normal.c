/* fannkuch_redux.c - Optimized implementation */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int checksum;
    int maxflips;
} Result;

Result fannkuch_redux(int n) {
    int perm[16], perm1[16], count[16];
    int maxflips = 0, checksum = 0;
    int sign = 1, perm_count = 0;
    
    // Initialize arrays
    for (int i = 0; i < n; i++) {
        perm[i] = i;
        perm1[i] = i;
        count[i] = n - i;
    }
    
    while (1) {
        // Count flips for current permutation
        if (perm1[0] != 0) {
            memcpy(perm, perm1, n * sizeof(int));
            int flips = 0;
            
            while (1) {
                int k = perm[0];
                if (k == 0) break;
                
                // Reverse first k+1 elements
                for (int i = 0, j = k; i < j; i++, j--) {
                    int temp = perm[i];
                    perm[i] = perm[j];
                    perm[j] = temp;
                }
                flips++;
            }
            
            if (flips > maxflips) maxflips = flips;
            checksum += sign * flips;
        }
        
        // Generate next permutation
        if (perm_count == n - 1) break;
        
        sign = -sign;
        perm_count++;
        
        // Swap first two elements
        int temp = perm1[0];
        perm1[0] = perm1[1];
        perm1[1] = temp;
        
        int i = 1;
        while (count[i] == 0) {
            count[i] = i + 1;
            i++;
            
            // Rotate elements
            int first = perm1[0];
            for (int j = 0; j <= i; j++) {
                perm1[j] = perm1[j + 1];
            }
            perm1[i + 1] = first;
            
            if (i >= n - 1) {
                Result result = {checksum, maxflips};
                return result;
            }
        }
        count[i]--;
    }
    
    Result result = {checksum, maxflips};
    return result;
}

int main(int argc, char *argv[]) {
    int n = (argc > 1) ? atoi(argv[1]) : 7;
    
    if (n < 3 || n > 12) {
        fprintf(stderr, "n should be between 3 and 12\n");
        if (n > 12) {
            fprintf(stderr, "Warning: values above 12 may be slow\n");
        }
    }
    
    Result result = fannkuch_redux(n);
    
    printf("%d\n", result.checksum);
    printf("Pfannkuchen(%d) = %d\n", n, result.maxflips);
    
    return 0;
}