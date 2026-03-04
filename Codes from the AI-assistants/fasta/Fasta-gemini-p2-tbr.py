import sys
import bisect
from itertools import accumulate, islice, cycle

# --- Constants defined by the FASTA Benchmark ---
IM = 139968
IA = 3877
IC = 29573
SEED = 42

LINE_LENGTH = 60

# Data for the simulation
ALU = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

IUB = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008)
]

def make_cumulative(table):
    """
    Transform frequency table into cumulative probabilities and associated chars.
    Uses native itertools.accumulate for efficient summation.
    """
    chars, probs = zip(*table)
    # cum_probs are scaled by IM to map directly to the LCG output
    cum_probs = list(accumulate(probs, lambda x, y: x + y))
    # Normalize exact float precision issues to align with IM
    cum_probs = [p * IM for p in cum_probs]
    return chars, cum_probs

class LCG:
    """
    Naïve Linear Congruential Generator.
    Maintains state (seed) and provides the next pseudo-random value.
    """
    def __init__(self, seed=SEED):
        self.state = seed

    def gen_random(self, max_val=1.0):
        """Generates the next random number using the FASTA recurrence."""
        self.state = (self.state * IA + IC) % IM
        return max_val * self.state / IM

    def gen_stream(self, n):
        """Yields a stream of 'n' random numbers."""
        for _ in range(n):
            self.state = (self.state * IA + IC) % IM
            yield self.state

def write_fasta(title, sequence_iterator, n):
    """
    Writes a FASTA formatted sequence to stdout.buffer.
    
    Args:
        title (str): The FASTA header.
        sequence_iterator (iterator): A generator yielding bytes/chars.
        n (int): Total number of characters to write.
    """
    # Write Header (encoded to bytes)
    sys.stdout.buffer.write(f">{title}\n".encode('ascii'))
    
    # We slice the infinite iterator to exactly 'n' characters
    limited_iterator = islice(sequence_iterator, n)
    
    while True:
        # Take a chunk of LINE_LENGTH characters
        # join is efficient in Python for building strings/bytes
        chunk = ''.join(islice(limited_iterator, LINE_LENGTH))
        if not chunk:
            break
        sys.stdout.buffer.write(f"{chunk}\n".encode('ascii'))

def make_repeat_fasta(id, desc, s, n):
    """Generates the ALU sequence (repeating)."""
    # cycle() is a native library tool that repeats the sequence infinitely
    write_fasta(f"{id} {desc}", cycle(s), n)

def make_random_fasta(id, desc, table, n, lcg):
    """Generates the Random sequences using LCG and Bisect."""
    chars, cum_probs = make_cumulative(table)
    
    # Pre-binding for performance in the inner loop
    bisect_left = bisect.bisect_left
    
    def random_char_generator():
        # Optimization: We generate the stream of random numbers first
        # then map them to characters using binary search
        for r in lcg.gen_stream(n):
            # bisect_left performs a binary search to find the insertion point
            # which corresponds to the weighted random choice.
            idx = bisect_left(cum_probs, r)
            yield chars[idx]

    write_fasta(f"{id} {desc}", random_char_generator(), n)

if __name__ == "__main__":
    # Default length if not provided
    n = 1000
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    # Shared LCG instance ensures the seed state persists across function calls
    lcg = LCG()

    # 1. ALU (Repeat) - Multiplied by 2 as per benchmark convention usually
    make_repeat_fasta("ONE", "Homo sapiens alu", ALU, n * 2)

    # 2. IUB (Random) - Multiplied by 3
    make_random_fasta("TWO", "IUB ambiguity codes", IUB, n * 3, lcg)

    # 3. Homo Sapiens (Random) - Multiplied by 5
    make_random_fasta("THREE", "Homo sapiens frequency", HOMOSAPIENS, n * 5, lcg)