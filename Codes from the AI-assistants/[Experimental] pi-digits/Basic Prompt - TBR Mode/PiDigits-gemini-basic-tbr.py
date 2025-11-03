import decimal
import sys

def calculate_pi_gauss_legendre(n_digits):
    """
    Calculates Pi to n_digits decimal places using the Gauss-Legendre
    algorithm and Python's native decimal module for arbitrary precision.

    Args:
        n_digits: The number of decimal places of Pi to calculate (positive integer).

    Returns:
        A string representing Pi to n_digits decimal places.
        Returns None if input is invalid.
    """
    if not isinstance(n_digits, int) or n_digits <= 0:
        print("Error: Number of digits must be a positive integer.", file=sys.stderr)
        return None

    try:
        # Set precision for the decimal context.
        # Need slightly more digits than requested for intermediate calculations
        # and to ensure the final N digits are correct. Add a small buffer (e.g., 5).
        precision = n_digits + 5
        decimal.getcontext().prec = precision

        # Initialization using Decimal objects for arbitrary precision
        a = decimal.Decimal(1)
        # Calculate 1 / sqrt(2) using the current precision
        b = decimal.Decimal(1) / decimal.Decimal(2).sqrt()
        t = decimal.Decimal(1) / decimal.Decimal(4)
        p = decimal.Decimal(1)

        # Store the previous 'a' value to check for convergence
        a_old = a

        # Iteration loop
        # The loop converges quadratically. It stops when 'a' and 'b' are
        # indistinguishable at the current precision level (a == a_old).
        while True:
            a_next = (a + b) / 2
            b_next = (a * b).sqrt()
            t -= p * (a - a_next)**2
            a = a_next
            b = b_next
            p *= 2

            # Check if 'a' has converged (no change from the previous iteration)
            if a == a_old:
                break
            a_old = a # Update for the next iteration check

        # Final Pi calculation
        pi_approx = (a + b)**2 / (4 * t)

        # Format the output to exactly n_digits decimal places.
        # We use quantize with ROUND_DOWN for truncation to N decimal places.
        # Create a Decimal exponent string like '1e-100' for 100 digits.
        quantizer = decimal.Decimal('1e-' + str(n_digits))

        # Apply quantization to round/truncate pi_approx
        # ROUND_DOWN truncates after the Nth digit.
        pi_rounded = pi_approx.quantize(quantizer, rounding=decimal.ROUND_DOWN)

        return str(pi_rounded)

    except Exception as e:
        print(f"An error occurred during calculation: {e}", file=sys.stderr)
        return None

# --- Example Usage ---
if __name__ == "__main__":
    try:
        num_digits_to_calculate = int(input("Enter the number of decimal places for Pi: "))

        pi_value = calculate_pi_gauss_legendre(num_digits_to_calculate)

        if pi_value:
            print(f"\nPi calculated to {num_digits_to_calculate} decimal places:")
            print(pi_value)
            # Verify the number of digits after the decimal point
            actual_digits = len(pi_value.split('.')[1]) if '.' in pi_value else 0
            print(f"(Actual decimal digits generated: {actual_digits})")

    except ValueError:
        print("Invalid input. Please enter an integer.", file=sys.stderr)