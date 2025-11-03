// fannkuch.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    int n = (argc > 1) ? atoi(argv[1]) : 7;
    int i, j, k;

    int *perm = malloc(n * sizeof(int));
    int *perm1 = malloc(n * sizeof(int));
    int *count = malloc(n * sizeof(int));
    int *temp = malloc(n * sizeof(int));
    if (!perm || !perm1 || !count || !temp) { perror("alloc"); return 1; }

    for (i = 0; i < n; ++i) perm1[i] = i + 1;
    for (i = 0; i < n; ++i) {
        perm[i] = perm1[i];
        count[i] = i;
    }

    int maxflips = 0;
    int checksum = 0;
    int sign = 1;

    while (1) {
        // copy perm -> temp for flipping
        memcpy(temp, perm, n * sizeof(int));

        // count flips
        int flips = 0;
        while (temp[0] != 1) {
            k = temp[0];
            // reverse prefix of length k
            for (i = 0, j = k - 1; i < j; ++i, --j) {
                int t = temp[i]; temp[i] = temp[j]; temp[j] = t;
            }
            flips++;
            if (flips > n) break; // safety
        }
        checksum += sign * flips;
        if (flips > maxflips) maxflips = flips;

        // generate next permutation using count (odometer)
        int idx = 1;
        while (idx < n) {
            if (count[idx] > 0) {
                // rotate first idx+1 elements left by 1
                int first = perm[0];
                for (i = 0; i < idx; ++i) perm[i] = perm[i + 1];
                perm[idx] = first;

                count[idx]--;
                sign = -sign;
                break;
            } else {
                count[idx] = idx;
                idx++;
            }
        }
        if (idx >= n) break; // done
    }

    printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, maxflips);

    free(perm); free(perm1); free(count); free(temp);
    return 0;
}
