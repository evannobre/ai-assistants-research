#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * fannkuch-redux (sequential, native libc only)
 * Computes:
 *   checksum and maxFlips for permutations of 0..n-1
 */

static inline void rotate_left_1(int *a, int len) {
    int first = a[0];
    memmove(a, a + 1, (size_t)(len - 1) * sizeof(int));
    a[len - 1] = first;
}

static inline void reverse_prefix(int *a, int k) {
    // reverse a[0..k] inclusive
    int i = 0, j = k;
    while (i < j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
        ++i; --j;
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s n\n", argv[0]);
        return 2;
    }

    int n = atoi(argv[1]);
    if (n < 0) return 2;

    // Conventionally, benchmarks use n up to ~12..13 in C for sequential runs.
    // This code still works for larger n but runtime grows factorially.
    int *perm1 = (int *)malloc((size_t)n * sizeof(int));
    int *perm  = (int *)malloc((size_t)n * sizeof(int));
    int *count = (int *)calloc((size_t)n, sizeof(int));
    if (!perm1 || !perm || !count) {
        fprintf(stderr, "out of memory\n");
        free(perm1); free(perm); free(count);
        return 1;
    }

    for (int i = 0; i < n; ++i) perm1[i] = i;

    int maxFlips = 0;
    long long checksum = 0;

    // r indicates which count slot we’re working with
    int r = n;
    int permCount = 0;

    for (;;) {
        // Ensure count[] initialized for current r expansion
        while (r > 1) {
            count[r - 1] = r;
            --r;
        }

        // Copy perm1 -> perm
        memcpy(perm, perm1, (size_t)n * sizeof(int));

        int flips = 0;
        if (n > 0 && perm[0] != 0) {
            while (perm[0] != 0) {
                int k = perm[0];
                reverse_prefix(perm, k);
                ++flips;
            }
        }

        if (flips > maxFlips) maxFlips = flips;

        // Alternating checksum by permutation index parity
        if ((permCount & 1) == 0) checksum += flips;
        else                      checksum -= flips;

        ++permCount;

        // Generate next permutation in “count” order
        for (;;) {
            if (r == n) {
                // exhausted all permutations
                printf("%lld\nPfannkuchen(%d) = %d\n", checksum, n, maxFlips);
                free(perm1); free(perm); free(count);
                return 0;
            }

            // Rotate first (r+1) left by 1
            rotate_left_1(perm1, r + 1);

            // Decrement count[r]; if still > 0, we have next perm1 ready
            if (--count[r] > 0) {
                break;
            }

            // Otherwise carry to next r
            ++r;
        }

        // Reset r back down to 1.. for next evaluation phase
        r = 1;
    }
}
