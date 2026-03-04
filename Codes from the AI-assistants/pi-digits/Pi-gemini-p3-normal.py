import sys

def generate_pi(n):
    # Initial state: q/t represents the transformation matrix
    q, r, t, k, n_digits = 1, 0, 1, 1, 0
    
    while n_digits < n:
        # Check if 3 and 4 produce the same digit when transformed
        # Extract(3) and Extract(4)
        if 4 * q + r - t < 3 * q + r:
            # We found a digit!
            digit = (3 * q + r) // t
            n_digits += 1
            
            # Print logic: 10 per line with running total
            print(digit, end="")
            if n_digits % 10 == 0:
                print(f"\t:{n_digits}")
            elif n_digits == n:
                # Handle alignment for the final line if not multiple of 10
                print(" " * (10 - (n_digits % 10)), end="")
                print(f"\t:{n_digits}")

            # Produce: Update state by composing with the inverse of the digit matrix
            # This "extracts" the digit from our current transformation
            old_q = q
            q = 10 * q
            r = 10 * (r - digit * t)
        else:
            # Ingest: We need more precision, so compose with the next term of 
            # the continued fraction for pi: (k, 4k+2, 0, 2k+1)
            q *= k
            r = (2 * k + 1) * (q * 4 + r) # This incorporates the step-by-step math
            r = (2 * q * k + (4 * k + 2) * q + (2 * k + 1) * r) # Re-calculating for r
            
            # Correct sequential step for r and t based on the spigot formula:
            r = (2 * k + 1) * (r + 2 * q)
            t *= (2 * k + 1)
            q *= k
            k += 1

# Refined inner loop for exact Spigot (Gibbons) logic:
def spigot_pi(n):
    q, r, t, k, i, n_digits = 1, 0, 1, 1, 3, 0
    while n_digits < n:
        if 4 * q + r - t < 3 * q + r:
            # Extracting the digit
            d = (3 * q + r) // t
            n_digits += 1
            print(str(d), end="")
            if n_digits % 10 == 0: print(f"\t:{n_digits}")
            
            # Update state (Extract)
            r = 10 * (r - d * t)
            q *= 10
        else:
            # Update state (Ingest)
            r = (2 * q * (4 * k + 2) + r * (2 * k + 1))
            t *= (2 * k + 1)
            q *= k
            k += 1

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    spigot_pi(n)