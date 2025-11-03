IM, IA, IC = 139968, 3877, 29573
seed = 42

def rand(max_val):
    global seed
    seed = (seed * IA + IC) % IM
    return max_val * seed / IM

def build_cumulative_probs(probs):
    cum = []
    total = 0.0
    for ch, prob in probs:
        total += prob
        cum.append((ch, total))
    return cum

def select_base(cum_probs):
    r = rand(1)
    for ch, cum_prob in cum_probs:
        if r < cum_prob:
            return ch
    return cum_probs[-1][0]  # fallback

def repeat_sequence(name, seq, n):
    print(f">{name}")
    s = seq * ((n // len(seq)) + 1)
    for i in range(0, n, 60):
        print(s[i:i+60])

def random_sequence(name, n, cum_probs):
    print(f">{name}")
    line = []
    for i in range(n):
        line.append(select_base(cum_probs))
        if (i + 1) % 60 == 0:
            print("".join(line))
            line = []
    if line:
        print("".join(line))

# Template sequence
alu = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

# Probabilities from IUB and Homo sapiens DNA
iub = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

homo_sapiens = [('a', 0.3029549426680), ('c', 0.1979883004921),
                ('g', 0.1975473066391), ('t', 0.3015094502008)]

import sys

def main():
    n = 25000000  # Default size or from command line
    repeat_sequence("ONE", alu, n)
    random_sequence("TWO", n, build_cumulative_probs(iub))
    random_sequence("THREE", n, build_cumulative_probs(homo_sapiens))

if __name__ == "__main__":
    main()