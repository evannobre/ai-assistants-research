import sys

def spigot_pi(n):
    # Initialize variables for the algorithm
    n = int(n) + 1
    digits = [2] * (10 * n // 3)
    pi_digits = []
    carry = 0

    for i in range(n):
        sum = 0
        for j in range(len(digits), 0, -1):
            sum = sum * j + 10 * digits[j - 1]
            digits[j - 1] = sum % (2 * j - 1)
            sum //= (2 * j - 1)

        digits[0] = sum % 10
        carry = sum // 10

        # Extract digit
        if carry == 9:
            for k in range(len(pi_digits)):
                if pi_digits[k] == 9:
                    pi_digits[k] = 0
                else:
                    pi_digits[k] += 1
                    break
            carry = 0
        elif carry == 10:
            pi_digits.append(0)
            carry = 1
        else:
            pi_digits.append(carry)
            carry = 0

    # Print digits 10-to-a-line with running total
    for i in range(0, len(pi_digits), 10):
        print("".join(map(str, pi_digits[i:i + 10])), "\t:", i + 10)

if __name__ == "__main__":
    # Set a larger value to test performance
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    spigot_pi(n)