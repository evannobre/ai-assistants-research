import sys
from decimal import Decimal, getcontext

def spigot_pi(n_digits):
    """
    Implementation of the Spigot algorithm to calculate Pi to n_digits.
    """
    # Set precision for decimal calculations
    getcontext().prec = n_digits + 100  # Extra precision to avoid rounding errors
    
    # Initial values for the algorithm
    q, r, t, k, m, x = 1, 0, 1, 1, 3, 3
    digits = []
    
    # Calculate n_digits of Pi
    for j in range(n_digits):
        if 4 * q + r - t < m * t:
            # Extract the digit
            digits.append(m)
            # Update values for next iteration using the formula
            q, r, t, k, m, x = (10 * q, 10 * (r - m * t), t, k, 
                              (10 * (3 * q + r)) // t - 10 * m, x)
        else:
            # Update values without extracting a digit
            q, r, t, k, m, x = (q * k, (2 * q + r) * x, t * x, k + 1, 
                              (q * (7 * k + 2) + r * x) // (t * x), x + 2)
    
    return digits

def extract3(n_digits):
    """
    Extract method using base 3
    """
    # Set precision for decimal calculations
    getcontext().prec = n_digits + 100  # Extra precision to avoid rounding errors
    
    # Initial values for the algorithm in base 3
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3  # Using different variable names to match traditional implementation
    result = []
    
    count = 0
    while count < n_digits:
        if 4 * q + r - t < n * t:
            # We can extract a digit
            result.append(n)
            # Update for the next digit
            q, r, t, k, n, l = (3 * q, 3 * (r - n * t), t, k, 
                              (3 * (3 * q + r)) // t - 3 * n, l)
        else:
            # Need to transform
            q, r, t, k, n, l = (q * k, (2 * q + r) * l, t * l, k + 1, 
                              (q * (7 * k + 2) + r * l) // (t * l), l + 2)
        count += 1
    
    return result

def extract4(n_digits):
    """
    Extract method using base 4
    """
    # Set precision for decimal calculations
    getcontext().prec = n_digits + 100  # Extra precision to avoid rounding errors
    
    # Initial values for the algorithm in base 4
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3  # Using different variable names to match traditional implementation
    result = []
    
    count = 0
    while count < n_digits:
        if 4 * q + r - t < n * t:
            # We can extract a digit
            result.append(n)
            # Update for the next digit
            q, r, t, k, n, l = (4 * q, 4 * (r - n * t), t, k, 
                              (4 * (3 * q + r)) // t - 4 * n, l)
        else:
            # Need to transform
            q, r, t, k, n, l = (q * k, (2 * q + r) * l, t * l, k + 1, 
                              (q * (7 * k + 2) + r * l) // (t * l), l + 2)
        count += 1
    
    return result

def print_digits(digits):
    """
    Print the digits 10 to a line with a running total.
    """
    for i in range(0, len(digits), 10):
        line_digits = digits[i:i+10]
        line = ''.join(map(str, line_digits))
        print(f"{line} :{i + len(line_digits)}")

def main():
    # Parse command line argument for the number of digits
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 100  # Default value if no argument is provided
    
    print("Calculating Pi using base-10 Spigot algorithm:")
    digits = spigot_pi(n)
    print_digits(digits)
    
    print("\nCalculating Pi using extract(3) method:")
    digits_extract3 = extract3(n)
    print_digits(digits_extract3)
    
    print("\nCalculating Pi using extract(4) method:")
    digits_extract4 = extract4(n)
    print_digits(digits_extract4)

if __name__ == "__main__":
    main()