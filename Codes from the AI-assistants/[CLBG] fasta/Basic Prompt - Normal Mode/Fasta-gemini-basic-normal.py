import sys

# --- Naive Linear Congruential Generator (LCG) ---
IM = 139968
IA = 3877
IC = 29573
# Seed is initialized globally as per the requirement
# It will be reset for each major section of the simulation if needed,
# or maintained across the entire run based on interpretation.
# For this implementation, we will maintain a single global seed.
current_seed = 42

def reset_seed():
    """Resets the global LCG seed to its initial value."""
    global current_seed
    current_seed = 42

def gen_random(maximum):
    """
    Generates a random number using the Naive LCG arithmetic.
    Updates the global current_seed.
    """
    global current_seed
    current_seed = (current_seed * IA + IC) % IM
    return maximum * current_seed / IM

# --- Helper function for writing sequences ---
def write_sequences(header, sequence, line_length=60):
    """Writes a sequence to stdout with a given header and line length."""
    sys.stdout.write(header + '\n')
    for i in range(0, len(sequence), line_length):
        sys.stdout.write(sequence[i:i+line_length] + '\n')

# --- Weighted Random Selection Logic ---

# Define the alphabets and their probabilities
# These will be converted to cumulative probabilities.

# Alphabet 1
ALU_SEQUENCE = """
GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG
GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA
CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT
ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA
GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG
AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC
AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA
"""

# Alphabet 2 (IUB)
IUB = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

# Alphabet 3 (Homo sapiens)
HOMO_SAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883024875),
    ('g', 0.1979883024875),
    ('t', 0.3010684523570)
]

def build_cumulative_probabilities(alphabet_probabilities):
    """
    Converts a list of (character, probability) tuples into
    a list of (character, cumulative_probability) tuples.
    """
    cumulative = []
    current_cumulative_prob = 0.0
    for char, prob in alphabet_probabilities:
        current_cumulative_prob += prob
        cumulative.append((char, current_cumulative_prob))
    return cumulative

# Pre-calculate cumulative probabilities
CUMULATIVE_IUB = build_cumulative_probabilities(IUB)
CUMULATIVE_HOMO_SAPIENS = build_cumulative_probabilities(HOMO_SAPIENS)

def select_nucleotide(cumulative_probabilities):
    """
    Selects a nucleotide based on a random number and cumulative probabilities.
    Uses linear search (naive lookup).
    """
    rand_num = gen_random(1.0) # Random number between 0.0 and 1.0
    for char, cum_prob in cumulative_probabilities:
        if rand_num < cum_prob:
            return char
    # Fallback in case of floating point issues or rand_num == 1.0 (shouldn't happen with <)
    # Return the last character if no match (implies rand_num >= last cumulative prob)
    return cumulative_probabilities[-1][0]


def fasta_simulation(n):
    """
    Performs the fasta simulation as specified.
    n: The total length of the sequence to generate for random parts.
    """
    # Section 1: Generate DNA sequences by copying from a given sequence
    # Re-use ALU_SEQUENCE by repeating and trimming
    alu_len = len(ALU_SEQUENCE.replace('\n', ''))
    # Ensure total length of this section is 2N
    copy_length = 2 * n
    copied_sequence = (ALU_SEQUENCE.replace('\n', '') * ((copy_length // alu_len) + 1))[:copy_length]
    write_sequences('>ONE Homo sapiens alu', copied_sequence)

    # Section 2: Generate DNA sequences by weighted random selection (IUB)
    # Ensure total length of this section is 3N
    # Reset seed before starting a new random generation block if desired for consistency,
    # or let it flow based on the "don't cache" and "each time" requirement.
    # The problem implies a continuous sequence of random numbers for overall simulation.
    # So we will NOT reset the seed here, but allow it to continue from previous section's state.
    # If a hard reset per section was intended, add reset_seed() here.
    random_iub_length = 3 * n
    iub_sequence = [select_nucleotide(CUMULATIVE_IUB) for _ in range(random_iub_length)]
    write_sequences('>TWO IUB ambiguity codes', "".join(iub_sequence))

    # Section 3: Generate DNA sequences by weighted random selection (Homo sapiens)
    # Ensure total length of this section is 5N
    homo_sapiens_length = 5 * n
    homo_sapiens_sequence = [select_nucleotide(CUMULATIVE_HOMO_SAPIENS) for _ in range(homo_sapiens_length)]
    write_sequences('>THREE Homo sapiens random', "".join(homo_sapiens_sequence))

# --- Main Execution ---
if __name__ == "__main__":
    # Get N from command-line argument, default to a smaller value for testing
    # Use int(sys.argv[1]) for the specified command-line argument.
    # For performance check, the user should provide 25000000.
    N_ARG = 1000 # Default for quick testing
    if len(sys.argv) > 1:
        try:
            N_ARG = int(sys.argv[1])
        except ValueError:
            print("Invalid argument. Please provide an integer for N.")
            sys.exit(1)

    fasta_simulation(N_ARG)