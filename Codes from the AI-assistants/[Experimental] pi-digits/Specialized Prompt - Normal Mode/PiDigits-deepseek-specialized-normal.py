import decimal
import math
from datetime import datetime

def compute_pi(digits):
    """
    Compute pi to the specified number of digits using the Chudnovsky algorithm
    with arbitrary precision arithmetic.
    
    Args:
        digits (int): Number of digits of pi to compute
        
    Returns:
        str: Pi calculated to the specified precision
    """
    # Set the precision slightly higher than needed to prevent rounding errors
    decimal.getcontext().prec = digits + 10
    
    # Constants for the Chudnovsky algorithm
    C = 426880 * decimal.Decimal(10005).sqrt()
    M = 1
    L = 13591409
    X = 1
    K = 6
    S = L
    
    # Calculate the sum until convergence
    for i in range(1, digits//14 + 2):
        M = (K**3 - 16*K) * M // (i**3)
        L += 545140134
        X *= -262537412640768000
        S += decimal.Decimal(M * L) / X
        K += 12
    
    # Final calculation and rounding
    pi = C / S
    return str(pi)[:digits + 2]  # +2 to account for "3." at start

def validate_input(n):
    """
    Validate the input for pi digit calculation.
    
    Args:
        n (str): Input string to validate
        
    Returns:
        int: Validated number of digits or None if invalid
    """
    try:
        digits = int(n)
        if digits <= 0:
            print("Number of digits must be positive.")
            return None
        # Practical limitation based on system resources
        max_digits = 10**7  # ~10MB memory needed for 10M digits
        if digits > max_digits:
            print(f"Warning: Calculating more than {max_digits:,} digits may consume significant resources.")
            print(f"Your system has 16GB RAM and 10GB SSD available.")
            proceed = input("Do you want to continue? (y/n): ").lower()
            if proceed != 'y':
                return None
        return digits
    except ValueError:
        print("Please enter a valid positive integer.")
        return None

def main():
    print("Pi Digit Calculator")
    print(f"System: Ubuntu 24.10 64-bit | 16GB RAM | 10GB SSD")
    
    while True:
        user_input = input("\nEnter number of digits to compute (or 'q' to quit): ").strip()
        if user_input.lower() == 'q':
            break
            
        digits = validate_input(user_input)
        if digits is None:
            continue
            
        print(f"\nCalculating {digits:,} digits of pi...")
        start_time = datetime.now()
        
        try:
            pi_digits = compute_pi(digits)
            elapsed = datetime.now() - start_time
            
            # Display results and statistics
            print(f"\nComputation time: {elapsed.total_seconds():.2f} seconds")
            
            # Show a preview of the result
            preview_len = min(100, digits)
            print(f"\nFirst {preview_len} digits of pi:")
            print(pi_digits[:preview_len] + ("..." if digits > preview_len else ""))
            
            # Save to file option for large computations
            if digits > 100:
                save = input("\nSave full result to file? (y/n): ").lower()
                if save == 'y':
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"pi_digits_{digits}_{timestamp}.txt"
                    with open(filename, 'w') as f:
                        f.write(pi_digits)
                    print(f"Results saved to {filename}")
                    
        except MemoryError:
            print("Error: Computation requires more memory than available.")
            print("Try with a smaller number of digits.")
        except decimal.DivisionByZero:
            print("Error: Precision too high for the system's capabilities.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()]