import sys
import bisect
from itertools import accumulate

# --- 1. Constants & LCG State ---
IM = 139968
IA = 3877
IC = 29573
LAST = 42

def gen_random(max_val):
    """
    A generator that yields the LCG state normalized.
    Updates the global LAST state.
    """
    global LAST
    while True:
        LAST = (LAST * IA + IC) % IM
        yield (max_val * LAST) / IM

# --- 2. Data Definitions ---
alu = (
   'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
   'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
   'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
   'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
   'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
   'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
   'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
)

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

# --- 3. Native Library Helpers ---

def make_cumulative(table):
    """
    Uses itertools.accumulate to transform [(char, prob)...]
    into separate lists of chars and cumulative probabilities.
    """
    chars, probs = zip(*table)
    # Native library: itertools.accumulate calculates running totals efficiently
    cum_probs = list(accumulate(probs))
    return chars, cum_probs

def repeat_fasta(title, n, sequence):
    """
    Handles the repeating sequence (ALU).
    """
    sys.stdout.write(f">{title}\n")
    seq_len = len(sequence)
    
    # We can calculate the exact output using native string slicing and joining
    # rather than looping char by char.
    full_sequence = sequence * ((n // seq_len) + 1)
    formatted = full_sequence[:n]
    
    # Process in chunks of 60 for FASTA line width
    width = 60
    for i in range(0, n, width):
        sys.stdout.write(formatted[i:i+width] + "\n")

def random_fasta(title, n, table):
    """
    Handles the random sequences using LCG and Bisect.
    """
    sys.stdout.write(f">{title}\n")
    
    # Prepare lookup tables
    chars, cum_probs = make_cumulative(table)
    
    # Create the LCG generator
    # We request random numbers scaled to 1.0
    rng = gen_random(1.0)
    
    width = 60
    
    # We process line by line (chunk by chunk)
    for i in range(0, n, width):
        line_len = min(width, n - i)
        line_buffer = []
        
        # Generate the random numbers for this line
        for _ in range(line_len):
            val = next(rng)
            
            # Native Library: bisect
            # Finds the insertion point in the cumulative probability list
            # which corresponds to the weighted random choice.
            idx = bisect.bisect(cum_probs, val)
            line_buffer.append(chars[idx])
            
        sys.stdout.write("".join(line_buffer) + "\n")

# --- 4. Main Execution ---

def main():
    n = 1000 # Default size, usually passed via command line
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    repeat_fasta('ONE Homo sapiens alu', n * 2, alu)
    random_fasta('TWO IUB ambiguity codes', n * 3, iub)
    random_fasta('THREE Homo sapiens frequency', n * 5, homosapiens)

if __name__ == "__main__":
    main()