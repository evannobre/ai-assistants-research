import sys
import math

def main():
    if len(sys.argv) < 2:
        n = 5500
    else:
        n = int(sys.argv[1])
    
    denom = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = i + j
            denom[i][j] = s * (s + 1) // 2 + i + 1

    def A(i, j):
        return 1.0 / denom[i-1][j-1]
    
    def multiply_A(v):
        size = len(v)
        u = [0.0] * size
        for i in range(size):
            total = 0.0
            for j in range(size):
                total += v[j] / denom[i][j]
            u[i] = total
        return u

    def multiply_At(v):
        size = len(v)
        w = [0.0] * size
        for j in range(size):
            total = 0.0
            for i in range(size):
                total += v[i] / denom[i][j]
            w[j] = total
        return w

    def multiply_AtA(v):
        u = multiply_A(v)
        return multiply_At(u)
    
    v = [1.0] * n
    nrm = math.sqrt(sum(x*x for x in v))
    v = [x / nrm for x in v]
    
    for _ in range(10):
        v = multiply_AtA(v)
        nrm = math.sqrt(sum(x*x for x in v))
        v = [x / nrm for x in v]
    
    spectral_norm = math.sqrt(nrm)
    print("{:.9f}".format(spectral_norm))

if __name__ == '__main__':
    main()