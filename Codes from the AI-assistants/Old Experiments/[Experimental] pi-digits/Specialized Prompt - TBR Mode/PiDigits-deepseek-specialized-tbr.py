import math

def calculate_pi(N):
    # Validate input
    if N <= 0:
        raise ValueError("N must be a positive integer")
    
    # Scaling factor to maintain precision
    S = 10 ** (N + 10)
    
    # Initialize variables
    a = S
    sqrt_2_S_squared = math.isqrt(2 * S * S)
    b = (S * S) // sqrt_2_S_squared
    t = S // 4
    p = 1
    
    # Number of iterations (sufficient for ~2^20 digits)
    iterations = 20
    for _ in range(iterations):
        a_next = (a + b) // 2
        b = math.isqrt(a * b)
        delta = a - a_next
        t -= p * delta * delta // S
        a = a_next
        p *= 2
    
    # Calculate pi approximation
    pi_approx = (a + b) * (a + b) // (4 * t)
    pi_str = str(pi_approx)
    
    # Format the result
    if len(pi_str) < N + 1:
        raise RuntimeError("Insufficient iterations to compute the requested digits")
    
    return f"{pi_str[0]}.{pi_str[1:N+1]}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pi.py <number_of_digits>")
        sys.exit(1)
    
    try:
        N = int(sys.argv[1])
        result = calculate_pi(N)
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)