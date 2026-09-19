import sys
from decimal import Decimal, getcontext

def compute_pi(digits):
    # Set precision a few digits higher than requested to avoid rounding errors at the final decimal places
    getcontext().prec = digits + 5

    # Initialize Gauss-Legendre variables
    a = Decimal(1)
    b = Decimal(1) / Decimal(2).sqrt()
    t = Decimal(1) / Decimal(4)
    p = Decimal(1)

    while True:
        # Calculate next values
        a_next = (a + b) / 2
        b_next = (a * b).sqrt()
        t_next = t - p * (a - a_next)**2
        p_next = 2 * p
        
        # If 'a' stops changing at our current precision level, we've converged
        if a == a_next:
            break
            
        # Update variables for the next iteration
        a, b, t, p = a_next, b_next, t_next, p_next

    # Final calculation for Pi
    pi = ((a + b)**2) / (4 * t)
    
    # Convert to string and slice to exactly the requested number of decimal places
    # We add 2 to account for the "3." at the beginning
    pi_str = str(pi)
    return pi_str[:digits + 2]

if __name__ == "__main__":
    # Ensure a command-line argument is passed
    if len(sys.argv) != 2:
        print("Usage: python pi_generator.py <number_of_digits>")
        sys.exit(1)
        
    try:
        n_digits = int(sys.argv[1])
        if n_digits <= 0:
            raise ValueError
    except ValueError:
        print("Error: Please provide a positive integer for the number of digits.")
        sys.exit(1)
        
    # Compute and print Pi
    print(compute_pi(n_digits))