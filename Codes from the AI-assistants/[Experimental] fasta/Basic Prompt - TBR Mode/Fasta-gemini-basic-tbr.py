def naive_lcg_fasta_simulator(seed, a, c, m, alphabet, length, header, output_file):
    """
    Generates a biological sequence using a naive LCG and saves it in FASTA format.

    Args:
        seed (int): The initial seed for the LCG.
        a (int): The multiplier for the LCG.
        c (int): The increment for the LCG.
        m (int): The modulus for the LCG.
        alphabet (str): The set of characters for the sequence (e.g., "ACGT").
        length (int): The desired length of the sequence.
        header (str): The FASTA header.
        output_file (str): The name of the output file.
    """
    sequence = []
    current_x = seed
    alphabet_len = len(alphabet)

    # 1. Generate the sequence
    for _ in range(length):
        current_x = (a * current_x + c) % m
        index = current_x % alphabet_len
        sequence.append(alphabet[index])

    # 2. Format and write to FASTA file
    with open(output_file, 'w') as f:
        f.write(header + '\n')
        
        # Write sequence with line wrapping
        line_width = 80
        for i in range(0, len(sequence), line_width):
            f.write("".join(sequence[i:i+line_width]) + '\n')

# --- Example Usage ---
# LCG parameters (example values)
SEED = 42
MULTIPLIER = 1664525
INCREMENT = 1013904223
MODULUS = 2**32

# Simulation parameters
DNA_ALPHABET = "ACGT"
SEQUENCE_LENGTH = 1000
FASTA_HEADER = ">sim_dna_seq_lcg"
OUTPUT_FILENAME = "simulated_sequence.fasta"

# Run the simulation
naive_lcg_fasta_simulator(
    SEED,
    MULTIPLIER,
    INCREMENT,
    MODULUS,
    DNA_ALPHABET,
    SEQUENCE_LENGTH,
    FASTA_HEADER,
    OUTPUT_FILENAME
)

print(f"FASTA sequence successfully generated and saved to {OUTPUT_FILENAME}")