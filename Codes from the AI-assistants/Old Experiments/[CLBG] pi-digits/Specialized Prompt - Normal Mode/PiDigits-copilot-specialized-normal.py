from decimal import Decimal, getcontext

def spigot_pi_digits(n):
    # Set precision higher than required to ensure accuracy
    getcontext().prec = n + 2
    
    q, r, t, k, n1 = Decimal(1), Decimal(0), Decimal(1), 1, Decimal(3)
    pi_digits = []

    for _ in range(n):
        if 4 * q + r - t < n1 * t:
            pi_digits.append(int(n1))
            nr = Decimal(10) * (r - n1 * t)
            n1 = (3 * (q + nr) // t) - Decimal(1)
            r, q, t = Decimal(nr), q * Decimal(10), t * Decimal(10)
        else:
            nr = (2 * q + r) * k
            nt = t * k
            nq = q * k
            n1 += Decimal(k)

            r, q, t = Decimal(nr), Decimal(nq), Decimal(nt)
            k += 1

    return ''.join(map(str, pi_digits))

def print_pi_digits(n):
    pi = spigot_pi_digits(n)
    for i in range(0, len(pi), 10):
        print(f"{pi[i:i+10]} {i+10}/{n}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pi_spigot.py <number_of_digits>")
        sys.exit(1)
    
    num_digits = int(sys.argv[1])
    if num_digits < 1:
        print("Number of digits must be greater than 0.")
        sys.exit(1)
    
    print_pi_digits(num_digits)
