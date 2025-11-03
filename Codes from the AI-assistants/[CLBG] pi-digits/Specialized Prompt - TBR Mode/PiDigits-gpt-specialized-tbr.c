/*
 * pi_spigot.c
 *
 * Generate the first N digits of pi using the Rabinowitz–Wagon spigot algorithm,
 * in two modes: extract(3) (base=1000) or extract(4) (base=10000).
 *
 * Usage: ./pi_spigot N mode
 *    N    = number of digits to compute
 *    mode = 3 (for 3‑digit blocks) or 4 (for 4‑digit blocks)
 *
 * Prints 10 digits per line followed by the total digits generated so far.
 *
 * Requires: GMP library (sudo apt install libgmp-dev)
 * Compile with:
 *    gcc -O2 -std=c99 -Wall -lgmp -o pi_spigot pi_spigot.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

void spigot_pi(unsigned long N, int digits_per_block) {
    // array length = floor(10*N/3) + 1
    long len = (10 * N) / 3 + 1;
    // allocate and initialize a[i] = 2
    mpz_t *a = malloc(len * sizeof(mpz_t));
    for (long i = 0; i < len; i++) {
        mpz_init_set_ui(a[i], 2);
    }

    mpz_t q, r, tmp, base;
    mpz_init(q);
    mpz_init(r);
    mpz_init(tmp);
    mpz_init(base);

    // base = 10^digits_per_block
    mpz_ui_pow_ui(base, 10, digits_per_block);

    unsigned long count = 0, total = 0;
    unsigned long blocks = (N + digits_per_block - 1) / digits_per_block;

    for (unsigned long blk = 0; blk < blocks; blk++) {
        mpz_set_ui(q, 0);

        // inner reduction loop
        for (long i = len; i > 0; i--) {
            long idx = i - 1;
            // r = base * a[idx] + q * i
            mpz_mul(r, a[idx], base);
            mpz_mul_ui(tmp, q, i);
            mpz_add(r, r, tmp);

            unsigned long denom = 2 * i - 1;
            // a[idx] = r % denom
            mpz_mod_ui(a[idx], r, denom);
            // q = r / denom
            mpz_tdiv_q_ui(q, r, denom);
        }

        // q now holds the next block of digits
        char *blkstr = mpz_get_str(NULL, 10, q);

        // pad with leading zeros if needed
        size_t lenstr = strlen(blkstr);
        if (lenstr < (size_t)digits_per_block) {
            char *p = malloc(digits_per_block + 1);
            memset(p, '0', digits_per_block - lenstr);
            memcpy(p + (digits_per_block - lenstr), blkstr, lenstr + 1);
            free(blkstr);
            blkstr = p;
        }

        // output each digit, up to N
        for (int d = 0; d < digits_per_block && total < N; d++) {
            putchar(blkstr[d]);
            if (++count == 10) {
                printf(" %10lu\n", ++total);
                count = 0;
            } else {
                total++;
            }
        }
        free(blkstr);
    }

    // final newline if last line wasn’t full
    if (count != 0) {
        while (count++ < 10) putchar(' ');
        printf(" %10lu\n", total);
    }

    // cleanup
    for (long i = 0; i < len; i++) mpz_clear(a[i]);
    free(a);
    mpz_clears(q, r, tmp, base, NULL);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr,
            "Usage: %s <N> <mode>\n"
            "  N    = number of digits to generate\n"
            "  mode = 3 (extract(3), base=10^3) or 4 (extract(4), base=10^4)\n",
            argv[0]);
        return EXIT_FAILURE;
    }
    unsigned long N = strtoul(argv[1], NULL, 10);
    int mode = atoi(argv[2]);
    if ((mode != 3 && mode != 4) || N == 0) {
        fprintf(stderr, "Invalid arguments.  N must be >0, mode must be 3 or 4.\n");
        return EXIT_FAILURE;
    }
    spigot_pi(N, mode);
    return EXIT_SUCCESS;
}
