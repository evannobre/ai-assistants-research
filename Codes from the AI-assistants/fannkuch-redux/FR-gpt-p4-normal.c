// fannkuch-redux (single-threaded) - C99
// Build: gcc -O2 -std=c99 -march=native fannkuch.c -o fannkuch
// Run:   ./fannkuch 12

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline void reverse_prefix(int *a, int k) {
    // reverse a[0..k] inclusive
    int i = 0, j = k;
    while (i < j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
        i++; j--;
    }
}

static inline void rotate_left_prefix(int *a, int r) {
    // rotate left a[0..r] by 1 position
    // [x0 x1 x2 ... xr] -> [x1 x2 ... xr x0]
    int first = a[0];
    memmove(a, a + 1, (size_t)r * sizeof(int));
    a[r] = first;
}

int main(int argc, char **argv) {
    int n = 0;
    if (argc > 1) n = atoi(argv[1]);
    if (n <= 0) n = 7;          // conventional default in some benchmarks
    if (n > 16) {
        // n grows as n!; keep it reasonable for 8GB RAM + runtime
        fprintf(stderr, "n too large (try <= 16)\n");
        return 1;
    }

    int *perm1 = (int *)malloc((size_t)n * sizeof(int));
    int *perm  = (int *)malloc((size_t)n * sizeof(int));
    int *count = (int *)malloc((size_t)n * sizeof(int));
    if (!perm1 || !perm || !count) {
        fprintf(stderr, "allocation failed\n");
        return 1;
    }

    for (int i = 0; i < n; i++) perm1[i] = i;
    for (int i = 0; i < n; i++) count[i] = i + 1;

    int max_flips = 0;
    long long checksum = 0;
    int sign = 1;

    while (1) {
        // ---- count flips for current permutation ----
        int flips = 0;

        if (perm1[0] != 0) {
            memcpy(perm, perm1, (size_t)n * sizeof(int));

            while (perm[0] != 0) {
                int k = perm[0];
                reverse_prefix(perm, k);
                flips++;
            }

            checksum += (long long)sign * (long long)flips;
            if (flips > max_flips) max_flips = flips;
        }

        // ---- generate next permutation (same benchmark-style iterative scheme) ----
        if (sign == 1) {
            // swap first two elements
            int t = perm1[0]; perm1[0] = perm1[1]; perm1[1] = t;
            sign = -1;
        } else {
            // swap elements 1 and 2
            int t = perm1[1]; perm1[1] = perm1[2]; perm1[2] = t;
            sign = 1;

            // apply rotation counters
            int r = 2;
            while (r < n) {
                if (count[r] > 1) {
                    count[r]--;
                    rotate_left_prefix(perm1, r);
                    break;
                }
                count[r] = r + 1;
                rotate_left_prefix(perm1, r);
                r++;
            }
            if (r >= n) break; // finished all permutations
        }
    }

    // Output format commonly expected by Benchmarks Game variants:
    // first line: checksum
    // second line: "Pfannkuchen(n) = max"
    printf("%lld\n", checksum);
    printf("Pfannkuchen(%d) = %d\n", n, max_flips);

    free(perm1);
    free(perm);
    free(count);
    return 0;
}
