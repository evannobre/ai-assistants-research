import sys

# --- Naive Linear Congruential Generator ---
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def make_random_generator(seed):
    """Factory to create the LCG state"""
    state = {'seed': seed}
    def random_gen(max_val):
        state['seed'] = (state['seed'] * IA + IC) % IM
        return max_val * state['seed'] / IM
    return random_gen

# --- Fasta Generation Logic ---

def make_cumulative(probs):
    """Creates cumulative probabilities from a dictionary of probabilities."""
    cumulative = []
    p = 0.0
    for char, prob in probs.items():
        p += prob
        cumulative.append((p, char))
    return cumulative

def select_random(cumulative_probs, random_func):
    """Selects a random character based on cumulative probabilities using linear search."""
    r = random_func(1.0)
    for p, char in cumulative_probs:
        if r < p:
            return char
    return cumulative_probs[-1][1]

def generate_random_fasta(header, length, cumulative_probs, random_func):
    """Generates and prints a FASTA sequence from weighted random selection."""
    sys.stdout.write(f">{header}\n")
    line_length = 60
    sequence = [select_random(cumulative_probs, random_func) for _ in range(length)]
    for i in range(0, length, line_length):
        sys.stdout.write("".join(sequence[i:i+line_length]) + "\n")

def generate_repeating_fasta(header, length, sequence):
    """Generates and prints a FASTA sequence by repeating a given sequence."""
    sys.stdout.write(f">{header}\n")
    line_length = 60
    seq_len = len(sequence)
    extended_seq = sequence * (line_length // seq_len + 1)
    for i in range(0, length, line_length):
        sys.stdout.write(extended_seq[:min(line_length, length - i)] + "\n")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25000000

    # --- Alphabets and Probabilities ---
    iub_probs = {
        'a': 0.27, 'c': 0.12, 'g': 0.12, 't': 0.27,
        'B': 0.02, 'D': 0.02, 'H': 0.02, 'K': 0.02,
        'M': 0.02, 'N': 0.02, 'R': 0.02, 'S': 0.02,
        'V': 0.02, 'W': 0.02, 'Y': 0.02,
    }

    homosapiens_probs = {
        'a': 0.3029549426680, 'c': 0.1979883004921,
        'g': 0.1975473066391, 't': 0.3015094502008,
    }

    # --- Generate Cumulative Probabilities ---
    iub_cumulative = make_cumulative(iub_probs)
    homosapiens_cumulative = make_cumulative(homosapiens_probs)

    # --- Initialize Random Generator ---
    random_gen = make_random_generator(SEED)

    # --- Generate and Print Sequences ---
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGA"
        "TCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACT"
        "AAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAG"
        "GCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCG"
        "CCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    generate_repeating_fasta("ONE Homo sapiens alu", n * 2, alu)
    generate_random_fasta("TWO IUB ambiguity codes", n * 3, iub_cumulative, random_gen)
    generate_random_fasta("THREE Homo sapiens frequency", n * 5, homosapiens_cumulative, random_gen)