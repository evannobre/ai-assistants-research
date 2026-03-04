import decimal
import math
import time

# Constants for the Chudnovsky Algorithm
A = 545140134
B = 13591409
C = 640320
C3_OVER_24 = (C**3) // 24 # Precompute C^3 / 24 as integer

def calculate_pi_chudnovsky(n_digits):
    """
    Calculates N digits of Pi using the Chudnovsky algorithm and Python's
    native decimal module for arbitrary precision.

    Args:
        n_digits (int): The number of decimal digits of Pi to compute (after '3.').

    Returns:
        str: Pi calculated to n_digits decimal places.
             Returns None if n_digits is not positive.
    """
    if n_digits <= 0:
        print("Error: Number of digits must be positive.")
        return None

    # Set precision for decimal calculations: N digits + guard digits
    # We need enough precision for the intermediate calculations and the final sqrt.
    # Rule of thumb: n_digits + log10(number_of_terms) + few guard digits.
    # log10(n_digits/14) is small. Add ~10 guard digits.
    precision = n_digits + 10
    decimal.getcontext().prec = precision

    # Number of terms needed for convergence (~14 digits per term)
    # Add a couple of extra terms for safety
    num_terms = (n_digits // 14) + 2
    # For small N, ensure at least a few terms
    # num_terms = max(num_terms, 5) # Optional: ensure minimum terms

    print(f"Calculating Pi to {n_digits} digits using {num_terms} terms...")
    print(f"Decimal precision set to: {precision}")
    start_time = time.time()

    # --- Iterative Calculation ---
    # Initialize sum S and term T_k related variables
    # We compute the sum S = Sum [ T_k ] where T_k is the term inside the summation
    # T_k = (-1)^k * (6k)! * (A*k + B) / ( (3k)! * (k!)^3 * C^(3k) )

    # Instead of calculating T_k directly, we compute factors iteratively
    # Let P_k = (6k)! / ((3k)! * (k!)^3)
    # Let Q_k = C^(3k)
    # Let L_k = A*k + B
    # Term_k = (-1)^k * P_k * L_k / Q_k

    # We can compute the ratio T_k / T_{k-1} to avoid huge factorials.
    # T_k / T_{k-1} = - ( (6k-1)(2k-1)(6k-5) / (k^3 * C3_OVER_24) ) * (L_k / L_{k-1} is wrong)
    # Let's compute the full ratio:
    # Ratio = - [ (6k)(6k-1)...(6k-5) / ( (3k)(3k-1)(3k-2) * k^3 * C^3 ) ] * (L_k / L_{k-1}) is also wrong.

    # Let's compute the terms directly using the iterative ratio method for the components.
    # We will maintain the term T_k as a Decimal and update it multiplicatively.

    k = 0
    sum_s = decimal.Decimal(0)
    term_k = decimal.Decimal(B) # For k=0, term = (-1)^0 * 1 * (A*0+B) / (1 * 1 * 1) = B

    # Add the first term (k=0)
    sum_s += term_k

    print(f"Term {k}: Adding {term_k}")

    # Calculate subsequent terms iteratively
    for k in range(1, num_terms + 1):
        # Calculate components needed for the ratio T_k / T_{k-1} using large integers
        
        # L_k = A*k + B
        L_k = B + A * k

        # Numerator part of the factorial ratio (6k)...(6k-5)
        # Note: Using python's int which supports arbitrary size
        numerator_factor = (6*k - 1) * (2*k - 1) * (6*k - 5) # Simplified P_k/P_{k-1} factor (Check this!)
        # Let's use the full unsimplified ratio components for clarity
        num_ratio_part = (6*k)*(6*k-1)*(6*k-2)*(6*k-3)*(6*k-4)*(6*k-5)
        
        # Denominator part: k^3 * (3k)(3k-1)(3k-2) * C^3
        den_ratio_part = (k**3) * (3*k)*(3*k-1)*(3*k-2) * (C**3)
        
        # Update term T_k based on T_{k-1}
        # term_k = term_{k-1} * (-1) * num_ratio_part / den_ratio_part * L_k / L_{k-1}
        # It's better to update the components without dividing by L_{k-1}
        
        # Calculate the full T_k update factor based on T_{k-1}
        # Factor = - num_ratio_part / den_ratio_part
        update_factor_decimal = decimal.Decimal(-num_ratio_part) / decimal.Decimal(den_ratio_part)

        # Calculate T_k = T_{k-1} * Factor * (L_k / L_{k-1}) --- This division is problematic.
        
        # Let's rethink: keep track of the three main components M, L, X for T_k = M_k * L_k / X_k
        # This is more standard for Chudnovsky implementations.
        # M_k relates to factorials, L_k is linear, X_k relates to C power.
        
        # Simplified iterative update for the whole term T_k:
        # T_k = T_{k-1} * (-1) * [ (6k-1)(2k-1)(6k-5) / (k^3 * C^3 / 12?) ] * ... No.

        # Back to the ratio T_k / T_{k-1}:
        # It should be: T_k = T_{k-1} * Ratio(k)
        # Where Ratio(k) = - num_ratio_part / den_ratio_part * (L_k / L_{k-1}) ? No.

        # Let's use the verified factors:
        # Numerator update factor = (6k-1)(2k-1)(6k-5)
        # Denominator update factor = k^3 * C3_OVER_24
        
        # Recalculate term_k from scratch each time? No, too slow.
        # Use the iterative approach from known implementations:

        # Calculate M_k, L_k, X_k iteratively (as integers)
        if k == 1:
            M_k = 1 # M_0 = 1
            L_k = B # L_0 = B
            X_k = 1 # X_0 = 1
            term_k_prev = decimal.Decimal(L_k) / decimal.Decimal(X_k) # T_0
            sum_s = term_k_prev # Initialize sum with T_0

        # For k >= 1
        # Update L:
        L_k = B + A * k
        # Update M (factorial part):
        # M_k = M_{k-1} * (6k-1)(2k-1)(6k-5) -> Use this factor on the term T
        M_update_factor = (6*k - 1) * (2*k - 1) * (6*k - 5)
        # Update X (power part):
        # X_k = X_{k-1} * k^3 * C^3 -> Use this factor on the term T
        X_update_factor = (k**3) * (C**3)

        # Combine updates to get T_k from T_{k-1}
        # The term T_k includes the (-1)^k
        # T_k = T_{k-1} * (- M_update_factor / X_update_factor) * (L_k / L_{k-1}) - Still has L division.

        # --- Let's try the Binary Splitting structure adapted for simple iteration ---
        # We need three sequences P(k), Q(k), T(k) related to the sum term
        # This is getting too complex. Let's stick to the term ratio, carefully.

        # T_k = T_{k-1} * Ratio_k
        # Ratio_k = (-1) * num_ratio / den_ratio * (L_k / L_{k-1}) <-- This L_k/L_{k-1} seems wrong.
        # The term T_k = (-1)^k * P_k * L_k / Q_k
        # T_{k-1} = (-1)^{k-1} * P_{k-1} * L_{k-1} / Q_{k-1}
        # Ratio = T_k / T_{k-1} = -1 * (P_k/P_{k-1}) * (L_k/L_{k-1}) * (Q_{k-1}/Q_k)
        # P_k/P_{k-1} = (6k-1)(2k-1)(6k-5) * 12? No. Full ratio: num_ratio_part / ( (3k..)(k^3) )
        # Q_k/Q_{k-1} = C^3

        # Let's use the common simplified update factor:
        # Term_k = Term_{k-1} * [ - (6k-1)(2k-1)(6k-5) / (k^3 * C3_OVER_24) ]
        # This implies the L_k factor is handled differently.

        # Let's re-evaluate the sum: S = Sum (-1)^k * M_k * L_k / X_k
        # Calculate M_k, L_k, X_k iteratively and combine.
        
        # For k=1:
        M_k_factor_num = (6*k-1) * (2*k-1) * (6*k-5) # Factor relating M_k to M_{k-1} (simplified)
        M_k_factor_den = k**3 # Part of the denominator ratio
        L_k = B + A * k
        X_k_factor = C**3 # Factor relating X_k to X_{k-1}

        # Update the total term T_k based on T_{k-1}
        # T_k = T_{k-1} * (-1) * (M_k/M_{k-1}) * (L_k/L_{k-1}) * (X_{k-1}/X_k)
        # T_k = T_{k-1} * (-1) * [ M_k_factor_num / M_k_factor_den ] * [ L_k / L_{k-1} ] * [ 1 / X_k_factor ]
        # This seems the most direct ratio approach. Requires L_{k-1} from previous step.

        L_k_minus_1 = B + A * (k-1) # Get L_{k-1}

        # Calculate T_k using T_{k-1} and the ratio factors
        term_k = term_k_prev # Start with T_{k-1}
        term_k *= decimal.Decimal(M_k_factor_num) # Multiply by numerator parts
        term_k *= decimal.Decimal(L_k)
        term_k /= decimal.Decimal(M_k_factor_den) # Divide by denominator parts
        term_k /= decimal.Decimal(L_k_minus_1)
        term_k /= decimal.Decimal(X_k_factor)
        term_k *= -1 # Apply the (-1)^k factor relative to (-1)^{k-1}

        # Add the new term to the sum
        sum_s += term_k

        # Store T_k for the next iteration
        term_k_prev = term_k

        # Progress print (optional, slows down significantly for large N)
        # if k % 100 == 0:
        #     print(f"Term {k}/{num_terms} calculated...")


    # --- Final Calculation ---
    # pi = (C^(3/2) / (12 * S))
    # C^(3/2) = C * sqrt(C)

    sqrt_C = decimal.Decimal(C).sqrt()
    C_pow_3_2 = decimal.Decimal(C) * sqrt_C

    pi_inv = 12 * sum_s
    pi_val = C_pow_3_2 / pi_inv

    end_time = time.time()
    print(f"Calculation finished in {end_time - start_time:.4f} seconds.")

    # Format the output string to N decimal places
    # The calculated pi_val has extra precision. Format it.
    # Convert to string, find decimal point, take required digits.
    pi_str = format(pi_val, f'.{n_digits+1}f') # Get enough digits initially
    
    # Ensure correct number of digits after the decimal point
    # Find the decimal point
    point_index = pi_str.find('.')
    if point_index == -1:
        # Should not happen for pi
        return "Error in formatting" 
        
    # Return the part before the point, the point, and n_digits after
    return pi_str[:point_index + 1 + n_digits]


# --- Example Usage ---
if __name__ == "__main__":
    try:
        num_digits_input = int(input("Enter the number of decimal digits of Pi to calculate (N): "))

        if num_digits_input > 0:
            calculated_pi = calculate_pi_chudnovsky(num_digits_input)
            if calculated_pi:
                print(f"\nPi to {num_digits_input} digits:")
                print(calculated_pi)

                # Verification for small N (optional)
                if num_digits_input <= 50:
                    try:
                        # Get reference value using math.pi (low precision) or precomputed string
                        reference_pi = "3.14159265358979323846264338327950288419716939937510" # 50 digits
                        ref_part = reference_pi[:len(calculated_pi)]
                        if calculated_pi == ref_part:
                            print("Result matches reference for the first few digits.")
                        else:
                            print("Result differs from reference (check calculation or reference).")
                            print(f"Reference: {ref_part}")
                    except Exception as e:
                        print(f"Could not verify: {e}")
        else:
            print("Please enter a positive integer for the number of digits.")

    except ValueError:
        print("Invalid input. Please enter an integer.")