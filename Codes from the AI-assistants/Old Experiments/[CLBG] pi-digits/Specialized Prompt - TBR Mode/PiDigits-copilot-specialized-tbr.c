/*
 * Spigot algorithm for generating N digits of Pi.
 *
 * Based on the spigot algorithm described in the literature
 * (for example, by Rabinowitz and Wagon, and through subsequent 
 * expositions like Jeremy Gibbons’ work on unbounded spigot algorithms).
 *
 * The algorithm maintains four state variables q, r, t, and k (all arbitrary‐precision integers)
 * and uses the extraction function:
 *
 *      extract(j) = floor((j * q + r) / t)
 *
 * We compute candidate digits using extract(3) and extract(4). When they agree,
 * we output that digit. Otherwise, we “advance” the transformation state.
 *
 * The digit–production (“yield”) step updates:
 *      r := 10 * (r – t * d)
 *      q := 10 * q
 * where d is the confirmed candidate digit.
 *
 * The transformation (“next”) step is:
 *      r := (2*q + r)*k
 *      q := q * k
 *      t := t * k
 *      k := k + 1
 *
 * The program prints exactly 10 digits per line followed by a tab and the running total.
 *
 * To compile:
 *      gcc -O2 -o spigot spigot.c -lgmp
 *
 * To run (for example, to generate 10000 digits):
 *      ./spigot 10000
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

int main(int argc, char **argv) {
    // Check command-line argument for number of digits; default to 100 if not provided.
    unsigned long n;
    if (argc > 1) {
        n = strtoul(argv[1], NULL, 10);
        if(n == 0){
            fprintf(stderr, "Please provide a positive number of digits.\n");
            return 1;
        }
    } else {
        n = 100;
    }

    // Declare and initialize our multiprecision state variables.
    mpz_t q, r, t, k, tmp, y;
    mpz_inits(q, r, t, k, tmp, y, NULL);
    // Set initial values: q = 1, r = 0, t = 1, k = 1.
    mpz_set_ui(q, 1);
    mpz_set_ui(r, 0);
    mpz_set_ui(t, 1);
    mpz_set_ui(k, 1);

    // We'll also use some constant multipliers.
    mpz_t three, four, ten;
    mpz_inits(three, four, ten, NULL);
    mpz_set_ui(three, 3);
    mpz_set_ui(four, 4);
    mpz_set_ui(ten, 10);

    unsigned long count = 0;
    // Buffer for a line of digits (10 digits per line).
    char line[11];
    int lineIndex = 0;

    // Main loop: continue until we have generated n digits.
    while (count < n) {
        // STEP 1: Compute extract(3): y = floor((3*q + r) / t)
        mpz_mul_ui(tmp, q, 3);      // tmp <- 3*q
        mpz_add(tmp, tmp, r);       // tmp <- 3*q + r
        mpz_tdiv_q(y, tmp, t);      // y <- floor((3*q + r) / t)

        // STEP 2: Compute extract(4) in a temporary mpz_t:
        mpz_mul_ui(tmp, q, 4);      // tmp <- 4*q
        mpz_add(tmp, tmp, r);       // tmp <- 4*q + r
        mpz_tdiv_q(tmp, tmp, t);    // tmp <- floor((4*q + r) / t)

        // Compare the two extracts.
        if (mpz_cmp(y, tmp) == 0) {
            // They agree: we have a safe digit.
            unsigned long d = mpz_get_ui(y);  // Candidate digit d (should be 0..9).
            // Append the digit to our line buffer.
            line[lineIndex++] = '0' + (char)d;
            count++;

            // When we have 10 digits or finished outputting n digits, print the line.
            if (lineIndex == 10 || count == n) {
                line[lineIndex] = '\0';
                printf("%s\t: %lu\n", line, count);
                lineIndex = 0;
            }

            // Update the state after yielding digit d:
            // r <- 10*(r - t*d)
            mpz_mul_ui(tmp, t, d);      // tmp <- t*d
            mpz_sub(r, r, tmp);         // r <- r - t*d
            mpz_mul(r, r, ten);         // r <- 10*(r - t*d)
            // q <- 10*q
            mpz_mul(q, q, ten);
        } else {
            // The candidate is not safe yet. Advance the transformation.
            // r <- (2*q + r) * k
            mpz_mul_ui(tmp, q, 2);      // tmp <- 2*q
            mpz_add(tmp, tmp, r);       // tmp <- 2*q + r
            mpz_mul(tmp, tmp, k);       // tmp <- (2*q + r)*k
            mpz_set(r, tmp);            // update r
            
            // q <- q * k
            mpz_mul(q, q, k);
            // t <- t * k
            mpz_mul(t, t, k);
            // k <- k + 1
            mpz_add_ui(k, k, 1);
        }
    }

    // Clear all mpz_t variables.
    mpz_clears(q, r, t, k, tmp, y, three, four, ten, NULL);

    return 0;
}
