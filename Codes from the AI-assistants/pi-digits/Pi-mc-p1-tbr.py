# sketch: use integers and binary splitting; for production use existing libraries
# run: python3 pi_chudnovsky.py N
from decimal import Decimal, getcontext
from math import isqrt
import sys

def chudnovsky_terms(k):
    # compute using binary splitting (omitted: full recursion for brevity)
    pass

# set precision and compute k = ceil(N/14)
N = int(sys.argv[1])
getcontext().prec = N + 10
k = (N + 13)//14
# compute integer sum via binary splitting -> (P,Q,T)
# compute pi = (426880*sqrt(10005)) / (T/Q)
# format and print first N digits
