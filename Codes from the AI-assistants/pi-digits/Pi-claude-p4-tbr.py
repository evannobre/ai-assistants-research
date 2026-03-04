#!/usr/bin/env python3
"""
Spigot Algorithm for Pi - Sequential Implementation
Calculates N digits of Pi using arbitrary precision arithmetic.
Based on the algorithm by Rabinowitz and Wagon.
"""

import sys


class PiSpigot:
    """
    Implementation of the Spigot algorithm for generating Pi digits.
    Uses native Python arbitrary precision integers for all calculations.
    """
    
    def __init__(self, num_digits):
        """
        Initialize the spigot algorithm.
        
        Args:
            num_digits: Number of Pi digits to generate
        """
        self.num_digits = num_digits
        # Array length needs to be larger than num_digits for precision
        # Using 10 * num_digits / 3 as per standard spigot implementations
        self.array_length = (10 * num_digits) // 3 + 1
        # Initialize array with 2s (represents initial state)
        self.digits_array = [2] * self.array_length
        
    def extract(self, position):
        """
        Extract a digit at the given position.
        This is the key operation in the spigot algorithm.
        
        Args:
            position: Position to extract (3 or 4 for the algorithm)
            
        Returns:
            Extracted digit value
        """
        # Calculate the extracted value using arbitrary precision
        accumulator = 0
        
        for i in range(self.array_length - 1, -1, -1):
            # Multiply by position and add current array value
            accumulator = accumulator * position + self.digits_array[i] * 10000
            
            # Calculate divisor: 2 * i + 1
            divisor = 2 * i + 1
            
            # Update array with quotient
            self.digits_array[i] = accumulator // divisor
            
            # Keep remainder for next iteration
            accumulator = accumulator % divisor
        
        return accumulator // 10000
    
    def eliminate_digit(self, digit):
        """
        Eliminate the extracted digit from the working array.
        
        Args:
            digit: The digit to eliminate
        """
        for i in range(self.array_length):
            self.digits_array[i] = self.digits_array[i] - digit * 10
    
    def generate_digits(self):
        """
        Generate Pi digits using the spigot algorithm.
        Yields digits one at a time.
        """
        digits_generated = 0
        
        while digits_generated < self.num_digits:
            # Extract candidate digit using position 3
            digit_3 = self.extract(3)
            
            # Verify with position 4
            digit_4 = self.extract(4)
            
            # If both extractions agree, we have a valid digit
            if digit_3 == digit_4:
                yield digit_3
                digits_generated += 1
                
                # Eliminate this digit from the working array
                self.eliminate_digit(digit_3)
            else:
                # Disagreement means we need to continue processing
                # This shouldn't happen often with proper array sizing
                pass


def main():
    """
    Main execution function.
    Reads command line argument for number of digits and prints Pi.
    """
    # Parse command line argument
    if len(sys.argv) != 2:
        print("Usage: python spigot_pi.py <number_of_digits>", file=sys.stderr)
        sys.exit(1)
    
    try:
        num_digits = int(sys.argv[1])
        if num_digits <= 0:
            raise ValueError("Number of digits must be positive")
    except ValueError as e:
        print(f"Error: Invalid number of digits - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Memory check (rough estimation)
    # Each element in array is a Python int, roughly 28 bytes minimum
    array_length = (10 * num_digits) // 3 + 1
    estimated_memory_mb = (array_length * 28) / (1024 * 1024)
    
    if estimated_memory_mb > 7000:  # Leave 1GB for system
        print(f"Warning: Estimated memory usage: {estimated_memory_mb:.2f} MB", 
              file=sys.stderr)
        print("This may exceed available RAM (8 GB)", file=sys.stderr)
    
    # Initialize spigot algorithm
    spigot = PiSpigot(num_digits)
    
    # Generate and print digits
    digit_count = 0
    line_buffer = []
    
    for digit in spigot.generate_digits():
        line_buffer.append(str(digit))
        digit_count += 1
        
        # Print 10 digits per line with running total
        if len(line_buffer) == 10:
            print(f"{''.join(line_buffer)}\t:{digit_count}")
            line_buffer = []
    
    # Print remaining digits if any
    if line_buffer:
        # Pad to align with previous lines
        remaining = ''.join(line_buffer)
        print(f"{remaining:<10}\t:{digit_count}")


if __name__ == "__main__":
    main()
