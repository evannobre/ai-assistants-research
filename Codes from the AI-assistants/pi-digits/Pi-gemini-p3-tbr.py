import sys

def extract(x, q, r, t):
    """
    Extracts a digit from the current state using the linear fractional 
    transformation (LFT).
    Formula: (q * x + r) // t
    """
    return (q * x + r) // t

def run_spigot(n):
    """
    Generates the first n digits of Pi using the unbounded spigot algorithm.
    """
    # Initial state of the LFT matrix:
    # [ q  r ]
    # [ 0  t ]
    # Initially identity: q=1, r=0, t=1
    q = 1
    r = 0
    t = 1
    
    # k tracks the term in the infinite series
    k = 1
    
    # Counters for output
    digit_count = 0
    line_buffer = []

    while digit_count < n:
        # Do both extract(3) and extract(4) as requested.
        # This checks the integer part of the LFT at the bounds.
        digit_3 = extract(3, q, r, t)
        digit_4 = extract(4, q, r, t)

        if digit_3 == digit_4:
            # The interval has collapsed to a single integer; it is safe to produce a digit.
            y = digit_3
            
            # Print/Store logic
            line_buffer.append(str(y))
            digit_count += 1
            
            if len(line_buffer) == 10:
                print(f"{''.join(line_buffer)}\t:{digit_count}")
                line_buffer = []

            # Update state to produce the digit (Matrix Multiplication)
            # Matrix B: [[10, -10y], [0, 1]]
            # New q = 10 * q
            # New r = 10 * (r - y * t)
            # t remains unchanged
            q = 10 * q
            r = 10 * (r - y * t)
            
        else:
            # The interval is not precise enough; consume the next term of the series.
            # Matrix A_k: [[k, 4k+2], [0, 2k+1]]
            # This corresponds to the series expansion of Pi.
            
            # New r = q * (4k+2) + r * (2k+1)
            # New t = t * (2k+1)
            # New q = q * k
            # Note: r must be calculated before q is updated.
            r = (q * (4 * k + 2)) + (r * (2 * k + 1))
            t = t * (2 * k + 1)
            q = q * k
            
            k += 1

    # Flush remaining digits if total is not a multiple of 10
    if line_buffer:
        print(f"{''.join(line_buffer).ljust(10)}\t:{digit_count}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            n_digits = int(sys.argv[1])
            run_spigot(n_digits)
        except ValueError:
            print("Error: Argument must be an integer.")
            sys.exit(1)
    else:
        # Default to 27 digits if no argument is provided
        run_spigot(27)