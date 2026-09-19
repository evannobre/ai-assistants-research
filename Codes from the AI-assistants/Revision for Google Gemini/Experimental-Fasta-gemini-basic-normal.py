import sys
from itertools import cycle, accumulate, islice, batched
from bisect import bisect

# 1. LCG Parameters and Generator
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def naive_lcg():
    """Generates a pseudo-random float between 0.0 and 1.0 using LCG."""
    global SEED
    while True:
        SEED = (SEED * IA + IC) % IM
        yield SEED / IM

# 2. Biological Data Constants
ALU_SEQ = (
    b"GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCA"
    b"CCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    b"ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCA"
    b"GGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    b"AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

IUB_PROBS = [
    (b'a', 0.27), (b'c', 0.12), (b'g', 0.12), (b't', 0.27), (b'B', 0.02),
    (b'D', 0.02), (b'H', 0.02), (b'K', 0.02), (b'M', 0.02), (b'N', 0.02),
    (b'R', 0.02), (b'S', 0.02), (b'V', 0.02), (b'W', 0.02), (b'Y', 0.02)
]

HOMO_SAPIENS_PROBS = [
    (b'a', 0.3029549426680), (b'c', 0.1979883004921),
    (b'g', 0.1975473066391), (b't', 0.3015094502008)
]

# 3. Formatting and Sequence Generation
def make_cumulative_distribution(probability_table):
    """Uses native itertools.accumulate to create cumulative probabilities."""
    nucleotides = [nuc for nuc, _ in probability_table]
    probabilities = list(accumulate(prob for _, prob in probability_table))
    return nucleotides, probabilities

def write_repeated_fasta(header, sequence, length):
    """Uses native itertools.cycle and batched to repeat strings infinitely."""
    sys.stdout.buffer.write(b">" + header + b"\n")
    
    # cycle() repeats the Alu sequence natively.
    # islice() limits it to the requested length.
    infinite_seq = cycle(sequence)
    sliced_seq = islice(infinite_seq, length)
    
    # batched() chunks it into 60-character lines cleanly (Python 3.12+)
    for chunk in batched(sliced_seq, 60):
        sys.stdout.buffer.write(bytes(chunk) + b"\n")

def write_random_fasta(header, probability_table, length, rng):
    """Uses native bisect to select nucleotides without pure-Python loops."""
    sys.stdout.buffer.write(b">" + header + b"\n")
    nucleotides, cumulative_probs = make_cumulative_distribution(probability_table)
    
    def generate_random_nucleotides():
        for _ in range(length):
            # bisect uses a highly optimized C-binary search to find the correct
            # nucleotide based on the LCG's float output.
            random_val = next(rng)
            index = bisect(cumulative_probs, random_val)
            yield nucleotides[index]

    for chunk in batched(generate_random_nucleotides(), 60):
        sys.stdout.buffer.write(b"".join(chunk) + b"\n")

# 4. Execution
def main():
    # Read generation size (N) from command line, default to 1000 for testing
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    rng = naive_lcg()
    
    # The benchmark strictly requires generating three specific sequences:
    write_repeated_fasta(b"ONE Homo sapiens alu", ALU_SEQ, n * 2)
    write_random_fasta(b"TWO IUB ambiguity codes", IUB_PROBS, n * 3, rng)
    write_random_fasta(b"THREE Homo sapiens frequency", HOMO_SAPIENS_PROBS, n * 5, rng)

if __name__ == "__main__":
    main()