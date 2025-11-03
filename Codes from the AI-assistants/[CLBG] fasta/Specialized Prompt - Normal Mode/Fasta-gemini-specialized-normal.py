# LCG Parameters
IM = 139968
IA = 3877
IC = 29573
Seed = 42  # Initial seed, will be updated globally

def naive_lcg_random(max_val):
    global Seed
    Seed = (Seed * IA + IC) % IM
    return (max_val * Seed) / IM

def calculate_cumulative_probabilities(alphabet_probabilities):
    cumulative_probs = []
    current_cumulative = 0.0
    for char, prob in alphabet_probabilities:
        current_cumulative += prob
        cumulative_probs.append((char, current_cumulative))
    return cumulative_probs

def select_nucleotide(cumulative_probs, random_num):
    for char, cumulative_prob_threshold in cumulative_probs:
        if random_num < cumulative_prob_threshold:
            return char
    # This case should ideally not be reached if probabilities sum to 1
    return cumulative_probs[-1][0] # Fallback to the last character

def generate_sequence_by_copying(source_sequence, length):
    full_sequence = []
    source_len = len(source_sequence)
    for i in range(length):
        full_sequence.append(source_sequence[i % source_len])
    return "".join(full_sequence)

# Alphabet 1: IUB Ambiguity Codes (Simplified for example)
# Probabilities taken from an example (can be adjusted)
ALU = [
    ('A', 0.27), ('C', 0.27), ('G', 0.27), ('T', 0.19)
]

# Alphabet 2: Homo sapiens alu
IUB = [
    ('a', 0.3029549426680),
    ('c', 0.1979883024875),
    ('g', 0.1979883024875),
    ('t', 0.3010684523570)
]

# Calculate cumulative probabilities once for each alphabet
CUMULATIVE_ALU = calculate_cumulative_probabilities(ALU)
CUMULATIVE_IUB = calculate_cumulative_probabilities(IUB)

def generate_sequence_by_weighted_random(alphabet_type, length):
    target_cumulative_probs = []
    if alphabet_type == "ALU":
        target_cumulative_probs = CUMULATIVE_ALU
    elif alphabet_type == "IUB":
        target_cumulative_probs = CUMULATIVE_IUB
    else:
        raise ValueError("Invalid alphabet type. Use 'ALU' or 'IUB'.")

    generated_sequence = []
    for _ in range(length):
        # Generate a random number between 0 and 1 (or up to the max cumulative probability)
        # Assuming cumulative probabilities sum to 1.0, so max_val = 1.0
        random_num = naive_lcg_random(1.0)
        selected_char = select_nucleotide(target_cumulative_probs, random_num)
        generated_sequence.append(selected_char)
    return "".join(generated_sequence)

def fasta_simulation(N):
    global Seed # Ensure Seed is accessible for LCG

    # 1. Generate DNA sequence by copying
    # Example: Simple sequence
    IM = "GGGCATGACTGACGTACGTACGTACGTAGGGCATGACTGACGTACGTACGTACGTA"
    # Print header
    print(">repeat_sequence")
    # For a large N, we will generate parts of the sequence
    copied_seq = generate_sequence_by_copying(IM, N)
    # Print in 60-character lines
    for i in range(0, len(copied_seq), 60):
        print(copied_seq[i:i+60])

    # Reset seed for the next part of the simulation if necessary
    # (The problem statement doesn't explicitly say to reset the seed,
    # but for distinct random sequences for different parts, it's good practice
    # or ensure the LCG produces a long enough non-repeating sequence.)
    # For this problem, we continue with the current Seed state.


    # 2. Generate DNA sequence by weighted random selection (IUB)
    print(">random_iub")
    iub_seq = generate_sequence_by_weighted_random("IUB", N)
    for i in range(0, len(iub_seq), 60):
        print(iub_seq[i:i+60])

    # 3. Generate DNA sequence by weighted random selection (ALU)
    print(">random_alu")
    alu_seq = generate_sequence_by_weighted_random("ALU", N)
    for i in range(0, len(alu_seq), 60):
        print(alu_seq[i:i+60])

import sys

# --- Naïve Linear Congruential Generator (LCG) ---
IM = 139968
IA = 3877
IC = 29573
Seed = 42  # Initial seed, will be updated globally by LCG

def naive_lcg_random(max_val):
    """
    Generates a random number using the Naïve Linear Congruential Generator.
    Updates the global Seed.
    """
    global Seed
    Seed = (Seed * IA + IC) % IM
    return (max_val * Seed) / IM

