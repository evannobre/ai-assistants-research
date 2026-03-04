import sys
import time
from decimal import Decimal, getcontext

def pi_spigot(n_digits):
    """
    Implementation of the Spigot algorithm to generate digits of Pi.
    
    Args:
        n_digits: Number of digits of Pi to generate
    
    Returns:
        A string of digits representing Pi (not including the decimal point)
    """
    # Ensure we have enough precision for our calculation
    getcontext().prec = n_digits * 10
    
    # Setup initial state
    # Length needs to be 10*n/3 which is a safe overestimate
    length = 10 * n_digits // 3 + 1
    
    # Initialize the array with 2s
    array = [Decimal(2)] * length
    
    # Initialize result storage
    result = []
    
    # Main algorithm
    for i in range(n_digits):
        # Step 1: Multiply by 10
        carry = Decimal(0)
        for j in range(length - 1, -1, -1):
            array[j] = array[j] * 10 + carry
            carry = array[j] // 10
            array[j] %= 10
        
        # Step 2: Divide by denominator (2*j + 1)
        remainder = 0
        for j in range(length):
            temp = remainder * 10 + array[j]
            array[j] = temp // (2 * j + 1)
            remainder = temp % (2 * j + 1)
        
        # The next digit of Pi
        result.append(int(carry))
        
        if i > 0 and i % 10 == 0:
            # Print progress
            sys.stdout.write(f"\rCalculated {i} digits...")
            sys.stdout.flush()
    
    return ''.join(map(str, result))

def extract(n_digits):
    """
    Calculate and print the first n_digits of Pi
    """
    start_time = time.time()
    pi_digits = pi_spigot(n_digits)
    
    # Initial display in the format 3.141592...
    print(f"Pi = {pi_digits[0]}.{pi_digits[1:]}")
    
    # Display 10 digits per line with a running count
    lines = []
    for i in range(0, len(pi_digits), 10):
        chunk = pi_digits[i:i+10]
        lines.append(f"{i+len(chunk):5d}: {chunk}")
    
    print("\nDigits of Pi:")
    print('\n'.join(lines))
    
    elapsed_time = time.time() - start_time
    print(f"\nTime taken: {elapsed_time:.2f} seconds for {n_digits} digits")

def main():
    # Get digits from command line argument, default to 100
    n_digits = 100
    if len(sys.argv) > 1:
        try:
            n_digits = int(sys.argv[1])
        except ValueError:
            print(f"Invalid argument: {sys.argv[1]}. Using default of 100 digits.")
    
    extract(n_digits)

if __name__ == "__main__":
    main()