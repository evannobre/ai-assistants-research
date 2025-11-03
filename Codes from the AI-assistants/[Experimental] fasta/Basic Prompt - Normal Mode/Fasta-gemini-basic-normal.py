import math # Not strictly needed for LCG, but for general utility if more complex math was involved
import sys  # For stdout, if needed for direct printing

# --- 1. Define LCG Parameters ---
# These are example values. For better randomness, choose them carefully.
LCG_MODULUS = 2**31 - 1  # A common large prime (Mersenne prime)
LCG_MULTIPLIER = 1103515245
LCG_INCREMENT = 12345
current_lcg_seed = 42 # Initial seed (can be user-defined or time-based)

# --- 2. Define Base Frequencies (Cumulative) ---
# Example frequencies. Adjust as needed for specific biological context.
# Ensure the last cumulative probability is 1.0
DNA_BASES = [
    ('A', 0.27),  # A: 27%
    ('C', 0.52),  # C: 25% (0.52 - 0.27)
    ('G', 0.75),  # G: 23% (0.75 - 0.52)
    ('T', 1.00)   # T: 25% (1.00 - 0.75)
]

# --- 3. Implement the LCG Function ---
def get_next_lcg_random():
    global current_lcg_seed
    current_lcg_seed = (LCG_MULTIPLIER * current_lcg_seed + LCG_INCREMENT) % LCG_MODULUS
    # Normalize to a range [0, 1) for probability mapping
    return current_lcg_seed / LCG_MODULUS

# --- 4. Implement the Base Selection Function ---
def select_dna_base(random_value):
    for base, cumulative_prob in DNA_BASES:
        if random_value < cumulative_prob:
            return base
    return 'T' # Fallback, should not happen if probabilities are correct

# --- 5. Main Simulation Loop ---
def generate_fasta_sequence(sequence_length, line_wrap_length=60):
    fasta_sequence_chars = []
    
    print(f">Naïve LCG Generated FASTA Sequence, Length: {sequence_length}")

    for i in range(sequence_length):
        random_num = get_next_lcg_random()
        base = select_dna_base(random_num)
        fasta_sequence_chars.append(base)

        # Print in FASTA format (60 chars per line)
        if (i + 1) % line_wrap_length == 0:
            print("".join(fasta_sequence_chars[-line_wrap_length:]))
        elif i == sequence_length - 1: # Print remaining characters on the last line
            print("".join(fasta_sequence_chars[-(i % line_wrap_length + 1):]))

# --- How to use ---
if __name__ == "__main__":
    desired_sequence_length = 1000 # Example: Generate a 1000 base sequence
    generate_fasta_sequence(desired_sequence_length)