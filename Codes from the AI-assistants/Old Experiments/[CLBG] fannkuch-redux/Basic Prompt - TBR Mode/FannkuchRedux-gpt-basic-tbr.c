#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc, char** argv) {
    int n = (argc>1) ? atoi(argv[1]) : 7;
    int *perm1 = malloc(n * sizeof(int));
    int *perm  = malloc(n * sizeof(int));
    int *count = malloc(n * sizeof(int));
    for (int i=0;i<n;i++) { perm1[i]=i; count[i]=0; }
    int checksum = 0;
    int maxflips = 0;
    int sign = 1;

    while (1) {
        memcpy(perm, perm1, n * sizeof(int));

        int flips = 0;
        if (perm[0] != 0) {
            while (perm[0] != 0) {
                int k = perm[0];
                int i=0, j=k;
                while (i < j) {
                    int t = perm[i]; perm[i] = perm[j]; perm[j] = t;
                    i++; j--;
                }
                flips++;
            }
        }
        checksum += sign * flips;
        if (flips > maxflips) maxflips = flips;

        // next permutation
        int i = 1;
        for (; i < n; ++i) {
            count[i]++;
            if (count[i] <= i) {
                int first = perm1[0];
                for (int j = 0; j < i; ++j) perm1[j] = perm1[j+1];
                perm1[i] = first;
                break;
            } else {
                count[i] = 0;
            }
        }
        if (i == n) break;
        sign = -sign;
    }

    printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, maxflips);

    free(perm1); free(perm); free(count);
    return 0;
}
