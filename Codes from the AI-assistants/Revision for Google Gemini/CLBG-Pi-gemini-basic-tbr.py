import sys

def extract(x, q, r, t):
    """
    Evaluates the linear fractional transformation at point x.
    """
    return (q * x + r) // t

def generate_pidigits(n):
    """
    Yields 'n' digits of Pi using the step-by-step single-threaded Spigot algorithm.
    State is maintained in integers q, r, t which grow to arbitrary precision.
    """
    # Initial state matrix [q, r; s, t]. 
    # Because s is always 0, we only need to track q, r, and t.
    q, r, t = 1, 0, 1
    k = 1
    i = 0
    
    while i < n:
        # Step 1: Compute both extract(3) and extract(4) 
        # (Explicitly not optimizing away the work)
        d3 = extract(3, q, r, t)
        d4 = extract(4, q, r, t)
        
        # Step 2: If the integer parts match, we have safely found the next digit
        if d3 == d4:
            yield d3
            i += 1
            
            # Compose from the left with [10, -10*d3; 0, 1] to consume the digit
            q, r, t = q * 10, 10 * (r - d3 * t), t
        else:
            # Step 3: Otherwise, compose from the right with [k, 4k+2; 0, 2k+1] 
            # to advance the series
            q, r, t = q * k, q * (4 * k + 2) + r * (2 * k + 1), t * (2 * k + 1)
            k += 1

def main():
    # Read target number of digits from command line argument, defaulting to 10000
    n = 10000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Error: Please provide a valid integer for N.")
            sys.exit(1)

    digits = []
    count = 0
    
    # Process and format the digits
    for digit in generate_pidigits(n):
        digits.append(str(digit))
        count += 1
        
        # Print 10 digits per line, followed by a tab and the running total
        if count % 10 == 0:
            print(f"{''.join(digits)}\t:{count}")
            digits.clear()
    
    # If the total requested digits isn't a multiple of 10, pad with spaces and print
    if count % 10 != 0:
        print(f"{''.join(digits):<10}\t:{count}")

if __name__ == "__main__":
    main()