from decimal import Decimal, getcontext

def calculate_pi(digits):
    """
    Calculate Pi to the specified number of digits using the 
    Chudnovsky algorithm with arbitrary precision arithmetic.
    
    Args:
        digits (int): Number of digits of Pi to calculate
        
    Returns:
        Decimal: Pi calculated to the specified precision
    """
    # Set precision to a bit higher than requested to ensure accuracy
    getcontext().prec = digits + 10
    
    # Constants for Chudnovsky algorithm
    C = 426880 * Decimal(10005).sqrt()
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    K = Decimal(6)
    S = L
    
    # Number of iterations needed (approximately digits/14)
    iterations = digits // 14 + 10
    
    # Chudnovsky summation
    for i in range(1, iterations):
        M = M * (Decimal(i*i*i) - Decimal(i)) / (3 * Decimal(i) * Decimal(i) * Decimal(i))
        L += 545140134
        X *= -262537412640768000
        S += (M * L) / X
        K += 12

    pi = C / S
    
    # Return with the requested precision
    getcontext().prec = digits
    return +pi  # The unary plus forces re-rounding to current precision

def main():
    try:
        digits = int(input("Enter the number of Pi digits to calculate: "))
        if digits <= 0:
            print("Please enter a positive number.")
            return
            
        pi = calculate_pi(digits)
        
        print(f"\nPi to {digits} digits:")
        pi_str = str(pi)
        
        # Format with decimal point and proper digit count
        formatted_pi = pi_str[:1] + '.' + pi_str[1:digits+1]
        print(formatted_pi)
        
    except ValueError:
        print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()