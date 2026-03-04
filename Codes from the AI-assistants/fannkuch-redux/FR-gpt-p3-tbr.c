/*
 * fannkuch-redux (Benchmarks Game style)
 * - generates all n! permutations of 0..n-1
 * - for each, counts pancake flips until first element is 0
 * - checksum alternates by permutation index parity
 *
 * Build: gcc -O3 -march=native -std=c11 fannkuch.c -o fannkuch
 * Run:   ./fannkuch 12
 */

#include <stdio.h>
#include <stdlib.h>

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

static inline void rotate_left_prefix(int *a, int len) {
    // rotate left first len elements: a[0] goes to a[len-1]
    int t = a[0];
    for (int i = 0; i < len - 1; i++) a[i] = a[i + 1];
    a[len - 1] = t;
}

int main(int argc, char **argv) {
    int n = 7;
    if (argc > 1) n = atoi(argv[1]);
    if (n < 0) n = 0;

    if (n < 2) {
        // n=0 or n=1: only one permutation, flips=0
        printf("0\nPfannkuchen(%d) = 0\n", n);
        return 0;
    }

    int *perm1 = (int*)malloc((size_t)n * sizeof(int));
    int *perm  = (int*)malloc((size_t)n * sizeof(int));
    int *count = (int*)malloc((size_t)n * sizeof(int));
    if (!perm1 || !perm || !count) {
        fprintf(stderr, "Out of memory\n");
        free(perm1); free(perm); free(count);
        return 1;
    }

    for (int i = 0; i < n; i++) {
        perm1[i] = i;
        count[i] = i;
    }

    int checksum = 0;
    int maxflips = 0;
    int sign = 1;

    while (1) {
        // Count flips for current permutation (only if first != 0)
        if (perm1[0] != 0) {
            for (int i = 0; i < n; i++) perm[i] = perm1[i];

            int flips = 0;
            while (perm[0] != 0) {
                int k = perm[0];
                reverse_prefix(perm, k);
                flips++;
            }

            checksum += sign * flips;
            if (flips > maxflips) maxflips = flips;
        }

        // Generate next permutation
        if (sign == 1) {
            // swap first two
            int t = perm1[0];
            perm1[0] = perm1[1];
            perm1[1] = t;
            sign = -1;
        } else {
            // rotate left first 3
            int t = perm1[0];
            perm1[0] = perm1[1];
            perm1[1] = perm1[2];
            perm1[2] = t;
            sign = 1;

            int i;
            for (i = 2; i < n; i++) {
                int c = count[i];
                if (c > 0) {
                    count[i] = c - 1;
                    break;
                }
                count[i] = i;
                rotate_left_prefix(perm1, i + 1);
            }
            if (i == n) break; // finished all permutations
        }
    }

    printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, maxflips);

    free(perm1);
    free(perm);
    free(count);
    return 0;
}
