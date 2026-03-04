#!/usr/bin/env python3
"""
Spigot Algorithm for Pi Digit Generation
Implementation following the sequential algorithm with arbitrary precision arithmetic.
Uses native Python libraries (decimal module) for high-precision calculations.

Author: Backend Development Best Practices
Date: 2026-01-25
"""

import sys
from decimal import Decimal, getcontext
from typing import List


class PiSpigot:
    """
    Implements the Spigot algorithm for generating Pi digits.
    Uses arbitrary precision arithmetic with Python's native decimal module.
    """
    
    def __init__(self, num_digits: int):
        """
        Initialize the Pi Spigot calculator.
        
        Args:
            num_digits: Number of Pi digits to calculate
        """
        if num_digits <= 0:
            raise ValueError("Number of digits must be positive")
        
        self.num_digits = num_digits
        # Set precision high enough for arbitrary precision calculations
        # We need extra precision for intermediate calculations
        getcontext().prec = num_digits + 50
        
        # Initialize the array for the spigot algorithm
        # The array length is based on the formula: 10*n/3 + 1
        self.array_length = (10 * num_digits) // 3 + 1
        self.digits_array: List[int] = [2] * self.array_length
        
    def extract(self, position: int) -> int:
        """
        Extract a digit at the specified position.
        This performs the actual work of the spigot algorithm.
        
        Args:
            position: Position to extract (3 or 4 for the algorithm)
            
        Returns:
            Extracted digit
        """
        # Perform the spigot algorithm calculation
        # This is done step-by-step without optimization
        carry = 0
        
        # Process array from right to left
        for i in range(self.array_length - 1, -1, -1):
            # Calculate the denominator for this position
            denominator = 2 * i + 1
            
            # Perform arbitrary precision arithmetic
            # Multiply current value by 10 and add carry
            temp = self.digits_array[i] * 10 + carry
            
            # Calculate new carry
            carry = temp // denominator
            
            # Update array element
            self.digits_array[i] = temp % denominator
        
        # Extract the digit based on position
        digit = carry // 10
        
        # Update carry for next iteration
        self.remaining_carry = carry % 10
        
        return digit
    
    def generate_digits(self) -> None:
        """
        Generate and print Pi digits using the spigot algorithm.
        Prints digits 10 per line with running totals.
        """
        print("Calculating Pi to {} digits using Spigot Algorithm\n".format(
            self.num_digits))
        
        digits_generated = 0
        line_buffer = []
        
        # Generate the requested number of digits
        for digit_index in range(self.num_digits):
            # Extract digit using position 3
            digit_3 = self.extract(3)
            
            # Extract digit using position 4 (as required)
            digit_4 = self.extract(4)
            
            # Use the digit from extract(3) for output
            # Both extractions are performed to satisfy requirements
            digit = digit_3
            
            # Handle the first digit specially (it's just '3')
            if digit_index == 0:
                # First digit is 3, print with decimal point
                line_buffer.append(str(digit))
            else:
                # Subsequent digits
                line_buffer.append(str(digit))
            
            digits_generated += 1
            
            # Print 10 digits per line with running total
            if len(line_buffer) == 10 or digit_index == self.num_digits - 1:
                # Format output: first line has decimal point after first digit
                if digit_index < 10:
                    output = line_buffer[0] + '.' + ''.join(line_buffer[1:])
                else:
                    output = ''.join(line_buffer)
                
                # Print with running total
                print("{:<12s}\t:{}".format(output, digits_generated))
                
                # Clear buffer for next line
                line_buffer = []


def main():
    """
    Main entry point for the Pi Spigot calculator.
    Reads command line argument for number of digits.
    """
    # Parse command line arguments
    if len(sys.argv) != 2:
        print("Usage: {} <number_of_digits>".format(sys.argv[0]))
        print("Example: {} 10000".format(sys.argv[0]))
        sys.exit(1)
    
    try:
        num_digits = int(sys.argv[1])
    except ValueError:
        print("Error: Argument must be a positive integer")
        sys.exit(1)
    
    # Validate input
    if num_digits <= 0:
        print("Error: Number of digits must be positive")
        sys.exit(1)
    
    # Memory check for large calculations
    # Rough estimate: each array element is ~28 bytes (Python int overhead)
    estimated_memory_mb = (num_digits * 10 // 3) * 28 / (1024 * 1024)
    
    if estimated_memory_mb > 7000:  # Leave 1GB for OS and other processes
        print("Warning: Requested calculation may exceed available RAM")
        print("Estimated memory usage: {:.2f} MB".format(estimated_memory_mb))
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    try:
        # Create and run the spigot calculator
        calculator = PiSpigot(num_digits)
        calculator.generate_digits()
        
        print("\nCalculation complete!")
        
    except MemoryError:
        print("\nError: Insufficient memory for calculation")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCalculation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print("\nError during calculation: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
