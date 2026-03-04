# Needed for command-line arguments and exiting
import sys
import argparse

def pi_digits_spigot(n):
    """
    Generates n digits of Pi using the sequential Spigot algorithm.

    This implementation uses arbitrary precision integers provided by Python.
    It follows the standard iterative approach, including the check
    comparing results equivalent to extract(3) and extract(4) to
    determine when a digit is safe to output. It does not optimize
    away the core iterative steps.

    Args:
        n (int): The number of digits of Pi to generate.

    Yields:
        int: The next digit of Pi (after the decimal point).
    """
    # Initialize state variables for the algorithm
    # k is related to the terms in the series expansion
    # q, r, t represent the state of the transformation 2x2 matrix [[q,r],[0,t]]
    # or equivalently the rational function (q*x + r) / t
    k, q, r, t = 1, 1, 0, 1
    # l is used in the transformation, typically 2*k + 1
    l = 3

    digits_produced = 0
    while digits_produced < n:
        # --- Core Spigot Algorithm Step ---
        # Check if a digit can be safely extracted.
        # This implicitly performs the extract(3) and extract(4) comparison.
        # Calculate potential digit using the '3' factor (extract(3) equivalent)
        potential_digit_3 = (q * 3 + r) // t
        # Calculate potential digit using the '4' factor (extract(4) equivalent)
        potential_digit_4 = (q * 4 + r) // t

        if potential_digit_3 == potential_digit_4:
            # --- Produce Digit ---
            # If they match, the digit is safe to output.
            digit = potential_digit_3
            yield digit
            digits_produced += 1

            # --- Update state after producing a digit ---
            # This corresponds to applying the transformation [[10, -10*digit], [0, 1]]
            # Effectively subtracting the digit's value and preparing for the next decimal place.
            # r' = 10 * (r - digit * t)
            # q' = 10 * q
            # t' = t (remains unchanged in this step)
            # Note: We use 'r' and 'q' directly as Python handles large integers.
            r = 10 * (r - digit * t)
            q = 10 * q
            # State q, r updated. t, k, l remain for the *next* potential transformation.

        else:
            # --- Transform State ---
            # If extract(3) and extract(4) differ, the digit is not safe yet.
            # Apply the transformation based on k and l = 2k+1
            # This corresponds to composing with the matrix [[k, (2k+1)], [0, (2k+1)]]
            # q' = q * k
            # r' = (2*q + r) * l
            # t' = t * l
            # Use current k and l for this transformation
            nr = (2 * q + r) * l # Calculate new r first using old q, r, l
            nq = q * k           # Calculate new q using old q, k
            nt = t * l           # Calculate new t using old t, l

            # Update state variables
            q, r, t = nq, nr, nt

            # --- Update k and l for the next transformation step ---
            k = k + 1
            l = 2 * k + 1
            # State q, r, t, k, l are now ready for the next iteration's check or transformation.

def main():
    """
    Parses command-line arguments and runs the Pi digit generation.
    """
    parser = argparse.ArgumentParser(
        description="Generate N digits of Pi (after the decimal point) using a sequential Spigot algorithm.",
        epilog="Example: python pi_spigot.py 10000"
    )
    parser.add_argument(
        'n_digits',
        type=int,
        nargs='?', # Makes the argument optional
        default=27, # A small default if no argument is given
        help='The number of digits of Pi to calculate (default: 27)'
    )
    args = parser.parse_args()

    n = args.n_digits
    if n <= 0:
        print("Error: Number of digits must be positive.", file=sys.stderr)
        sys.exit(1)

    print(f"Calculating {n} digits of Pi...\n")

    # --- Output Formatting ---
    digits_generated = 0
    line_buffer = []
    digits_per_line = 10

    # Print the integer part '3.'
    print("3.", end="")

    # Consume the generator and print digits
    for digit in pi_digits_spigot(n):
        line_buffer.append(str(digit))
        digits_generated += 1

        # Check if the line buffer is full (or if it's the last digit)
        is_last_digit = (digits_generated == n)
        if len(line_buffer) == digits_per_line or is_last_digit:
            print("".join(line_buffer), end="")
            # Add padding spaces if it's the last line and not full
            if is_last_digit and len(line_buffer) < digits_per_line:
                 print(" " * (digits_per_line - len(line_buffer)), end="")

            print(f"\t:{digits_generated}")
            line_buffer = [] # Reset buffer for the next line

        # Add a newline every 10 lines (100 digits) for better readability with large N
        # if digits_generated % (digits_per_line * 10) == 0 and not is_last_digit:
        #      print() # Add extra spacing

    print(f"\nFinished calculating {n} digits.")

if __name__ == "__main__":
    main()