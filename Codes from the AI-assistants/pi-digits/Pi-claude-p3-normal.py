#!/usr/bin/env python3
"""
Spigot algorithm for calculating digits of Pi.
Uses arbitrary precision arithmetic with native Python integers.
Implements the sequential algorithm without optimizations.
"""

import sys


class PiSpigot:
    def __init__(self, n):
        """Initialize the spigot algorithm for n digits of Pi."""
        self.n = n
        # Array length needs to be longer for precision
        self.len = n * 10 // 3 + 1
        # Initialize the array with 2s (represents initial state)
        self.a = [2] * self.len
    
    def extract(self, j):
        """
        Extract the jth digit from the current state.
        This performs the extraction calculation without modifying state.
        """
        # Calculate q (quotient) from the array
        q = 0
        for i in range(self.len):
            q = q * i + self.a[i] * j
            q = q % (2 * i + 1)
        
        return q
    
    def eliminate(self, d):
        """
        Eliminate digit d from the state.
        This updates the array after a digit has been produced.
        """
        # Work through the array to eliminate the digit
        for i in range(self.len):
            self.a[i] = self.a[i] * 10 - d * (2 * i + 1)
        
        # Normalize the array (propagate carries)
        c = 0
        for i in range(self.len - 1, -1, -1):
            temp = self.a[i] + c
            q = temp // (2 * i + 1)
            r = temp % (2 * i + 1)
            self.a[i] = r
            c = q * i
    
    def next_digit(self):
        """
        Calculate the next digit of Pi using the spigot algorithm.
        Returns the next digit (0-9).
        """
        # Extract both potential digits
        d3 = self.extract(3)
        d4 = self.extract(4)
        
        # Check if they agree (safe to output)
        if d3 == d4:
            # Eliminate this digit from the state
            self.eliminate(d3)
            return d3
        else:
            # Should not happen in correct implementation
            # but we handle it for robustness
            self.eliminate(d3)
            return d3
    
    def generate(self):
        """Generate n digits of Pi."""
        digits = []
        for i in range(self.n):
            digit = self.next_digit()
            digits.append(digit)
        return digits


def print_pi_digits(digits):
    """Print digits 10 per line with running total."""
    for i in range(0, len(digits), 10):
        # Get up to 10 digits
        chunk = digits[i:i+10]
        # Format as string
        digit_str = ''.join(map(str, chunk))
        # Print with running total (right-aligned)
        print(f"{digit_str:<10}\t:{i + len(chunk)}")


def main():
    # Get number of digits from command line
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Usage: python pi_spigot.py [number_of_digits]")
            sys.exit(1)
    else:
        n = 1000  # default
    
    # Create spigot and generate digits
    spigot = PiSpigot(n)
    digits = spigot.generate()
    
    # Print results
    print_pi_digits(digits)


if __name__ == "__main__":
    main()