# --- Cumulative Probabilities Calculation ---
def calculate_cumulative_probabilities(alphabet_probabilities):
    """
    Converts a list of (character, probability) tuples into
    (character, cumulative_probability) tuples.
    """
    cumulative_probs = []
    current_cumulative = 0.0
    for char, prob in alphabet_probabilities:
        current_cumulative += prob
        cumulative_probs.append((char, current_cumulative))
    return cumulative_probs

# --- Nucleotide Selection by Weighted Random Choice (Linear Search) ---
def select_nucleotide(cumulative_probs, random_num):
    """
    Selects a nucleotide based on a random number and cumulative probabilities
    using a linear search.
    """
    for char, cumulative_prob_threshold in cumulative_probs:
        if random_num < cumulative_prob_threshold:
            return char
    # Fallback in case of floating point inaccuracies or random_num == 1.0
    return cumulative_probs[-1][0]

# --- DNA Alphabet Definitions and Pre-calculated Cumulative Probabilities ---
# Alphabet 1: IUB Ambiguity Codes (example probabilities)
IUB_ALPHABET = [
    ('a', 0.27), ('c', 0.27), ('g', 0.27), ('t', 0.19)
]
# Alphabet 2: Homo sapiens alu (example probabilities)
ALU_ALPHABET = [
    ('a', 0.3029549426680),
    ('c', 0.1979883024875),
    ('g', 0.1979883024875),
    ('t', 0.3010684523570)
]

# Calculate cumulative probabilities once for each alphabet
CUMULATIVE_IUB = calculate_cumulative_probabilities(IUB_ALPHABET)
CUMULATIVE_ALU = calculate_cumulative_probabilities(ALU_ALPHABET)

# --- DNA Sequence Generation Functions ---

def generate_sequence_by_copying(source_sequence, length):
    """
    Generates a DNA sequence by copying and repeating a source sequence.
    """
    full_sequence_parts = []
    source_len = len(source_sequence)
    for i in range(length):
        full_sequence_parts.append(source_sequence[i % source_len])
    return "".join(full_sequence_parts)

def generate_sequence_by_weighted_random(alphabet_type, length):
    """
    Generates a DNA sequence using weighted random selection based on
    the specified alphabet and the LCG.
    """
    target_cumulative_probs = []
    if alphabet_type == "ALU":
        target_cumulative_probs = CUMULATIVE_ALU
    elif alphabet_type == "IUB":
        target_cumulative_probs = CUMULATIVE_IUB
    else:
        raise ValueError("Invalid alphabet type. Use 'ALU' or 'IUB'.")

    generated_sequence_parts = []
    for _ in range(length):
        # Generate a random number between 0 and 1.0 (as cumulative sum is 1.0)
        random_num = naive_lcg_random(1.0)
        selected_char = select_nucleotide(target_cumulative_probs, random_num)
        generated_sequence_parts.append(selected_char)
    return "".join(generated_sequence_parts)

# --- Main FASTA Simulation Function ---
def fasta_simulation(N):
    """
    Performs the FASTA simulation according to the specified requirements.
    """
    # 1. Generate DNA sequence by copying
    # Initial sequence to copy from
    IM_sequence = "GGGCATGACTGACGTACGTACGTACGTAGGGCATGACTGACGTACGTACGTACGTA"
    # Print header
    sys.stdout.write(">repeat_sequence\n")
    copied_seq = generate_sequence_by_copying(IM_sequence, N)
    # Print in 60-character lines
    for i in range(0, len(copied_seq), 60):
        sys.stdout.write(copied_seq[i:i+60] + '\n')

    # 2. Generate DNA sequence by weighted random selection (IUB)
    sys.stdout.write(">random_iub\n")
    iub_seq = generate_sequence_by_weighted_random("IUB", N)
    for i in range(0, len(iub_seq), 60):
        sys.stdout.write(iub_seq[i:i+60] + '\n')

    # 3. Generate DNA sequence by weighted random selection (ALU)
    sys.stdout.write(">random_alu\n")
    alu_seq = generate_sequence_by_weighted_random("ALU", N)
    for i in range(0, len(alu_seq), 60):
        sys.stdout.write(alu_seq[i:i+60] + '\n')

# --- Command Line Execution ---
if __name__ == "__main__":
    # Get N from command-line argument
    if len(sys.argv) < 2:
        print("Usage: python fasta_simulation.py <N>")
        sys.exit(1)
    
    try:
        N = int(sys.argv[1])
        fasta_simulation(N)
    except ValueError:
        print("Error: N must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)