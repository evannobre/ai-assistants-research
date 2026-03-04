import sys

# --- Constants & Data ---

IM = 139968
IA = 3877
IC = 29573

# The 'ALU' sequence for the repeat simulation
ALU = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

# IUB ambiguity codes probabilities
IUB = [
    ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
    ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
    ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
    ('V', 0.02), ('W', 0.02), ('Y', 0.02)
]

# Homo Sapiens base probabilities
HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008)
]

# --- Naïve Linear Congruential Generator ---

class MyRandom:
    """
    Implements the required naive LCG.
    We use a class to maintain the seed state cleanly.
    """
    def __init__(self):
        self.seed = 42

    def gen_random(self, max_val=1.0):
        """
        Calculates the next random number using:
        Seed = (Seed * IA + IC) modulo IM
        Result = Max * Seed / IM
        """
        self.seed = (self.seed * IA + IC) % IM
        return max_val * self.seed / IM

# Initialize global random state
rng = MyRandom()

# --- Helper Functions ---

def make_cumulative(table):
    """
    Converts a list of (char, prob) into (cumulative_prob, char).
    Do not optimize using scaling factors (keep as float).
    """
    cumulative = []
    prob_sum = 0.0
    for char, prob in table:
        prob_sum += prob
        cumulative.append((prob_sum, char))
    return cumulative

def select_nucleotide(cumulative_table):
    """
    Matches a random number against cumulative probabilities using Linear Search.
    """
    r = rng.gen_random(1.0)
    for prob, char in cumulative_table:
        if r < prob:
            return char
    return cumulative_table[-1][1]  # Fallback for floating point rounding

# --- Main Logic ---

def make_repeat_fasta(id, desc, source, n):
    """
    Generates DNA by copying from a given sequence (ALU).
    Uses native string slicing and generator yielding for efficiency.
    """
    # Header
    sys.stdout.write(f">{id} {desc}\n")
    
    source_len = len(source)
    line_length = 60
    
    # We maintain a pointer 'p' inside the source string
    p = 0
    while n > 0:
        # Determine how many characters to print on this line
        chunk = min(n, line_length)
        
        # If the chunk fits within the remaining source string
        if p + chunk <= source_len:
            sys.stdout.write(source[p:p+chunk])
            p += chunk
        else:
            # We need to wrap around the source string
            remainder = source_len - p
            sys.stdout.write(source[p:])
            # Determine how much is left to print after the wrap
            needed = chunk - remainder
            # Print full repeats of source if needed (rare for short lines, but robust)
            while needed > source_len:
                sys.stdout.write(source)
                needed -= source_len
            # Print the start of the source
            sys.stdout.write(source[:needed])
            p = needed
        
        sys.stdout.write("\n")
        
        # If we reached the end of the source, reset pointer
        if p == source_len: 
            p = 0
            
        n -= chunk

def make_random_fasta(id, desc, table, n):
    """
    Generates DNA by weighted random selection.
    """
    # Header
    sys.stdout.write(f">{id} {desc}\n")
    
    # Pre-calculate cumulative probabilities
    cumulative = make_cumulative(table)
    
    line_length = 60
    
    while n > 0:
        chunk = min(n, line_length)
        # Generate 'chunk' characters
        # Using a generator expression joined by empty string is 'native' Pythonic style
        line = ''.join(select_nucleotide(cumulative) for _ in range(chunk))
        
        sys.stdout.write(line + "\n")
        n -= chunk

# --- Entry Point ---

def main():
    # Default to 25,000,000 if not specified
    n = 25000000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass

    # 1. Output the ALU repetition
    make_repeat_fasta('ONE', 'Homo sapiens alu', ALU, n * 2)

    # 2. Output the IUB random sequence
    make_random_fasta('TWO', 'IUB ambiguity codes', IUB, n * 3)

    # 3. Output the Homo Sapiens random sequence
    make_random_fasta('THREE', 'Homo sapiens frequency', HOMOSAPIENS, n * 5)

if __name__ == "__main__":
    main()