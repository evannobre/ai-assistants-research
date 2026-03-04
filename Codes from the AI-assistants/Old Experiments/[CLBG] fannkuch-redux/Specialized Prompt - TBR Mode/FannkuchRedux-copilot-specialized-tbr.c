// fannkuch.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

int main(int argc, char **argv) {
    int n = 12;
    if (argc > 1) {
        long v = strtol(argv[1], NULL, 10);
        if (v < 1) v = 1;
        if (v > 12) v = 12;
        n = (int)v;
    }

    int i, j, k;
    int perm[12];
    int perm_copy[12];
    int count[12];
    for (i = 0; i < n; ++i) {
        perm[i] = i + 1;
        count[i] = 0;
    }

    int maxflips = 0;
    int64_t checksum = 0;
    int64_t perm_index = 0;

    // Optional timing
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    // iterate over all permutations
    while (1) {
        // compute flips for current permutation
        memcpy(perm_copy, perm, n * sizeof(int));
        int flips = 0;
        while (perm_copy[0] != 1) {
            k = perm_copy[0];
            // reverse first k elements (k is in 1..n)
            int a = 0, b = k - 1;
            while (a < b) {
                int tmp = perm_copy[a];
                perm_copy[a] = perm_copy[b];
                perm_copy[b] = tmp;
                ++a; --b;
            }
            ++flips;
        }

        // checksum: add if perm_index even, subtract if odd
        if ((perm_index & 1) == 0) checksum += flips;
        else checksum -= flips;

        if (flips > maxflips) maxflips = flips;

        // generate next permutation using count array
        // find first i where count[i] < i, increment and rotate
        for (i = 1; i < n; ++i) {
            if (count[i] < i) break;
            count[i] = 0;
        }
        if (i >= n) break; // finished all permutations

        ++count[i];

        // rotate left first (i+1) elements by one
        int first = perm[0];
        for (j = 0; j < i; ++j) perm[j] = perm[j + 1];
        perm[i] = first;

        ++perm_index;
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double elapsed = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;

    printf("%lld\n", (long long)checksum);
    printf("Pfannkuchen(%d) = %d\n", n, maxflips);
    printf("Elapsed: %.3f sec\n", elapsed);

    return 0;
}