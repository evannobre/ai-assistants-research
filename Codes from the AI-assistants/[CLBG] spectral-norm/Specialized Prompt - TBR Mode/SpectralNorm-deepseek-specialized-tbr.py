import math
import sys

def A_element(i, j):
    k = i + j - 1
    n_val = (k - 1) * k // 2 + i
    return 1.0 / n_val

def matvec(v):
    n = len(v)
    u = [0.0] * n
    for i in range(1, n + 1):
        total = 0.0
        for j in range(1, n + 1):
            total += A_element(i, j) * v[j - 1]
        u[i - 1] = total
    return u

def matvec_transpose(v):
    n = len(v)
    u = [0.0] * n
    for i in range(1, n + 1):
        total = 0.0
        for j in range(1, n + 1):
            total += A_element(j, i) * v[j - 1]
        u[i - 1] = total
    return u

def matvec_ATA(v):
    u = matvec(v)
    return matvec_transpose(u)

def main():
    if len(sys.argv) < 2:
        n = 5500
    else:
        n = int(sys.argv[1])
    
    v = [1.0] * n
    norm_v = math.sqrt(sum(x * x for x in v))
    v = [x / norm_v for x in v]
    
    for _ in range(10):
        u = matvec(v)
        w = matvec_transpose(u)
        norm_w = math.sqrt(sum(x * x for x in w))
        v = [x / norm_w for x in w]
    
    u_final = matvec(v)
    w_final = matvec_transpose(u_final)
    v_dot_w = sum(v[i] * w_final[i] for i in range(n))
    spectral_norm = math.sqrt(v_dot_w)
    print("{:.9f}".format(spectral_norm))

if __name__ == "__main__":
    main()