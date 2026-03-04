#include <stdio.h>
#include <stdlib.h>

void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s N\n", argv[0]); return 1; }
    int n = atoi(argv[1]);
    int *perm = malloc(n * sizeof(int));
    int *count = malloc(n * sizeof(int));
    int *temp = malloc(n * sizeof(int));
    if (!perm || !count || !temp) { perror("malloc"); return 2; }

    for (int i = 0; i < n; ++i) { perm[i] = i + 1; count[i] = i + 1; }

    int max_flips = 0;
    long checksum = 0;
    long perm_index = 0;

    while (1) {
        int flips = 0;
        if (perm[0] != 1) {
            for (int i = 0; i < n; ++i) temp[i] = perm[i];
            while (temp[0] != 1) {
                int k = temp[0];
                int i = 0, j = k - 1;
                while (i < j) { swap(&temp[i], &temp[j]); ++i; --j; }
                ++flips;
            }
        }
        if ((perm_index & 1) == 0) checksum += flips; else checksum -= flips;
        if (flips > max_flips) max_flips = flips;

        int i = 1;
        for (;; ++i) {
            if (i >= n) goto done;
            if (count[i] > 1) break;
            count[i] = i + 1;
            // rotate left perm[0..i]
            int first = perm[0];
            for (int j = 0; j < i; ++j) perm[j] = perm[j+1];
            perm[i] = first;
        }
        count[i]--;
        // swap perm[0] and perm[i]
        swap(&perm[0], &perm[i]);
        ++perm_index;
    }
done:
    printf("%ld\nPfannkuchen(%d) = %d\n", checksum, n, max_flips);
    free(perm); free(count); free(temp);
    return 0;
}
