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
    """Converts (char, prob) list to (char, cumulative_prob)."""
    current = 0.0
    cumulative = []
    for char, prob in alphabet:
        current += prob
        cumulative.append((char, current))
    return cumulative

def select_random(cumulative):
    """Naïve linear search for nucleotide selection."""
    r = gen_random(1.0)
    for char, prob in cumulative:
        if r < prob:
            return char
    return cumulative[-1][0]

def fasta_repeat(seq, n):
    """Generates DNA by copying from a given sequence."""
    out = sys.stdout.buffer
    seq_len = len(seq)
    # Handle line wrapping at 60 chars
    for i in range(0, n, 60):
        chunk_size = min(60, n - i)
        # Efficient slicing using modulo to handle wrap-around
        line = [seq[(j + i) % seq_len] for j in range(chunk_size)]
        out.write(bytes(line) + b'\n')

def fasta_random(alphabet, n):
    """Generates DNA by weighted random selection."""
    out = sys.stdout.buffer
    cumulative = make_cumulative(alphabet)
    for i in range(0, n, 60):
        chunk_size = min(60, n - i)
        line = bytearray()
        for _ in range(chunk_size):
            line.append(ord(select_random(cumulative)))
        out.write(line + b'\n')

def main():
    # Large command-line argument N
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    alu = (b'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
           b'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
           b'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
           b'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
           b'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
           b'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
           b'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA')

    iub = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]

    homosapiens = [
        ('a', 0.3029549426680), ('c', 0.1979883004921),
        ('g', 0.1975473066391), ('t', 0.3015094502008)
    ]

    print(">ONE Homo sapiens alu")
    fasta_repeat(alu, n * 2)

    print(">TWO IUB ambiguity codes")
    fasta_random(iub, n * 3)

    print(">THREE Homo sapiens frequency")
    fasta_random(homosapiens, n * 5)

if __name__ == "__main__":
    main()