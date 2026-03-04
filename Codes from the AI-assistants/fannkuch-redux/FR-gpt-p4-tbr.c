// fannkuch-redux (single-thread, native C stdlib)
// Order of permutation generation: Tompkin–Paige iterative method
// Output format: checksum then "Pfannkuchen(n) = maxflips"
//
// Compile (Ubuntu):
//   gcc -O3 -march=native -pipe -Wall -Wextra fannkuchredux.c -o fannkuchredux
//
// Run:
//   ./fannkuchredux 12

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define MAX_N 16

typedef int elem;

static elem s[MAX_N];
static elem t[MAX_N];

static int maxflips = 0;
static int checksum = 0;
static int odd = 0;     // toggled each permutation; used for checksum sign
static int n = 0;

static inline void rotate_prefix_left_by1(int last_index) {
    // Rotate s[0..last_index] left by 1:
    // [a0,a1,...,alast] -> [a1,a2,...,alast,a0]
    elem first = s[0];
    for (int i = 1; i <= last_index; i++) s[i - 1] = s[i];
    s[last_index] = first;
}

static int flip_count(void) {
    // Copy s -> t
    for (int i = 0; i < n; i++) t[i] = s[i];

    int flips = 0;

    // While first element != 0, reverse prefix [0..k]
    while (t[0] != 0) {
        int k = t[0];
        int i = 0, j = k;
        while (i < j) {
            elem tmp = t[i];
            t[i] = t[j];
            t[j] = tmp;
            i++; j--;
        }
        flips++;
    }
    return flips;
}

static void tompkin_paige_permute_and_measure(void) {
    // Tompkin–Paige iterative permutation generation
    // c[i] ranges 0..i and drives rotation/carry.
    int c[MAX_N] = {0};

    int i = 0;
    while (i < n) {
        rotate_prefix_left_by1(i);

        if (c[i] >= i) {
            c[i] = 0;
            i++;
            continue;
        }

        c[i]++;
        i = 1;

        odd = ~odd; // toggle sign each permutation in this generation order

        if (s[0] != 0) {
            int flips;
            // Small fast-path seen in common benchmark code:
            // if s[s[0]] == 0 then exactly 1 flip is needed.
            if (s[s[0]] == 0) flips = 1;
            else flips = flip_count();

            if (flips > maxflips) maxflips = flips;
            checksum += (odd ? -flips : flips);
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s n\n", argv[0]);
        return 1;
    }

    n = atoi(argv[1]);
    if (n < 1 || n > 12) {
        fprintf(stderr, "range: must be 1 <= n <= 12\n");
        return 1;
    }

    for (int i = 0; i < n; i++) s[i] = i;

    tompkin_paige_permute_and_measure();

    printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, maxflips);
    return 0;
}
