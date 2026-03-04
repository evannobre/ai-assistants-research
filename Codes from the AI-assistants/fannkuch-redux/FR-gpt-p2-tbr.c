// fannkuch-redux (single-threaded, iterative)
// Build: gcc -O3 -march=native -std=c11 fannkuch.c -o fannkuch
// Run:   ./fannkuch 12

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static inline void reverse_prefix(int *a, int k) {
    // reverse a[0..k]
    int i = 0, j = k;
    while (i < j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
        i++; j--;
    }
}

static inline int count_flips(const int *perm, int n, int *tmp) {
    // Copy perm into tmp
    for (int i = 0; i < n; i++) tmp[i] = perm[i];

    int flips = 0;
    while (tmp[0] != 0) {
        int k = tmp[0];
        reverse_prefix(tmp, k);
        flips++;
    }
    return flips;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s n\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    if (n < 1) {
        fprintf(stderr, "n must be >= 1\n");
        return 1;
    }
    // Practical note: n! grows extremely fast; typical benchmark n is <= 12.
    if (n > 15) {
        fprintf(stderr, "warning: n=%d will take a very long time (n! growth)\n", n);
    }

    int *perm  = (int*)malloc((size_t)n * sizeof(int));
    int *tmp   = (int*)malloc((size_t)n * sizeof(int));
    int *count = (int*)calloc((size_t)n, sizeof(int));
    if (!perm || !tmp || !count) {
        fprintf(stderr, "allocation failed\n");
        free(perm); free(tmp); free(count);
        return 1;
    }

    // perm = [0..n-1]
    for (int i = 0; i < n; i++) perm[i] = i;

    // total permutations = n!
    uint64_t fact = 1;
    for (int i = 2; i <= n; i++) fact *= (uint64_t)i;

    int max_flips = 0;
    int64_t checksum = 0;

    for (uint64_t idx = 0; idx < fact; idx++) {
        // Optional fast-skip often used in fannkuch-redux:
        // if perm[0] == 0 => flips=0; also if perm[n-1] == n-1, flips tends to be small,
        // but the safe skip is only perm[0] == 0.
        int flips = 0;
        if (perm[0] != 0) {
            flips = count_flips(perm, n, tmp);
            if (flips > max_flips) max_flips = flips;
        }

        if ((idx & 1ULL) == 0ULL) checksum += flips;
        else                      checksum -= flips;

        // Generate next permutation using count[] and prefix rotations
        // Find i such that count[i] < i
        int i = 1;
        while (i < n && count[i] == i) {
            count[i] = 0;
            i++;
        }
        if (i >= n) break; // finished

        count[i]++;

        // Left-rotate the first (i+1) elements by 1:
        // [a0,a1,...,ai] -> [a1,a2,...,ai,a0]
        int first = perm[0];
        for (int j = 0; j < i; j++) perm[j] = perm[j + 1];
        perm[i] = first;
    }

    printf("%" PRId64 "\n", checksum);
    printf("Pfannkuchen(%d) = %d\n", n, max_flips);

    free(perm);
    free(tmp);
    free(count);
    return 0;
}
