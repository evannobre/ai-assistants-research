import sys
import time
from decimal import Decimal, getcontext

def spigot_pi_digits(n):
    """
    Implementation of the Spigot algorithm by Rabinowitz and Wagon
    to compute digits of pi one at a time.
    
    This is a direct implementation of the algorithm without optimizations.
    """
    # Initialize arrays
    len = n * 10 // 3 + 1
    a = [2] * len
    predigits = []
    
    nines = 0
    predigit = 0
    
    for j in range(1, n + 1):
        # Step 1: Multiply by 10
        carry = 0
        for i in range(len - 1, -1, -1):
            a[i] *= 10
        
        # Step 2: Calculate q and propagate carries
        for i in range(len - 1, -1, -1):
            a[i] += carry
            if i == 0:
                denom = 10
            else:
                denom = 2 * i + 1
            q = a[i] // denom
            r = a[i] % denom
            a[i] = r
            if i > 0:
                carry = q * i
        
        # Step 3: Get the next digit
        a[0] = q % 10
        q = q // 10
        
        if q == 9:
            nines += 1
        elif q == 10:
            # Handle overflow: emit predigit+1 and nines zeros
            digit = predigit + 1
            if digit == 10:
                digit = 0
            predigits.append(digit)
            
            for k in range(nines):
                predigits.append(0)
            
            predigit = 0
            nines = 0
        else:
            # Normal case
            if predigit != 0 or (predigits and predigits[0] != 0):
                predigits.append(predigit)
            
            for k in range(nines):
                predigits.append(9)
            
            predigit = q
            nines = 0
        
        # Yield digits if we have them
        while predigits:
            yield predigits.pop(0)
    
    # Yield any remaining predigit
    if predigit != 0 or (predigits and predigits[0] != 0):
        yield predigit

def print_pi_digits(n):
    """Print digits of pi 10 per line with running total."""
    digits = spigot_pi_digits(n)
    count = 0
    line_digits = []
    
    print(f"Computing first {n} digits of pi...")
    print("=" * 60)
    
    try:
        while count < n:
            digit = next(digits)
            line_digits.append(str(digit))
            
            if len(line_digits) == 10:
                count += 10
                line_str = ''.join(line_digits)
                print(f"{line_str} : {count}")
                line_digits = []
            
    except StopIteration:
        # Print any remaining digits
        if line_digits:
            count += len(line_digits)
            line_str = ''.join(line_digits)
            print(f"{line_str} : {count}")

def extract_digit_3(n):
    """Extract the nth digit using algorithm (3) - basic spigot."""
    # Set precision for Decimal calculations
    getcontext().prec = n + 10
    
    q = Decimal(0)
    for k in range(n + 1):
        numerator = Decimal(1) / (16 ** k)
        term1 = Decimal(4) / (8 * k + 1)
        term2 = Decimal(2) / (8 * k + 4)
        term3 = Decimal(1) / (8 * k + 5)
        term4 = Decimal(1) / (8 * k + 6)
        
        q += numerator * (term1 - term2 - term3 - term4)
    
    # Convert to string and get the nth digit
    pi_str = str(q)
    if pi_str[0] == '3':
        pi_str = pi_str[2:]  # Remove "3."
    else:
        pi_str = pi_str[1:]  # Remove leading digit
    
    if n <= len(pi_str):
        return int(pi_str[n-1])
    return None

def extract_digit_4(n):
    """Extract the nth digit using algorithm (4) - Bailey-Borwein-Plouffe formula."""
    # This is a different formula for extracting individual digits
    def s(j, n):
        """Helper function for BBP formula."""
        total = 0
        k = 0
        while k <= n:
            denominator = 8 * k + j
            if denominator != 0:
                total += pow(16, n - k, denominator) / denominator
            k += 1
        
        k = n + 1
        while True:
            term = pow(16, n - k) / (8 * k + j)
            if term < 1e-17:  # Precision threshold
                break
            total += term
            k += 1
        
        return total
    
    # Calculate using BBP formula
    n1 = n - 1
    pi_part = 4 * s(1, n1) - 2 * s(4, n1) - s(5, n1) - s(6, n1)
    
    # Extract the fractional part and get the digit
    pi_part = pi_part - int(pi_part)
    if pi_part < 0:
        pi_part += 1
    
    # Get the hexadecimal digit
    hex_digit = int(pi_part * 16) % 16
    
    # For this example, we'll convert to decimal digit
    # In a full implementation, we'd need to convert base-16 to base-10 properly
    return hex_digit

def main():
    """Main function to run the spigot algorithm."""
    # Set default value
    n = 100
    
    # Check for command line argument
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Invalid argument: {sys.argv[1]}. Using default n={n}.")
    
    print(f"Running spigot algorithm for pi with n = {n}")
    print()
    
    # Measure performance
    start_time = time.time()
    print_pi_digits(n)
    end_time = time.time()
    
    print("=" * 60)
    print(f"Time taken: {end_time - start_time:.3f} seconds")
    print()
    
    # Test extract(3) and extract(4) for small n
    print("Testing extract(3) and extract(4) for n = 5, 10, 20:")
    print("-" * 40)
    
    test_values = [5, 10, 20]
    for test_n in test_values:
        digit3 = extract_digit_3(test_n)
        digit4 = extract_digit_4(test_n)
        print(f"Digit {test_n}: extract(3) = {digit3}, extract(4) = {digit4}")
    
    print()
    print("Note: extract(4) returns hexadecimal digits which may need conversion")
    print("for direct comparison with decimal digits from extract(3).")

if __name__ == "__main__":
    main()