from decimal import Decimal, getcontext
import math
import sys

def chudnovsky_bs(a, b):
    """
    Returns (P(a,b), Q(a,b), T(a,b)) for the Chudnovsky series,
    in integer form, via binary splitting.
    """
    if b - a == 1:
        # base case: single term k = a
        k = a
        # P = (6k)! / ( (3k)! (k!)^3 ) * (−1)^k
        # but we factor it differently to avoid huge factorials here
        P = Decimal(math.factorial(6*k)) // (math.factorial(3*k) * math.factorial(k)**3)
        if k & 1:
            P = -P
        T = P * (13591409 + 545140134 * k)
        Q = Decimal(640320)**(3*k)
        return (P, Q, T)
    else:
        m = (a + b) // 2
        P1, Q1, T1 = chudnovsky_bs(a, m)
        P2, Q2, T2 = chudnovsky_bs(m, b)
        P = P1 * P2
        Q = Q1 * Q2
        T = T1 * Q2 + P1 * T2
        return (P, Q, T)

def compute_pi(n_digits):
    # set working precision a bit higher to guard intermediate round-off
    getcontext().prec = n_digits + 20

    # number of terms needed
    K = int(n_digits / 14.181647646263415) + 1

    P, Q, T = chudnovsky_bs(0, K)

    # pi = Q * 426880 * sqrt(10005) / T
    sqrtC = Decimal(10005).sqrt()
    pi = (Q * Decimal(426880) * sqrtC) / T

    # round to exactly n_digits
    return +pi  # unary plus applies the context precision

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 compute_pi.py <N_digits>")
        sys.exit(1)
    N = int(sys.argv[1])
    pi_str = format(compute_pi(N), f'.{N}f')
    print(pi_str)
