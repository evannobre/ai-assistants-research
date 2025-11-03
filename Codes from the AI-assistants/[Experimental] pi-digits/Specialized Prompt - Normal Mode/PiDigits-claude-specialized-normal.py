from decimal import Decimal, getcontext
import sys
import time

def calculate_pi(digits):
    """
    Calculate pi to the specified number of digits using the Chudnovsky algorithm.
    This algorithm converges much faster than other methods like Machin's formula.
    """
    # Set precision to desired digits + extra margin for accuracy
    getcontext().prec = digits + 20
    
    # Chudnovsky algorithm constants
    C = 426880 * Decimal(10005).sqrt()
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    K = Decimal(6)
    S = L
    
    n = 1
    # Continue until we have enough precision
    while True:
        M = M * (Decimal(K**3 - 16*K) / Decimal(n**3))
        L += 545140134
        X *= -262537412640768000
        S += (M * L) / X
        n += 1
        K += 12
        
        # Check if we have enough terms for the desired precision
        term_size = abs(M * L / X)
        if term_size < Decimal(10) ** (-digits - 10):
            break
    
    # Calculate pi using the Chudnovsky formula
    pi = C / S
    
    # Return only the requested number of digits
    return str(pi)[:digits+2]  # +2 for the "3." part

def main():
    if len(sys.argv) != 2:
        print("Usage: python pi_generator.py <number_of_digits>")
        return
    
    try:
        digits = int(sys.argv[1])
        if digits <= 0:
            print("Please provide a positive number of digits.")
            return
            
        # Check if we have enough memory
        estimated_memory_bytes = digits * 8  # Conservative estimate
        if estimated_memory_bytes > 16 * 10**9:  # 16 GB limit
            print(f"Warning: Generating {digits} digits might require more than the available 16GB of RAM.")
            return
            
        start_time = time.time()
        pi = calculate_pi(digits)
        end_time = time.time()
        
        print(f"First {digits} digits of Pi:")
        print(pi)
        print(f"\nCalculation took {end_time - start_time:.2f} seconds")
        
    except ValueError:
        print("Please provide a valid integer for the number of digits.")
    
if __name__ == "__main__":
    main()