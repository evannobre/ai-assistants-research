import sys
import math

def eval_A(i, j):
    """
    (i) Computes the infinite matrix element A(i, j).
    Uses standard 0-indexed coordinates.
    """
    return 1.0 / (((i + j) * (i + j + 1) // 2) + i + 1)

def eval_A_times_u(u):
    """
    (ii) Computes A * v (represented here as u).
    """
    n = len(u)
    # Using list comprehensions for native C-level optimization in Python
    return [sum(eval_A(i, j) * u[j] for j in range(n)) for i in range(n)]

def eval_At_times_u(u):
    """
    (iii) Computes Aᵗ * v.
    Notice the coordinates in eval_A are flipped to (j, i) for the transpose.
    """
    n = len(u)
    return [sum(eval_A(j, i) * u[j] for j in range(n)) for i in range(n)]

def eval_AtA_times_u(u):
    """
    (iv) Computes Aᵗ * (A * v).
    """
    return eval_At_times_u(eval_A_times_u(u))

def main():
    # Default to 5500 unless overridden by command-line argument
    n = 5500
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Invalid integer argument, defaulting to n={n}")
            
    # Initialize the vector u with 1s
    u = [1.0] * n

    # Perform 10 iterations of the power method.
    # Each loop applies AᵗA twice (u -> v, then v -> u), making 20 steps total.
    for _ in range(10):
        v = eval_AtA_times_u(u)
        u = eval_AtA_times_u(v)

    # Compute the Rayleigh quotient (vBv / vv)
    vBv = sum(u[i] * v[i] for i in range(n))
    vv = sum(v[i] * v[i] for i in range(n))

    # The spectral norm is the square root of the Rayleigh quotient
    print(f"{math.sqrt(vBv / vv):.9f}")

if __name__ == '__main__':
    main()