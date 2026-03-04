#!/usr/bin/env python3
"""
Spigot algorithm for π digits generation.
Implements both extract(3) and extract(4) methods.
"""
import sys
import time
from typing import List, Iterator


class SpigotPiGenerator:
    """Base class for Spigot π digit generators."""
    
    def __init__(self, n_digits: int):
        self.n_digits = n_digits
        self.digits_generated = 0
        self.start_time = time.time()
    
    def print_progress(self, digits: str, line_num: int):
        """Print digits 10-to-a-line with running total."""
        for i in range(0, len(digits), 10):
            chunk = digits[i:i+10]
            self.digits_generated += len(chunk)
            print(f"{chunk:<10} {self.digits_generated}")
            
    def print_stats(self):
        """Print performance statistics."""
        elapsed = time.time() - self.start_time
        print(f"\nDigits calculated: {self.digits_generated}")
        print(f"Time elapsed: {elapsed:.2f} seconds")
        print(f"Digits per second: {self.digits_generated/elapsed:.0f}")


class SpigotPiExtract3(SpigotPiGenerator):
    """
    Implementation of the Rabinowitz-Wagon spigot algorithm (extract(3)).
    This is the straightforward implementation using only integer arithmetic.
    """
    
    def generate_digits(self) -> Iterator[str]:
        """Generate π digits using extract(3) algorithm."""
        n = self.n_digits
        
        # Initialize array A = [2, 2, 2, ..., 2] of length floor(10n/3)
        length = (10 * n // 3) + 1
        A = [2] * length
        
        predigit = 0
        nines = 0
        
        for digit_position in range(1, n + 1):
            # Multiply by 10 and propagate carries
            carry = 0
            for i in range(length - 1, -1, -1):
                A[i] *= 10
                A[i] += carry
                
                if i == 0:
                    denominator = 10
                else:
                    denominator = 2 * i + 1
                
                quotient = A[i] // denominator
                remainder = A[i] % denominator
                
                if i > 0:
                    carry = quotient * i
                A[i] = remainder
            
            # Extract next digit
            next_digit = A[0] // 10
            A[0] %= 10
            
            # Handle carries from potential 9's
            if next_digit == 9:
                nines += 1
            elif next_digit == 10:
                yield str(predigit + 1)
                for _ in range(nines):
                    yield '0'
                predigit = 0
                nines = 0
            else:
                if predigit != 0 or digit_position > 1:
                    yield str(predigit)
                for _ in range(nines):
                    yield '9'
                predigit = next_digit
                nines = 0
        
        # Yield final digit
        yield str(predigit)
        for _ in range(nines):
            yield '9'


class SpigotPiExtract4(SpigotPiGenerator):
    """
    Implementation of the optimized spigot algorithm (extract(4)).
    Uses base 10,000 arithmetic for better performance.
    """
    
    def __init__(self, n_digits: int):
        super().__init__(n_digits)
        self.base = 10000  # Base for calculations
        self.base_log10 = 4  # log10(base)
    
    def generate_digits(self) -> Iterator[str]:
        """Generate π digits using extract(4) algorithm."""
        n = self.n_digits
        
        # Calculate number of terms needed
        # Using the series: π = 16*arctan(1/5) - 4*arctan(1/239)
        # For base B, need enough terms for n*log10(B) digits
        scale = 10 ** (n + 10)  # Extra precision for rounding
        
        # Initialize arrays for arctan(1/5) and arctan(1/239)
        # We'll compute: π/4 = 4*arctan(1/5) - arctan(1/239)
        # So π = 16*arctan(1/5) - 4*arctan(1/239)
        
        # Calculate arctan(1/5) using series: arctan(x) = x - x³/3 + x⁵/5 - ...
        # We work with scaled integers
        arctan5 = 0
        power5 = scale // 5  # Start with 1/5
        divisor = 1
        sign = 1
        
        # Continue until terms become negligible
        term = power5
        while term != 0:
            arctan5 += sign * (term // divisor)
            power5 //= 25  # Divide by 5² each time (x² = 1/25)
            divisor += 2
            sign = -sign
            term = power5 // divisor
        
        # Calculate arctan(1/239)
        arctan239 = 0
        power239 = scale // 239
        divisor = 1
        sign = 1
        
        term = power239
        while term != 0:
            arctan239 += sign * (term // divisor)
            power239 //= 57121  # Divide by 239²
            divisor += 2
            sign = -sign
            term = power239 // divisor
        
        # Combine: π = 16*arctan(1/5) - 4*arctan(1/239)
        pi_approx = 16 * arctan5 - 4 * arctan239
        
        # Convert to decimal digits
        pi_str = str(pi_approx)
        
        # The first digit is before the decimal point, rest are after
        # Our calculation gives pi * 10^(n+10), so we need to extract digits
        result = pi_str[0] + '.' + pi_str[1:n]
        
        # Yield digits one by one
        for digit in result:
            if digit == '.':
                continue
            yield digit


def validate_machine_specs():
    """Validate we're within machine specifications."""
    import os
    import shutil
    
    # Check disk space
    total, used, free = shutil.disk_usage("/")
    if total < 256 * 1024**3:  # 256 GB
        print("Warning: Machine has less than 256 GB SSD", file=sys.stderr)
    
    # Check memory
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_gb = mem_bytes / (1024.**3)
    if mem_gb < 8:
        print("Warning: Machine has less than 8 GB RAM", file=sys.stderr)


def run_spigot_algorithm(method: int, n_digits: int):
    """Run the specified spigot algorithm."""
    print(f"\n{'='*60}")
    print(f"Calculating π to {n_digits} digits using extract({method})")
    print(f"{'='*60}\n")
    
    if method == 3:
        generator = SpigotPiExtract3(n_digits)
    else:  # method == 4
        generator = SpigotPiExtract4(n_digits)
    
    # Buffer for printing 10 digits at a time
    buffer = []
    buffer_size = 0
    
    for digit in generator.generate_digits():
        buffer.append(digit)
        buffer_size += 1
        
        if buffer_size == 10:
            generator.print_progress(''.join(buffer), generator.digits_generated // 10)
            buffer = []
            buffer_size = 0
    
    # Print any remaining digits
    if buffer:
        generator.print_progress(''.join(buffer), generator.digits_generated // 10 + 1)
    
    generator.print_stats()


def main():
    """Main function."""
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python spigot_pi.py <method> <n_digits>")
        print("  method: 3 for extract(3), 4 for extract(4)")
        print("  n_digits: number of π digits to calculate (use 10000 for performance test)")
        sys.exit(1)
    
    try:
        method = int(sys.argv[1])
        n_digits = int(sys.argv[2])
    except ValueError:
        print("Error: method and n_digits must be integers")
        sys.exit(1)
    
    if method not in (3, 4):
        print("Error: method must be 3 or 4")
        sys.exit(1)
    
    if n_digits <= 0:
        print("Error: n_digits must be positive")
        sys.exit(1)
    
    # Validate machine specs
    validate_machine_specs()
    
    # Run the algorithm
    run_spigot_algorithm(method, n_digits)


if __name__ == "__main__":
    main()