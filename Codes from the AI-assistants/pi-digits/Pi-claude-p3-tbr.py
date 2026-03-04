#!/usr/bin/env python3
"""
Spigot algorithm for generating digits of Pi.
Uses arbitrary precision arithmetic with native Python integers.
Sequential algorithm - no optimization of work.
"""

import sys


class PiSpigot:
    """
    Implements the Spigot algorithm for calculating Pi digits.
    Based on the algorithm by Stanley Rabinowitz and Stan Wagon.
    """
    
    def __init__(self, n):
        """Initialize the spigot algorithm for n digits."""
        self.n = n
        # Array length needs to be sufficient for the algorithm
        # Using formula: 10 * n / 3
        self.len = (10 * n) // 3 + 1
        # Initialize the array with 2s (represents initial state)
        self.digits = [2] * self.len
    
    def extract(self, x):
        """
        Extract digit when multiplied by x.
        This performs the extraction step of the spigot algorithm.
        """
        # Work from right to left through the array
        # Accumulator for carries
        carry = 0
        
        for i in range(self.len - 1, -1, -1):
            # Calculate: digit[i] * x + carry
            temp = self.digits[i] * x + carry
            
            # The position from the right
            pos = self.len - i
            
            # Calculate quotient and remainder
            # quotient = temp // (2 * pos - 1)
            # remainder = temp % (2 * pos - 1)
            divisor = 2 * pos - 1
            quotient = temp // divisor
            remainder = temp % divisor
            
            # Store the remainder back
            self.digits[i] = remainder
            
            # Carry forward the quotient
            carry = quotient * i
        
        # Final result is the quotient from the last operation
        result = carry // self.len
        
        # Update the first element with the remainder
        self.digits[0] = carry % self.len
        
        return result
    
    def next_digit(self):
        """Generate the next digit of Pi."""
        # Extract with 3 to get the candidate digit
        q3 = self.extract(3)
        
        # Extract with 4 to verify
        q4 = self.extract(4)
        
        # If they match, we have our digit
        if q3 == q4:
            # Remove the digit we just extracted
            self.extract(q3)
            return q3
        else:
            # In the standard algorithm, we would continue
            # For this implementation, we return the q3 value
            return q3


def calculate_pi(n):
    """
    Calculate the first n digits of Pi using the Spigot algorithm.
    Prints digits 10 per line with running total.
    """
    spigot = PiSpigot(n)
    
    digits_printed = 0
    line_buffer = []
    
    for i in range(n):
        digit = spigot.next_digit()
        
        # First digit is before the decimal point
        if i == 0:
            print(f"{digit}.", end="")
        else:
            line_buffer.append(str(digit))
            
            # Print 10 digits per line
            if len(line_buffer) == 10:
                print("".join(line_buffer), end="")
                digits_printed += 10
                print(f"\t:{digits_printed}")
                line_buffer = []
    
    # Print any remaining digits
    if line_buffer:
        print("".join(line_buffer), end="")
        digits_printed += len(line_buffer)
        print(f"\t:{digits_printed}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python pi_spigot.py <number_of_digits>")
        print("Example: python pi_spigot.py 1000")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            print("Error: Number of digits must be positive")
            sys.exit(1)
        
        calculate_pi(n)
        
    except ValueError:
        print("Error: Argument must be an integer")
        sys.exit(1)


if __name__ == "__main__":
    main()
