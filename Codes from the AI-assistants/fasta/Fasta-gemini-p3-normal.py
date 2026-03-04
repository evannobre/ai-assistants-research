import sys

# LCG Constants
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def gen_random(max_val):
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

def make_cumulative(alphabet):
    """Converts (char, probability) tuples into (char, cumulative_prob)."""
    cumulative = []
    current_p = 0.0
    for char, p in alphabet:
        current_p += p
        cumulative.append((char, current_p))
    return cumulative

def select_random(cumulative_alphabet):
    """Naive linear search to match random number against cumulative probabilities."""
    r = gen_random(1.0)
    for char, p in cumulative_alphabet:
        if r < p:
            return char
    return cumulative_alphabet[-1][0]

def fasta_generate(n, cumulative_alphabet, line_length=60):
    """Generates DNA via weighted random selection."""
    for i in range(1, n + 1):
        sys.stdout.write(select_random(cumulative_alphabet))
        if i % line_length == 0:
            sys.stdout.write('\n')
    if n % line_length != 0:
        sys.stdout.write('\n')

def fasta_repeat(n, sequence, line_length=60):
    """Generates DNA by cycling through a given sequence."""
    seq_len = len(sequence)
    for i in range(1, n + 1):
        sys.stdout.write(sequence[(i - 1) % seq_len])
        if i % line_length == 0:
            sys.stdout.write('\n')
    if n % line_length != 0:
        sys.stdout.write('\n')

# --- Data Definitions ---

IUB = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

HOMO_SAPIENS = [
    ('a', 0.3029549426680), ('c', 0.1979883004921),
    ('g', 0.1975473066391), ('t', 0.3015094502008)
]

ALU = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

def main():
    # Use 25,000,000 for the final performance check
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    print(">ONE Homo sapiens alu")
    fasta_repeat(n * 2, ALU)

    print(">TWO IUB ambiguity codes")
    fasta_generate(n * 3, make_cumulative(IUB))

    print(">THREE Homo sapiens frequency")
    fasta_generate(n * 5, make_cumulative(HOMO_SAPIENS))

if __name__ == "__main__":
    main()