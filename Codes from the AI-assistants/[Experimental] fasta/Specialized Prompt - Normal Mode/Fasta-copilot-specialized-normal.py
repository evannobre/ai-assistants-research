import sys

# LCG parameters
A = 1664525
C = 1013904223
M = 2**32
state = 42  # seed

def lcg():
    global state
    state = (A * state + C) % M
    return state

# Weighted random choice from a probability table
def random_base(lookup):
    r = lcg() / M
    for base, prob in lookup:
        r -= prob
        if r < 0:
            return base
    return lookup[-1][0]

# Repeats a constant sequence in FASTA format
def fasta_repeat(name, desc, sequence, n):
    print(f">{name} {desc}")
    for i in range(0, n, 60):
        print(sequence[i % len(sequence): (i % len(sequence)) + 60])

# Generates a random sequence based on nucleotide frequencies
def fasta_random(name, desc, lookup, n):
    print(f">{name} {desc}")
    for _ in range(0, n, 60):
        print(''.join(random_base(lookup) for _ in range(60)))

if __name__ == "__main__":
    IUB = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]

    ALU = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    )

    fasta_repeat("ONE", "Homo sapiens alu", ALU, 1000)
    fasta_random("TWO", "IUB ambiguity codes", IUB, 1000)
