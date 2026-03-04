def compute_pi_digits(n):
    len_array = (10 * n // 3) + 1
    a = [2] * len_array
    digits = []
    nines = 0
    predigit = None  # Initialize predigit to None to avoid leading zero

    while len(digits) < n:
        carry = 0

        # Process each element from end to start
        for i in reversed(range(len_array)):
            x = 10 * a[i] + carry * (i + 1)
            denom = 2 * i + 1
            quotient, remainder = divmod(x, denom)
            a[i] = remainder
            carry = quotient

        # Extract current carry components
        q, r = divmod(carry, 10)

        if predigit is not None:
            if prev_r == 9:
                current_nines += 1
            else:
                if prev_r == 10:
                    # Emit predigit + 1 followed by zeros
                    digits.append(predigit + 1)
                    digits.extend([0] * current_nines)
                else:
                    # Emit predigit followed by nines
                    digits.append(predigit)
                    digits.extend([9] * current_nines)
                current_nines = 0
                # Check if we've reached the desired number of digits
                if len(digits) >= n:
                    digits = digits[:n]
                    break

        # Update previous values for next iteration
        predigit = q
        prev_r = r
        current_nines = nines
        nines = 0

        # Handle current r
        if r == 9:
            nines += 1
        elif r == 10:
            nines = current_nines
            current_nines = 0
            prev_r = 0  # Force emission in next iteration
        else:
            current_nines = 0

    # After loop, check if any remaining predigit to add
    if len(digits) < n and predigit is not None:
        digits.append(predigit)
    # Truncate to exact n digits in case of overflow
    digits = digits[:n]
    return digits

def main():
    import sys
    n = int(sys.argv[1])
    digits = compute_pi_digits(n)
    # Print digits 10 per line with running total
    for i in range(0, n, 10):
        chunk = digits[i:i+10]
        line = ''.join(map(str, chunk))
        total = min(i + 10, n)
        print(f"{line.ljust(10)}\t{total}")

if __name__ == "__main__":
    main()