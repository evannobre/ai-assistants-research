#!/usr/bin/env python3
"""
Spigot Algorithm for Pi
=======================

This program uses a step‐by‐step spigot algorithm to generate the digits of π.
It uses arbitrary–precision arithmetic (Python ints) and computes the result in a
single-threaded, sequential manner. Every “digit extraction” stage does the full
work. The algorithm is adapted so that digits are extracted in groups (blocks),
using either a three-digit extraction (extract(3)) or four-digit extraction (extract(4)).

/*
    Spigot algorithm for π using two extraction functions.
    This program computes the first N digits of π (without a decimal point)
    using a single-threaded, step-by-step algorithm that uses an array of
    integers to represent the large “numerators” (i.e. arbitrary precision arithmetic).
    
    It uses two extraction routines – one with multiplier 3 and one with multiplier 4 –
    to check that a candidate digit is “safe.” When the two agree the digit is output
    (with special handling if the digit is 9 or if a carry arises when it is 10).
    
    The computed digits are printed 10 digits per line with the running total.
    
    Usage:   spigot [num_digits]
           If no command-line argument is given, a default value is used.
           Use a larger value (say 10000) to test performance.
    
    This implementation does not optimize away any work:
    it makes two complete extraction passes (via temporary arrays)
    on each iteration.
*/

#include <stdio.h>
#include <stdlib.h>

/* 
   The working array “a” holds the state of the computation.
   Its length is chosen to be approximately (10 * N / 3) + 2.
   Each element is an integer (small enough that standard arithmetic suffices).
*/

/* duplicate_array: returns a new allocated copy of an integer array */
int *duplicate_array(const int *a, int len) {
    int *b = (int *) malloc(len * sizeof(int));
    if(b == NULL) {
        fprintf(stderr, "Memory allocation error in duplicate_array\n");
        exit(1);
    }
    for (int i = 0; i < len; i++) {
        b[i] = a[i];
    }
    return b;
}

/*
    extract_digit (multiplier d): 
    On a copy of the state the algorithm runs through all elements:
      for each index i (from last down to 0)
         multiply a[i] by d, add the carry,
         update a[i] = (value mod (2*i + 1))
         set carry = (value / (2*i + 1)) * i.
    Finally it returns (carry mod d).
    (We use d = 3 or 4 to “peek” at the next candidate.)
*/
int extract_digit(int d, int *arr, int len) {
    int carry = 0;
    for (int i = len - 1; i >= 0; i--) {
        int numerator = arr[i] * d + carry;
        int divisor = 2 * i + 1;
        arr[i] = numerator % divisor;
        carry = (numerator / divisor) * i;
    }
    return carry % d;
}

/*
    eliminate_digit:
    Now that a safe candidate digit has been determined,
    update the true state array “a” with multiplier 10 and with the known candidate digit.
    (This function “eliminates” the candidate from the working state.)
*/
void eliminate_digit(int d, int *a, int len) {
    int carry = d;
    for (int i = 0; i < len; i++) {
        int numerator = a[i] * 10 + carry;
        int divisor = 2 * i + 1;
        a[i] = numerator % divisor;
        carry = (numerator / divisor) * i;
    }
}

/*
    print_digit:
    Prints out a single digit and updates the running count.
    Every ten digits a tab and the total count is printed on the same line.
*/
void print_digit(int digit, int *count) {
    printf("%d", digit);
    (*count)++;
    if ((*count) % 10 == 0)
        printf("\t: %d\n", *count);
}

int main(int argc, char *argv[]) {
    int numDigits = 1000;  // default number of digits if not specified
    if (argc > 1) {
        numDigits = atoi(argv[1]);
        if (numDigits <= 0) {
            fprintf(stderr, "Invalid number of digits.\n");
            return 1;
        }
    }

    /* Determine size of working array.
       (This formula overallocates a bit to be sure.)
    */
    int len = (numDigits * 10) / 3 + 2;
    int *a = (int *) malloc(len * sizeof(int));
    if(a == NULL) {
        fprintf(stderr, "Memory allocation error\n");
        return 1;
    }
    for (int i = 0; i < len; i++) {
        a[i] = 2;
    }

    /* Variables for managing safe candidate output */
    int predigit = 0;  /* Holds the last candidate digit waiting for confirmation */
    int nines = 0;     /* Count of successive 9’s */
    int digitCount = 0; /* Total digits printed so far */
    int firstSafe = 1;  /* Flag to indicate that we do not print the first safe digit immediately */

    /*
       Main loop: each iteration either produces a safe candidate digit or
       updates the state further.
       
       The algorithm “peeks” at the next digit by computing extract_digit() twice –
       once with multiplier 3 and once with multiplier 4 using duplicated state.
       If the two agree, then the candidate is safe.
       When safe, the candidate is handled in one of three ways:
         - If it is 9: simply remember it by incrementing nines.
         - If it is 10: a “carry” must be propagated.
         - Otherwise: output the stored predigit (if not the first safe digit)
           and any previously buffered 9’s.
       In all safe cases the state is updated by calling eliminate_digit()
       with the safe candidate (or 10 if not safe).
    */
    while (digitCount < numDigits) {
        int d3, d4;
        int *tmp;
        
        /* Make a copy of the state and extract with multiplier 3 */
        tmp = duplicate_array(a, len);
        d3 = extract_digit(3, tmp, len);
        free(tmp);
        
        /* Make a fresh copy of the state and extract with multiplier 4 */
        tmp = duplicate_array(a, len);
        d4 = extract_digit(4, tmp, len);
        free(tmp);
        
        if (d3 == d4) {
            int d = d3;  /* safe candidate digit */
            if (firstSafe) {
                /* For the very first safe candidate, don't output anything yet */
                predigit = d;
                firstSafe = 0;
            } else if (d == 9) {
                /* Buffer 9’s */
                nines++;
            } else if (d == 10) {
                /* Candidate digit is 10: propagate the carry.
                   Increment predigit and output it, then output zero for each buffered nine.
                */
                predigit++;
                if (digitCount < numDigits) {
                    print_digit(predigit, &digitCount);
                    if (digitCount >= numDigits) break;
                }
                for (int k = 0; k < nines; k++) {
                    if (digitCount < numDigits) {
                        print_digit(0, &digitCount);
                        if (digitCount >= numDigits) break;
                    }
                }
                predigit = 0;
                nines = 0;
            } else {
                /* A safe non-9, non-10 digit:
                   Output the previous candidate and any buffered 9’s.
                */
                if (digitCount < numDigits) {
                    print_digit(predigit, &digitCount);
                    if (digitCount >= numDigits) break;
                }
                for (int k = 0; k < nines; k++) {
                    if (digitCount < numDigits) {
                        print_digit(9, &digitCount);
                        if (digitCount >= numDigits) break;
                    }
                }
                predigit = d;
                nines = 0;
            }
            /* Update the state with the safe candidate.
               (This “eliminates” the digit from the computation.)
            */
            eliminate_digit(d, a, len);
        } else {
            /* The candidate isn’t safe;
               update the state using multiplier 10 and try again.
            */
            eliminate_digit(10, a, len);
        }
    }
    
    /* When finished the final predigit is output */
    if (digitCount < numDigits) {
        print_digit(predigit, &digitCount);
    }
    /* If the last line has fewer than 10 digits, print the running total */
    if (digitCount % 10 != 0)
        printf("\t: %d\n", digitCount);
    
    free(a);
    return 0;
}
    python spigot_pi.py <num_digits> <extract_mode>

    where:
      <num_digits>   is the total number of digits of π to generate;
      <extract_mode> should be 3 or 4, indicating extraction by groups of 3 or 4 digits.

The output prints 10 digits per line, with a running total of digits generated.
For performance checking, try a larger command-line argument (e.g. 10000).
"""

