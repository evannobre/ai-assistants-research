#!/usr/bin/env python3
import sys

def extract(x: int, q: int, r: int, t: int) -> int:
    """
    Extracts a prospective digit by applying the linear fractional transformation.
    The formula is floor((q * x + r) / t).
    """
    return (q * x + r) // t

def generate_pi_digits():
    """
    Generates digits of Pi using the unbounded Spigot algorithm.
    Maintains state variables q, r, t for the LFT numerator and denominator.
    """
    # Initial state for the LFT transformation
    q, r, t, k = 1, 0, 1, 1
    
    while True:
        # Extract both 3 and 4 to check if the next digit has converged
        d3 = extract(3, q, r, t)
        d4 = extract(4, q, r, t)

        if d3 == d4:
            # Convergence reached; yield the digit
            yield d3
            
            # Consume the digit by shifting the state (multiply by 10)
            q, r, t = q * 10, 10 * (r - d3 * t), t
        else:
            # Produce the next term in the series (matrix multiplication)
            # using the LFT: [[k, 4*k+2], [0, 2*k+1]]
            q_next = q * k
            r_next = (2 * k + 1) * r + (4 * k + 2) * q
            t_next = t * (2 * k + 1)
            
            q, r, t = q_next, r_next, t_next
            k += 1

def main():
    """
    Main entry point. Parses the command-line argument for N digits
    and formats the output to 10-to-a-line with the running total.
    """
    # Parse the command line argument for N digits (default: 10000)
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    except ValueError:
        print("Error: The argument for N must be an integer.")
        sys.exit(1)

    pi_generator = generate_pi_digits()
    
    digits_printed = 0
    line_digits = []

    while digits_printed < n:
        line_digits.append(str(next(pi_generator)))
        digits_printed += 1

        # Format output: 10 digits per line, followed by a tab and the running total
        if digits_printed % 10 == 0:
            print(f"{''.join(line_digits)}\t:{digits_printed}")
            line_digits.clear()

    # Handle the final line if N is not a multiple of 10 (pad with spaces)
    if line_digits:
        chunk = ''.join(line_digits)
        pad = ' ' * (10 - len(chunk))
        print(f"{chunk}{pad}\t:{digits_printed}")

if __name__ == '__main__':
    main()