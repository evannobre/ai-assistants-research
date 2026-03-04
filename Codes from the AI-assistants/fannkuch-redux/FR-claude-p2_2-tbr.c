/* fannkuch-redux.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline void reverse(int *arr, int n) {
    int i, tmp;
    for (i = 0; i < n / 2; i++) {
        tmp = arr[i];
        arr[i] = arr[n - i - 1];
        arr[n - i - 1] = tmp;
    }
}

void fannkuch(int n, int *max_flips, int *checksum) {
    int *perm = malloc(n * sizeof(int));
    int *perm1 = malloc(n * sizeof(int));
    int *count = malloc(n * sizeof(int));
    
    // Initialize
    for (int i = 0; i < n; i++) {
        perm[i] = i;
        count[i] = i + 1;
    }
    
    *max_flips = 0;
    *checksum = 0;
    int sign = 1;
    
    while (1) {
        // Count flips
        int flips = 0;
        int k = perm[0];
        
        if (k != 0) {
            memcpy(perm1, perm, n * sizeof(int));
            
            while (k != 0) {
                reverse(perm1, k + 1);
                flips++;
                k = perm1[0];
            }
            
            if (flips > *max_flips) {
                *max_flips = flips;
            }
            *checksum += sign * flips;
        }
        
        sign = -sign;
        
        // Generate next permutation
        int i = 1;
        int done = 1;
        
        while (i < n) {
            int first = perm[0];
            for (int j = 0; j < i; j++) {
                perm[j] = perm[j + 1];
            }
            perm[i] = first;
            
            count[i]--;
            if (count[i] > 0) {
                done = 0;
                break;
            }
            
            count[i] = i + 1;
            i++;
        }
        
        if (done) break;
    }
    
    free(perm);
    free(perm1);
    free(count);
}

int main(int argc, char *argv[]) {
    int n = (argc > 1) ? atoi(argv[1]) : 7;
    
    if (n < 3 || n > 12) {
        fprintf(stderr, "n must be between 3 and 12\n");
        return 1;
    }
    
    int max_flips, checksum;
    fannkuch(n, &max_flips, &checksum);
    
    printf("%d\n", checksum);
    printf("Pfannkuchen(%d) = %d\n", n, max_flips);
    
    return 0;
}