import sys

def spigot_pi(n):
    m = (n * 10 + 3) // 3
    a = [2] * (m + 1)  # Using 1-based indexing; a[1..m]
    digits = []
    pre_digit = 0
    for j in range(n):
        carry = 0
        # Process from m down to 1 (1-based)
        for i in range(m, 0, -1):
            x = a[i] * 10 + carry
            denominator = 2 * i - 1
            q, r = divmod(x, denominator)
            a[i] = r
            carry = q * i  # Multiply by the current index (1-based)
        # Process the next digit
        x = a[1] * 10 + carry
        a[1] = x % 10
        next_digit = x // 10
        # Handle overflow
        if next_digit == 10:
            pre_digit += 1
            next_digit = 0
        # Collect the previous digit if not the first iteration
        if j != 0:
            digits.append(pre_digit)
        pre_digit = next_digit
    digits.append(pre_digit)
    return digits

def main():
    if len(sys.argv) < 2:
        print("Usage: python pi_spigot.py <N>")
        sys.exit(1)
    n = int(sys.argv[1])
    digits = spigot_pi(n)
    # Print the digits 10 per line with running total
    count = 0
    line = []
    for d in digits:
        line.append(str(d))
        count += 1
        if len(line) == 10:
            print(" ".join(line) + f"\t: {count}")
            line = []
    if line:
        print(" ".join(line) + f"\t: {count}")

if __name__ == "__main__":
    main()