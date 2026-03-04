/* 
 * Fannkuch-Redux benchmark
 * Compile: gcc -O3 -o fannkuch fannkuch.c
 * Usage: ./fannkuch <n>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline void reverse(int *arr, int len) {
    int i, tmp;
    for (i = 0; i < len / 2; i++) {
        tmp = arr[i];
        arr[i] = arr[len - 1 - i];
        arr[len - 1 - i] = tmp;
    }
}

void fannkuch(int n) {
    int *perm = malloc(n * sizeof(int));
    int *perm1 = malloc(n * sizeof(int));
    int *count = malloc(n * sizeof(int));
    
    int i, k, flips, first, tmp;
    int max_flips = 0;
    int checksum = 0;
    int perm_count = 0;
    int sign = 1;
    
    // Initialize
    for (i = 0; i < n; i++) {
        perm1[i] = i;
        count[i] = i;
    }
    
    while (1) {
        // Count flips
        flips = 0;
        first = perm1[0];
        
        if (first != 0) {
            memcpy(perm, perm1, n * sizeof(int));
            
            while (1) {
                flips++;
                reverse(perm, first + 1);
                first = perm[0];
                if (first == 0) break;
            }
            
            if (flips > max_flips) {
                max_flips = flips;
            }
            checksum += sign * flips;
        }
        
        // Next permutation
        if (perm_count >= n) break;
        
        if (perm_count < n) {
            sign = -sign;
            perm_count++;
        }
        
        // Generate next permutation
        int done = 0;
        k = 1;
        while (k < n) {
            count[k]--;
            if (count[k] > 0) break;
            
            if (k == n - 1) {
                done = 1;
                break;
            }
            
            count[k] = k + 1;
            
            // Rotate
            tmp = perm1[0];
            for (i = 0; i <= k; i++) {
                perm1[i] = perm1[i + 1];
            }
            perm1[k + 1] = tmp;
            
            k++;
        }
        
        if (done) break;
    }
    
    printf("%d\n", checksum);
    printf("Pfannkuchen(%d) = %d\n", n, max_flips);
    
    free(perm);
    free(perm1);
    free(count);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <n>\n", argv[0]);
        return 1;
    }
    
    int n = atoi(argv[1]);
    
    if (n < 3 || n > 12) {
        fprintf(stderr, "n must be between 3 and 12\n");
        return 1;
    }
    
    fannkuch(n);
    return 0;
}