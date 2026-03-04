import sys

def generate_pi(n_digits):
    """
    Gibbons' Unbounded Spigot Algorithm.
    Generates digits of Pi sequentially.
    """
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3
    count = 0
    
    while count < n_digits:
        if 4 * q + r - t < n * t:
            # Extract(3) and Extract(4) are consistent? Output digit n.
            yield n
            count += 1
            
            # Print formatting: 10 digits per line with running total
            if count % 10 == 0:
                print(f"{n}\t:{count}")
            else:
                print(n, end="")
            
            # Update state for the next digit
            nr = 10 * (r - n * t)
            n = ((10 * (3 * q + r)) // t) - 10 * n
            q *= 10
            r = nr
        else:
            # Produce more terms of the continued fraction
            nr = (2 * q + r) * l
            nn = (q * (7 * k + 2) + r * l) // (t * l)
            q *= k
            t *= l
            l += 2
            k += 1
            n = nn
            r = nr

def main():
    if len(sys.argv) < 2:
        print("Usage: python pi_spigot.py <number_of_digits>")
        return
    
    n_digits = int(sys.argv[1])
    # The generator yields digits; the logic is handled inside for formatting.
    list(generate_pi(n_digits))

if __name__ == "__main__":
    main()