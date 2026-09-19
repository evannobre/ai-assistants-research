import sys
import math

def eval_A(i: int, j: int) -> float:
    """(i) computes the infinite matrix element A(i, j)"""
    return 1.0 / (((i + j) * (i + j + 1) // 2) + i + 1)

def eval_A_times_v(v: list[float]) -> list[float]:
    """(ii) computes A * v"""
    return [sum(eval_A(i, j) * v_j for j, v_j in enumerate(v)) for i in range(len(v))]

def eval_At_times_v(v: list[float]) -> list[float]:
    """(iii) computes A^T * v"""
    return [sum(eval_A(j, i) * v_j for j, v_j in enumerate(v)) for i in range(len(v))]

def eval_AtA_times_v(v: list[float]) -> list[float]:
    """(iv) computes A^T * (A * v)"""
    return eval_At_times_v(eval_A_times_v(v))

def main():
    # Capture command-line argument for matrix size, defaulting to 100
    n = 100
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Invalid argument. Using default N=100.")

    u = [1.0] * n
    v = [0.0] * n

    # Power method: 10 iterations
    for _ in range(10):
        v = eval_AtA_times_v(u)
        u = eval_AtA_times_v(v)

    # Compute final spectral norm elements
    vBv = sum(u_i * v_i for u_i, v_i in zip(u, v))
    vv = sum(v_i * v_i for v_i in v)

    # Output precise to 9 decimal places
    print(f"{math.sqrt(vBv / vv):.9f}")

if __name__ == '__main__':
    main()