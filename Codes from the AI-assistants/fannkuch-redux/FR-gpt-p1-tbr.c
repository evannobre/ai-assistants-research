#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
  fannkuch-redux:
  - enumerate permutations of 0..n-1
  - for each permutation, compute flips (prefix reversals) until first element is 0
  - checksum: alternating sum of flips based on permutation index
  - maxFlips: maximum flips over all permutations
*/

static inline void reverse_prefix(int *a, int k) {
    // reverse a[0..k]
    for (int i = 0, j = k; i < j; i++, j--) {
        int tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
    }
}

int main(int argc, char **argv) {
    int n = (argc > 1) ? atoi(argv[1]) : 0;
    if (n <= 0) {
        fprintf(stderr, "Usage: %s <n>\n", argv[0]);
        return 1;
    }

    int *perm1 = (int *)malloc((size_t)n * sizeof(int));
    int *perm  = (int *)malloc((size_t)n * sizeof(int));
    int *count = (int *)malloc((size_t)n * sizeof(int));
    if (!perm1 || !perm || !count) {
        fprintf(stderr, "Out of memory\n");
        free(perm1); free(perm); free(count);
        return 1;
    }

    for (int i = 0; i < n; i++) perm1[i] = i;

    long long checksum = 0;
    int maxFlips = 0;

    // permutation index (for alternating checksum sign)
    long long permCount = 0;

    // r is the "active" prefix length (0..n-1 index)
    int r = n;
    while (1) {
        // Initialize counters when r decreases down to 1
        while (r != 1) {
            count[r - 1] = r;
            r--;
        }

        // Compute flips for current perm1 if it’s not trivially zero-flip
        if (perm1[0] != 0) {
            memcpy(perm, perm1, (size_t)n * sizeof(int));

            int flips = 0;
            while (perm[0] != 0) {
                int k = perm[0];
                reverse_prefix(perm, k);
                flips++;
            }

            if (flips > maxFlips) maxFlips = flips;
            if ((permCount & 1LL) == 0) checksum += flips;
            else                      checksum -= flips;
        } else {
            // flips == 0 contributes nothing; checksum unchanged
        }

        // Generate next permutation (carry/rotate)
        while (1) {
            if (r == n) {
                // done: all permutations generated
                printf("%lld\n", checksum);
                printf("Pfannkuchen(%d) = %d\n", n, maxFlips);
                free(perm1); free(perm); free(count);
                return 0;
            }

            // rotate left perm1[0..r]
            int first = perm1[0];
            for (int i = 0; i < r; i++) perm1[i] = perm1[i + 1];
            perm1[r] = first;

            count[r]--;
            if (count[r] > 0) break; // next permutation ready

            r++; // carry
        }

        permCount++;
    }
}
