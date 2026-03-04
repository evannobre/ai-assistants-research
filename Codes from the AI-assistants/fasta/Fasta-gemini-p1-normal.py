import sys
from itertools import accumulate, islice

# LCG Constants for FASTA
IM = 2147483647
IA = 3847
IC = 453406
LAST_SEED = 42

def gen_random(max_val):
    """Native LCG generator using global state."""
    global LAST_SEED
    while True:
        LAST_SEED = (LAST_SEED * IA + IC) % IM
        yield max_val * LAST_SEED / IM

def make_cumulative(alphabet):
    """Converts probabilities into a cumulative distribution for selection."""
    chars, probs = zip(*alphabet)
    cum_probs = list(accumulate(probs))
    return chars, cum_probs

def fasta_simulation(header, alphabet, n):
    """Generates the FASTA sequence based on weighted probabilities."""
    # Write the FASTA header
    sys.stdout.write(f">{header}\n")
    
    chars, cum_probs = make_cumulative(alphabet)
    random_gen = gen_random(1.0)
    
    # Process in chunks of 60 characters (standard FASTA line length)
    for _ in range(0, n, 60):
        line_len = min(60, n - _)
        line = []
        for _ in range(line_len):
            r = next(random_gen)
            # Find the character using the cumulative probability
            for i, p in enumerate(cum_probs):
                if r < p:
                    line.append(chars[i])
                    break
        sys.stdout.write("".join(line) + "\n")

# Example usage with DNA nucleotides
iub = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

if __name__ == "__main__":
    fasta_simulation("ONE IUB ambiguity codes", iub, 1000)