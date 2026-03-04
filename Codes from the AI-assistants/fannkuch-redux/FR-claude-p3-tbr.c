/* The Computer Language Benchmarks Game
 * https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
 *
 * contributed by Ledrug Katz
 * modified by Brendan Miller
 * optimized for fannkuch-redux benchmark
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef int32_t int_t;

/* Function to reverse elements from index 0 to k */
static inline void rotate(int_t *p, int_t k)
{
    int_t i, j, t;
    for (i = 0, j = k; i < j; i++, j--) {
        t = p[i];
        p[i] = p[j];
        p[j] = t;
    }
}

/* Count flips for current permutation */
static inline int_t count_flips(int_t *p, int_t n)
{
    int_t q[16]; /* max n is typically 12-13 */
    int_t i, flips;
    int_t first;
    
    /* Copy permutation */
    for (i = 0; i < n; i++)
        q[i] = p[i];
    
    flips = 0;
    while ((first = q[0]) != 0) {
        rotate(q, first);
        flips++;
    }
    
    return flips;
}

/* Generate next permutation using Heap's algorithm */
int fannkuch(int_t n)
{
    int_t p[16], count[16];
    int_t maxflips, flips, checksum;
    int_t i, k, r, perm_index;
    int_t sign;
    
    /* Initialize permutation and count array */
    for (i = 0; i < n; i++) {
        p[i] = i;
        count[i] = 0;
    }
    
    maxflips = 0;
    checksum = 0;
    perm_index = 0;
    sign = 1;
    
    do {
        /* Count flips for current permutation */
        flips = count_flips(p, n);
        
        if (flips > maxflips)
            maxflips = flips;
        
        checksum += sign * flips;
        sign = -sign;
        
        /* Generate next permutation using Heap's algorithm */
        k = 1;
        while (k < n) {
            if (count[k] < k) {
                /* Determine swap based on parity */
                if (k & 1) { /* k is odd */
                    i = count[k];
                } else { /* k is even */
                    i = 0;
                }
                
                /* Swap elements */
                int_t tmp = p[i];
                p[i] = p[k];
                p[k] = tmp;
                
                count[k]++;
                k = 1;
                break;
            } else {
                count[k] = 0;
                k++;
            }
        }
        
        if (k >= n)
            break;
            
        perm_index++;
        
    } while (1);
    
    printf("%d\n", checksum);
    return maxflips;
}

int main(int argc, char **argv)
{
    int_t n = argc > 1 ? atoi(argv[1]) : 7;
    
    if (n < 3 || n > 16) {
        fprintf(stderr, "n must be between 3 and 16\n");
        return 1;
    }
    
    printf("Pfannkuchen(%d) = %d\n", n, fannkuch(n));
    
    return 0;
}