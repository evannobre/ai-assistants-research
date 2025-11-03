# The Computer Language Benchmarks Game
# https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
#
# Contributed by Tupteq
# Corrected by Alec Thomas
# 2to3'd by Daniel Nanz
# Made parallel by The Anh Tran
# Converted to a sequential algorithm by Isaac Gouy
# Adapted by Google Gemini to meet specific user constraints.

import sys

# --- Naive Linear Congruential Generator (LCG) State and Function ---

IM = 139968
IA = 3877
IC = 29573
LAST_SEED = 42

def gen_random(max_val: float) -> float:
    """
    Generates a pseudo-random number using the specified LCG constants.
    The global seed is updated in place.
    """
    global LAST_SEED
    LAST_SEED = (LAST_SEED * IA + IC) % IM
    return max_val * LAST_SEED / IM

# --- Alphabets and Sequences ---

ALU = (
    'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGA'
    'TCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACT'
    'AAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAG'
    'GCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCG'
    'CCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
)

IUB = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02),
]

HOMO_SAPIENS = [
    ('a', 0.3029549426680), ('c', 0.1979883004921),
    ('g', 0.1975473066391), ('t', 0.3015094502008),
]

# --- Core Algorithm Functions ---

def make_cumulative(alphabet: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """
    Converts probabilities to cumulative probabilities.
    """
    cumulative_prob = 0.0
    cumulative_alphabet = []
    for nucleotide, prob in alphabet:
        cumulative_prob += prob
        cumulative_alphabet.append((nucleotide, cumulative_prob))
    # The last probability should be ~1.0, set it exactly to 1.0 to avoid
    # floating point inaccuracies on the final check.
    cumulative_alphabet[-1] = (cumulative_alphabet[-1][0], 1.0)
    return cumulative_alphabet

def select_random_nucleotide(cum_probs: list[tuple[str, float]]) -> str:
    """
    Selects a nucleotide by generating a random number and performing a
    naive linear search on the cumulative probability list.
    """
    # Generate one random number for each selection.
    r = gen_random(1.0)

    # Linear search (no optimization as requested).
    for nucleotide, cum_prob in cum_probs:
        if r < cum_prob:
            return nucleotide
    return cum_probs[-1][0] # Should not be reached in practice with r < 1.0

def make_repeating_fasta(header: str, sequence: str, n: int):
    """
    Generates and prints a sequence by repeating a given template.
    Output is written line by line to stdout to conserve memory.
    """
    sys.stdout.write(header + '\n')
    seq_len = len(sequence)
    line_len = 60
    
    # Generate whole lines
    for i in range(n // line_len):
        start = (i * line_len) % seq_len
        end = start + line_len
        if end <= seq_len:
            sys.stdout.write(sequence[start:end] + '\n')
        else:
            sys.stdout.write(sequence[start:] + sequence[:end % seq_len] + '\n')

    # Generate the remaining part of the last line
    remaining = n % line_len
    if remaining > 0:
        start = (n - remaining) % seq_len
        end = start + remaining
        if end <= seq_len:
            sys.stdout.write(sequence[start:end] + '\n')
        else:
            sys.stdout.write(sequence[start:] + sequence[:end % seq_len] + '\n')


def make_random_fasta(header: str, cum_probs: list[tuple[str, float]], n: int):
    """
    Generates and prints a random sequence based on weighted probabilities.
    Output is written line by line to stdout to conserve memory.
    """
    sys.stdout.write(header + '\n')
    line_len = 60
    
    for i in range(n // line_len):
        line = [select_random_nucleotide(cum_probs) for _ in range(line_len)]
        sys.stdout.write("".join(line) + '\n')

    remaining = n % line_len
    if remaining > 0:
        line = [select_random_nucleotide(cum_probs) for _ in range(remaining)]
        sys.stdout.write("".join(line) + '\n')

# --- Main Execution ---

def main():
    """
    Main function to run the Fasta simulation.
    """
    try:
        n = int(sys.argv[1])
    except (IndexError, ValueError):
        n = 1000 # Default value for small tests

    # 1. Prepare cumulative probability distributions
    iub_cum_probs = make_cumulative(IUB)
    homo_sapiens_cum_probs = make_cumulative(HOMO_SAPIENS)

    # 2. Generate and print sequences as per the Fasta benchmark standard
    make_repeating_fasta('>ONE Homo sapiens alu', ALU, n * 2)
    make_random_fasta('>TWO IUB ambiguity codes', iub_cum_probs, n * 3)
    make_random_fasta('>THREE Homo sapiens frequency', homo_sapiens_cum_probs, n * 5)


if __name__ == "__main__":
    main()