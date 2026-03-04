import sys
from decimal import Decimal, getcontext

def compute_pi(n):
    """
    Generates n digits of Pi using the Chudnovsky algorithm 
    and the native decimal library.
    """
    # Set precision to N + extra digits to avoid rounding errors
    getcontext().prec = n + 10
    
    # Chudnovsky algorithm constants
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = L
    
    # Iterate roughly N/14 times (14 digits per iteration)
    # We use integers for loop counting to keep the logic clean
    iterations = n // 14 + 1
    
    for i in range(1, iterations):
        # Calculate the terms
        M = (K ** 3 - 16 * K) * M // (i ** 3)
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
        K += 12
        
    # Final calculation: Pi = C / S
    pi = C / S
    
    # Return pi as a string truncated to n digits (plus the "3.")
    return str(pi)[:n + 2] 

if __name__ == "__main__":
    # Handle command line arguments
    try:
        if len(sys.argv) != 2:
            print("Usage: python pi_gen.py <number_of_digits>")
            sys.exit(1)
            
        digits = int(sys.argv[1])
        if digits <= 0:
            raise ValueError("Number of digits must be positive.")
            
        print(f"Generating {digits} digits of Pi...")
        pi_value = compute_pi(digits)
        print("\nResult:")
        print(pi_value)
        
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")