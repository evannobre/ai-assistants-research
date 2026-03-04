// fannkuch-redux (single-threaded, C99)
// Build: gcc -O3 -march=native -std=c99 fannkuch.c -o fannkuch
// Run:   ./fannkuch 12

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline void reverse_prefix(int *a, int k) {
    // reverse a[0..k] inclusive
    int i = 0;
    while (i < k) {
        int t = a[i];
        a[i] = a[k];
        a[k] = t;
        i++;
        k--;
    }
}

// Generate the next permutation in the Benchmarks Game "rotate by level" order.
// Returns 1 if a next permutation exists, 0 if finished.
static inline int next_permutation_fannkuch(int *perm1, int *count, int n) {
    int i = 1;

    // Step at level 1: swap first two, increment count[1]
    int t = perm1[0];
    perm1[0] = perm1[1];
    perm1[1] = t;
    count[1]++;

    // Carry if overflow: count[i] may go beyond i
    while (i < n && count[i] > i) {
        count[i] = 0;
        i++;
        if (i >= n) return 0;

        // rotate-left the first (i+1) elements by one:
        // [x0,x1,...,xi] -> [x1,...,xi,x0]
        int first = perm1[0];
        // shift left positions 0..i-1 from 1..i
        memmove(&perm1[0], &perm1[1], (size_t)i * sizeof(int));
        perm1[i] = first;

        count[i]++;
    }

    return 1;
}

int main(int argc, char **argv) {
    int n = 12;
    if (argc > 1) n = atoi(argv[1]);
    if (n < 0 || n > 12) {
        // n=12 is the typical performance parameter; keep bounds small and safe.
        fprintf(stderr, "Usage: %s [n], with 0 <= n <= 12\n", argv[0]);
        return 1;
    }
    if (n < 2) {
        printf("0\nPfannkuchen(%d) = 0\n", n);
        return 0;
    }

    int perm1[12], perm[12], count[12];

    for (int i = 0; i < n; i++) perm1[i] = i;
    for (int i = 0; i < n; i++) count[i] = 0;

    int max_flips = 0;
    int checksum = 0;
    int perm_index = 0;

    for (;;) {
        int flips = 0;

        if (perm1[0] != 0) {
            memcpy(perm, perm1, (size_t)n * sizeof(int));

            while (perm[0] != 0) {
                int k = perm[0];
                reverse_prefix(perm, k);
                flips++;
            }

            if (flips > max_flips) max_flips = flips;
        }

        // alternating-sign checksum by permutation index
        if ((perm_index & 1) == 0) checksum += flips;
        else checksum -= flips;

        perm_index++;

        if (!next_permutation_fannkuch(perm1, count, n)) break;
    }

    printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, max_flips);
    return 0;
}
