#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv){
    int n = 7;
    if (argc > 1) n = atoi(argv[1]);
    if (n < 1) return 1;

    int *p = malloc(n * sizeof(int));
    int *p_copy = malloc(n * sizeof(int));
    int *count = malloc(n * sizeof(int));
    if (!p || !p_copy || !count) return 1;

    for (int i = 0; i < n; ++i) p[i] = i + 1;
    for (int i = 0; i < n; ++i) count[i] = 0;

    int maxflips = 0;
    long checksum = 0;
    int sign = 1; // +1 for even permutation index, −1 for odd

    long permutations = 1;
    for (int i = 2; i <= n; ++i) permutations *= i;

    for (long perm = 0; perm < permutations; ++perm) {
        // Count flips for current permutation p
        for (int i = 0; i < n; ++i) p_copy[i] = p[i];
        int flips = 0;
        int first;
        while ((first = p_copy[0]) != 1) {
            // reverse prefix of length first
            int i = 0, j = first - 1;
            while (i < j) {
                int tmp = p_copy[i];
                p_copy[i] = p_copy[j];
                p_copy[j] = tmp;
                ++i; --j;
            }
            ++flips;
        }
        checksum += sign * flips;
        if (flips > maxflips) maxflips = flips;

        // generate next permutation in factoradic-like order
        // this loop emulates the typical fannkuch generator
        int i = 1;
        while (i < n) {
            count[i]++;
            if (count[i] <= i) {
                // rotate left the prefix 0..i
                int first_val = p[0];
                for (int j = 0; j < i; ++j) p[j] = p[j+1];
                p[i] = first_val;
                sign = -sign;
                break;
            } else {
                count[i] = 0;
                ++i;
            }
        }
        if (i >= n) break;
    }

    printf("%ld\nPfannkuchen(%d) = %d\n", checksum, n, maxflips);

    free(p); free(p_copy); free(count);
    return 0;
}