import sys
import math

def spigot_pi(num_digits, extract_mode):
    """
    Compute the digits of π using the spigot algorithm with block extraction.
    
    Traditional one-digit extraction uses a base of 10 and an array length L = floor((num_digits * 10)/3).
    When extracting several digits per iteration, we do the following:
      • Let base = 10^extract_mode. Each “group” will produce extract_mode digits.
      • Let groups = ceil(num_digits / extract_mode) be the number of iterations needed.
      • Set L = floor((groups * 10)/3). (In the one-digit algorithm groups=num_digits so that L = floor((num_digits*10)/3).)
    
    The inner loop (which is not optimized away) works as follows:
      For each iteration i in 0 .. groups-1:
         • Set carry = 0.
         • For j = L downto 1:
              x = a[j-1] * base + carry,
              a[j-1] is replaced by remainder:  x mod (2*j - 1),
              and carry becomes (x // (2*j - 1)) * j.
         • The extracted group is carry mod base.
         • Then update carry to carry // base.
    At the end the extracted groups are concatenated and truncated to num_digits digits.
    
    Arguments:
      num_digits   -- total number of (base‑10) digits of π desired.
      extract_mode -- an integer (3 or 4) indicating the group size in digits to extract.
      
    Returns:
      A string representing the first num_digits digits of π.
    """

    # Base for extraction: either 10^3 or 10^4.
    base = 10 ** extract_mode
    # Number of full extraction groups needed.
    groups = (num_digits + extract_mode - 1) // extract_mode
    # Determine the length of the working array.
    # In the classic one-digit algorithm, L = (num_digits * 10)//3; here we scale by groups.
    L = (groups * 10) // 3

    # Initialize the array: all entries start as 2.
    a = [2] * L

    results = []    # This will store string groups (each of length extract_mode except possibly the first).
    carry = 0       # The carry (or “remainder”) that is threaded through the inner loop.

    # Perform the digit extraction group by group.
    for group_index in range(groups):
        carry = 0
        # Process the array from rightmost element down to the left.
        for j in range(L, 0, -1):
            # Multiply current element by base and add carry.
            numerator = a[j - 1] * base + carry
            denominator = 2 * j - 1
            # Update the array element to the remainder.
            a[j - 1] = numerator % denominator
            # The quotient times j becomes the new carry.
            carry = (numerator // denominator) * j
        # The next group of digits is the last (carry mod base).
        group_digits = carry % base
        # Prepare a zero-padded string for these digits.
        group_str = f"{group_digits:0{extract_mode}d}"
        results.append(group_str)
        # Prepare the carry for the next iteration.
        carry //= base

    # Concatenate the groups into one long string.
    pi_str = "".join(results)
    # Truncate to exactly num_digits digits.
    return pi_str[:num_digits]

def print_pi_digits(pi_str):
    """
    Print the π digits 10 per line, along with a running total.
    """
    for i in range(0, len(pi_str), 10):
        line = pi_str[i:i+10]
        total = i + len(line)
        print(f"{line}\t: {total}")

def main():
    if len(sys.argv) < 3:
        print("Usage: {} <num_digits> <extract_mode (3 or 4)>".format(sys.argv[0]))
        sys.exit(1)

    try:
        num_digits = int(sys.argv[1])
        extract_mode = int(sys.argv[2])
        if extract_mode not in (3, 4):
            raise ValueError("extract_mode must be 3 or 4")
    except ValueError as err:
        print("Error:", err)
        sys.exit(1)

    pi_digits = spigot_pi(num_digits, extract_mode)
    print_pi_digits(pi_digits)

if __name__ == "__main__":
    main()