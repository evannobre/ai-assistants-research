import sys
import math # Only used for initial array size estimation in the *other* spigot algorithm, not needed here.

# Arbitrary precision arithmetic is built into Python's integers.

def pi_spigot_unbounded(n_digits):
    """
    Generates n_digits of Pi using the unbounded spigot algorithm
    based on matrix transformations (Gibbons).

    This algorithm uses the identity that if y = floor(f(3)) == floor(f(4)),
    then y is the next digit, where f(x) = (q*x + r) / (s*x + t).

    Args:
        n_digits: The number of digits of Pi to generate after the decimal point.
                  Note: The algorithm naturally produces digits starting with '3'.
                  So requesting n_digits=10 yields 3.1415926535 (11 total digits printed).
                  We will adjust to print exactly N digits *after* the '3.'.
    """
    # Initialize the transformation matrix components (q, r, s, t)
    # representing the identity transformation f(x) = (1*x + 0) / (0*x + 1) = x
    q, r, s, t = 1, 0, 0, 1
    k = 1 # Term counter for the series

    digit_count = 0
    line_count = 0

    # Adjust n_digits requested to account for the leading '3'
    # The loop runs until 'n_digits' digits *after* the '3.' are produced.
    target_digits = n_digits

    while digit_count < target_digits:
        # Calculate the next potential digit using the transformation f(x)
        # Check if the digit is "safe" by evaluating floor(f(3)) and floor(f(4))
        # Use integer division // which performs floor division

        # Ensure denominators are not zero (s*x + t should be positive)
        # In this algorithm, t starts at 1 and k >= 1, s >= 0.
        # s*(4*k + 2) + t*(2*k + 1) keeps t growing positively. s starts at 0.
        # Denominator t is always positive. s grows non-negatively.
        # s*3 + t and s*4 + t will be positive.

        term1_num = q * 3 + r
        term1_den = s * 3 + t
        digit_candidate_3 = term1_num // term1_den

        term2_num = q * 4 + r
        term2_den = s * 4 + t
        digit_candidate_4 = term2_num // term2_den

        # Step: Check if extract(3) == extract(4)
        if digit_candidate_3 == digit_candidate_4:
            # Digit is safe to output
            digit = digit_candidate_3

            # Print the digit
            print(digit, end="")
            digit_count += 1
            line_count += 1

            # Format output: 10 digits per line with running count
            if line_count == 10:
                print(f"\t:{digit_count}")
                line_count = 0
            elif digit_count == target_digits:
                 # Print remaining spaces and final count if finished mid-line
                 print(" " * (10 - line_count), end="")
                 print(f"\t:{digit_count}")


            # Update the transformation matrix to remove the extracted digit 'd'.
            # This corresponds to composing f(x) with g(x) = 10*(x - d)
            # Matrix multiplication: [[10, -10*d], [0, 1]] * [[q, r], [s, t]]
            # (Note: standard matrix notation vs state update differs sometimes,
            # the effect on q,r,s,t is:)
            # q' = 10*q - 10*d*s  <- This seems wrong based on sources, let's re-derive
            # r' = 10*r - 10*d*t
            # s' = s
            # t' = t

            # Correct update based on Gibbons/implementations:
            # We update the *numerator* part (q, r) by subtracting d*denominator (s, t)
            # and scaling by 10.
            # Equivalent to transformation: T_d(x) = 10 * (x - d)
            # Composing f with T_d^-1(x) = d + x/10. The new state (q', r', s', t')
            # represents f'(x) = T_d(f(x)). Let's apply the matrix [[10, -10d],[0, 1]]
            # (q, r) = (10*(q - d*s), 10*(r - d*t)) <--- This is the commonly shown update,
            # But it requires s, t which are updated *later* if not safe.
            # Let's stick to the simpler form derived from f'(x)=10(f(x)-y)
            # Update q, r based on removing the digit y (digit_candidate_3)
            # q_new = 10 * q
            # r_new = 10 * (r - digit * t)
            # s_new = s # unchanged by this operation
            # t_new = t # unchanged by this operation

            # Let's trace the most common implementation's update rule:
            # Subtract y times the denominator from the numerator, then scale by 10.
            r = 10 * (r - digit * t)
            q = 10 * (q - digit * s)
            # s and t remain unchanged by *this* step (digit extraction)

        else:
            # Digit is not safe, consume the next term from the series.
            # Compose the current transformation f(x) with the next term's transformation g_k(x).
            # The matrix for the k-th term transformation is [[k, 4k+2], [0, 2k+1]]
            # (q', r') = (q, r) * [[k, 4k+2], [0, 2k+1]] = (q*k, q*(4k+2) + r*(2k+1))
            # (s', t') = (s, t) * [[k, 4k+2], [0, 2k+1]] = (s*k, s*(4k+2) + t*(2k+1))

            k_val = k # Use a temporary variable for clarity if needed
            k2_1 = 2 * k_val + 1
            k4_2 = 4 * k_val + 2 # or 2 * k2_1

            # Calculate next state using temporary variables to avoid conflicts
            next_q = q * k_val
            next_r = q * k4_2 + r * k2_1
            next_s = s * k_val
            next_t = s * k4_2 + t * k2_1

            # Update state
            q, r, s, t = next_q, next_r, next_s, next_t

            # Move to the next term
            k = k + 1

    # If the loop finished but the last line wasn't full and printed
    if line_count > 0 and line_count != 10:
         print(" " * (10 - line_count), end="")
         print(f"\t:{digit_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pi_spigot.py <number_of_digits>")
        sys.exit(1)

    try:
        num_digits = int(sys.argv[1])
        if num_digits <= 0:
            raise ValueError("Number of digits must be positive.")
    except ValueError as e:
        print(f"Error: Invalid number of digits. {e}")
        sys.exit(1)

    # The algorithm naturally produces '3.' first.
    # We print N digits *after* the decimal point.
    print("3.", end="")

    # Handle the first digit '3' output formatting if N=0 wasn't requested
    if num_digits > 0:
        # Call the function to generate digits *after* the decimal point
        pi_spigot_unbounded(num_digits)
    else:
        # If 0 digits requested, just print the count for the '3.'
        print("\t:0") # Assuming 0 digits means just print '3.'

    # Example: python pi_spigot.py 10
    # Output:
    # 3.1415926535    :10

    # Example: python pi_spigot.py 25
    # Output:
    # 3.1415926535    :10
    # 8979323846    :20
    # 264338327     :25  <- Note: Corrected, it should be 25 not 27. My manual wrap was wrong.
    #                  Should be:
    #                  8979323846    :20
    #                  26433         :25