import sys

def spigot_pi(n, extract_method=3):
    """
    Calculate the first n digits of pi using the Spigot algorithm.
    extract_method can be 3 or 4 to choose between two different extraction methods.
    """
    # Initialize
    length = (10 * n) // 3 + 1
    a = [2] * length
    pi_digits = []
    carry = 0
    
    for digit_position in range(1, n + 1):
        total = 0
        
        # Work backwards through the array
        for i in range(length - 1, -1, -1):
            numerator = i
            denominator = 2 * i + 1
            total = total * i + a[i] * 10
            a[i] = total % denominator
            total = total // denominator
        
        # Extract the digit
        if extract_method == 3:
            # Method 3: digit = (carry + total // 10) % 10
            digit = (carry + total // 10) % 10
            carry = total % 10
        elif extract_method == 4:
            # Method 4: digit = carry + total // 10
            digit = carry + total // 10
            carry = total % 10
            if digit >= 10:
                carry += digit // 10
                digit = digit % 10
        
        # Adjust digits if we carried over a 10
        for i in range(len(pi_digits) - 1, -1, -1):
            if pi_digits[i] == 9 and digit == 10:
                pi_digits[i] = 0
                digit = 0
                if i > 0:
                    pi_digits[i-1] += 1
                else:
                    # This would only happen for the very first digit
                    pi_digits.insert(0, 1)
                    digit = 0
            else:
                break
        
        if digit == 10:
            digit = 0
        
        pi_digits.append(digit)
    
    return pi_digits

def print_pi_digits(pi_digits):
    """Print the digits 10 per line with running total"""
    print("3.", end="")
    count = 1  # We've already printed the "3"
    for i, digit in enumerate(pi_digits[1:], 1):
        print(digit, end="")
        count += 1
        if i % 10 == 0:
            print(f"\t:{count}")
        elif i % 5 == 0:
            print(" ", end="")
    if (len(pi_digits) - 1) % 10 != 0:
        print(f"\t:{count}")
    print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python spigot_pi.py <number_of_digits>")
        return
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please provide an integer number of digits")
        return
    
    if n <= 0:
        print("Number of digits must be positive")
        return
    
    print("Calculating using extract(3) method:")
    pi_digits = spigot_pi(n, extract_method=3)
    print_pi_digits(pi_digits)
    
    print("\nCalculating using extract(4) method:")
    pi_digits = spigot_pi(n, extract_method=4)
    print_pi_digits(pi_digits)

if __name__ == "__main__":
    main()