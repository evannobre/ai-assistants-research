#!/usr/bin/env python3
"""
Pi Digit Generator using Spigot Algorithm
Generates N digits of Pi using arbitrary precision arithmetic
Uses only Python's native libraries (no external dependencies)
"""

import sys


def generate_pi_digits(n):
    """
    Generate n digits of Pi using the Spigot algorithm (Rabinowitz-Wagon).
    
    This algorithm generates pi digit by digit without needing to compute
    all previous digits with full precision. It uses only integer arithmetic.
    
    Args:
        n: Number of decimal digits of Pi to generate
        
    Yields:
        Individual digits of Pi (after decimal point)
    """
    # We need more array elements for precision
    # The formula requires about n*10/3 elements
    k = n * 10 // 3 + 1
    
    # Initialize array with 2's (represents 2 in the continued fraction)
    a = [2] * k
    
    # Temporary variables for digit extraction
    nines = 0  # Count of consecutive 9s
    predigit = 0  # The previous digit
    
    for j in range(n):
        q = 0  # Quotient accumulator
        
        # Process the array from right to left
        for i in range(k - 1, -1, -1):
            # Each element represents a term in the continued fraction
            x = 10 * a[i] + q * i
            a[i] = x % (2 * i + 1)
            q = x // (2 * i + 1)
        
        # Update the first element
        a[0] = q % 10
        q = q // 10
        
        # Handle the digit output with carry propagation
        if q == 9:
            nines += 1
        elif q == 10:
            # Carry: increment predigit and output
            yield predigit + 1
            for _ in range(nines):
                yield 0
            predigit = 0
            nines = 0
        else:
            if j > 0:  # Don't output on first iteration
                yield predigit
            for _ in range(nines):
                yield 9
            predigit = q
            nines = 0
    
    # Output the last digit
    yield predigit


def main():
    """Main function to handle command-line arguments and output."""
    if len(sys.argv) != 2:
        print("Usage: python pi_generator.py <number_of_digits>")
        print("Example: python pi_generator.py 100")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            print("Error: Number of digits must be positive")
            sys.exit(1)
    except ValueError:
        print("Error: Invalid number format")
        sys.exit(1)
    
    print(f"Generating {n} digits of Pi...\n")
    print("π = 3.", end="")
    
    # Generate and print digits
    digit_count = 0
    for digit in generate_pi_digits(n):
        print(digit, end="")
        digit_count += 1
        
        # Add spacing for readability (every 50 digits)
        if digit_count % 50 == 0:
            print()
        elif digit_count % 10 == 0:
            print(" ", end="")
    
    print("\n")
    print(f"Generated {digit_count} digits of Pi")


if __name__ == "__main__":
    main()
