import sys

def spigot_pi_digits(n):
    """
    Implementation of the Spigot algorithm for calculating digits of π.
    Generates digits sequentially without optimizations.
    """
    # Initialize
    k = 0
    predigit = 0
    len = n * 10 // 3 + 1  # Enough length for n digits
    a = [2] * len
    
    digits = []
    total_digits = 0
    
    while k < n:
        # Step 1: Multiply by 10
        carry = 0
        for i in range(len-1, -1, -1):
            x = a[i] * 10 + carry
            a[i] = x % (2*i + 1)
            carry = x // (2*i + 1)
        
        # Step 2: Get the next digit
        q = carry // 10
        r = carry % 10
        
        # Step 3: Adjust the digit
        if q == 9:
            # Just accumulate this digit
            digits.append(str(q))
        elif q == 10:
            # Emit the previous predigit+1 and zeros
            digits.append(str((predigit + 1) % 10))
            for _ in range(k - total_digits):
                digits.append('0')
            total_digits = k + 1
            predigit = 0
        else:
            # Emit the previous predigit
            if k > 0:
                digits.append(str(predigit))
                total_digits += 1
            predigit = q
        
        # Print digits in batches of 10
        while len(digits) >= 10 and total_digits < n:
            print("".join(digits[:10]) + "\t%d" % (total_digits + 10))
            digits = digits[10:]
            total_digits += 10
        
        k += 1
    
    # Print any remaining digits
    if digits and total_digits < n:
        remaining = n - total_digits
        print("".join(digits[:remaining]) + "\t%d" % n)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python spigot.py <number_of_digits>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError
    except ValueError:
        print("Please provide a positive integer")
        sys.exit(1)
    
    spigot_pi_digits(n)