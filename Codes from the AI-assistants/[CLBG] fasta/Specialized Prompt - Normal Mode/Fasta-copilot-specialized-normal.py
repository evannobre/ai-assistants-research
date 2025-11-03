import sys

IM = 139968
IA = 3877
IC = 29573
SEED = 42

# Naïve Linear Congruential Generator
def random_lcg(max_val):
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

def build_cumulative(alphabet):
    cum = []
    total = 0.0
    for char, prob in alphabet:
        total += prob
        cum.append((char, total))
    return cum

# Linear search for match
def select_random(cum):
    r = random_lcg(1.0)
    for char, cp in cum:
        if r < cp:
            return char
    return cum[-1][0]  # fallback

# Write a repeated sequence to output
def repeat_fasta(id, desc, sequence, length):
    print(f">{id} {desc}")
    line_len = 60
    seq_len = len(sequence)
    for i in range(0, length, line_len):
        line = ''.join(sequence[(i + j) % seq_len] for j in range(min(line_len, length - i)))
        print(line)

# Write random DNA with probabilities
def random_fasta(id, desc, alphabet, length):
    print(f">{id} {desc}")
    cum = build_cumulative(alphabet)
    line_len = 60
    for _ in range(0, length, line_len):
        line = ''.join(select_random(cum) for _ in range(min(line_len, length)))
        print(line)

# DNA data
alu = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

# IUB and Homo sapiens DNA weight tables
iub = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

homosapiens = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008)
]

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25000000
    repeat_fasta("ONE", "Homo sapiens alu", alu, n)
    random_fasta("TWO", "IUB ambiguity codes", iub, n * 2)
    random_fasta("THREE", "Homo sapiens frequency", homosapiens, n * 3)
