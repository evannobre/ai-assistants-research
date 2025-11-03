from decimal import Decimal, getcontext
from math import ceil

def pi_chudnovsky_binary_splitting(N):
    # 1. set precision a bit above N
    getcontext().prec = N + 20

    # 2. number of terms
    K = ceil(N / 14.1816476)

    # 3. binary-split functions
    def bs(a, b):
        if b - a == 1:
            # base case: single term
            k = a
            # P = (6k)! / ((3k)! (k!)^3)
            # Q = (-640320^3)^k
            # T = P * (13591409 + 545140134*k) * (-1)^k
            P = factorial(6*k) // (factorial(3*k) * factorial(k)**3)
            Q = (-1)**k * 640320**(3*k)
            T = P * (13591409 + 545140134*k) * (-1)**k
            return P, Q, T
        # split
        m = (a + b) // 2
        P1, Q1, T1 = bs(a, m)
        P2, Q2, T2 = bs(m, b)
        P = P1 * P2
        Q = Q1 * Q2
        T = T1 * Q2 + P1 * T2
        return P, Q, T

    # 4. perform binary splitting
    P, Q, T = bs(0, K)

    # 5. compute pi
    one_over_pi = Decimal(12) * Decimal(T) / Decimal(Q)
    pi = +one_over_pi ** (-1)   # unary plus applies the context precision

    # 6. return string of digits
    s = format(pi, f'.{N}f')
    return s

# Example: compute 1000 digits
digits = pi_chudnovsky_binary_splitting(1000)
print(digits)
