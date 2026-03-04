import sys
import bisect
from typing import List, Tuple, Dict

# --- Configuration & Constants ---
IM = 139968
IA = 3877
IC = 29573
SEED = 42

LINE_LENGTH = 60

# --- DNA Data ---
ALU = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTC"
    "AGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCG"
    "TGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGG"
    "AGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

IUB = [
    ("a", 0.27), ("c", 0.12), ("g", 0.12), ("t", 0.27),
    ("B", 0.02), ("D", 0.02), ("H", 0.02), ("K", 0.02),
    ("M", 0.02), ("N", 0.02), ("R", 0.02), ("S", 0.02),
    ("V", 0.02), ("W", 0.02), ("Y", 0.02)
]

HOMOSAPIENS = [
    ("a", 0.3029549426680),
    ("c", 0.1979883004921),
    ("g", 0.1975473066391),
    ("t", 0.3015094502008),
]

# --- Naive Linear Congruential Generator ---
class MyRandom:
    """
    Manages the LCG state.
    We use a class to encapsulate the 'last' seed state cleanly 
    without relying on global variables.
    """
    def __init__(self, seed: int = 42):
        self.last = seed

    def gen(self, max_val: float = 1.0) -> float:
        """
        Calculates the next random number using the specific formula:
        Seed = (Seed * IA + IC) modulo IM
        Result = Max * Seed / IM
        """
        self.last = (self.last * IA + IC) % IM
        return max_val * self.last / IM

# --- Helper Functions ---

def make_cumulative(table: List[Tuple[str, float]]) -> Tuple[List[float], List[int]]:
    """
    Converts probabilities to cumulative probabilities.
    Returns:
        probs: A list of cumulative float probabilities for bisect.
        chars: A list of corresponding byte characters (integers).
    """
    probs = []
    chars = []
    prob_acc = 0.0
    for char, p in table:
        prob_acc += p
        probs.append(prob_acc)
        # Store as byte integer for faster buffer writing later
        chars.append(ord(char))
    return probs, chars

def make_repeat_fasta(header_id: str, header_desc: str, sequence: str, n: int):
    """
    Generates DNA sequences by copying from a given sequence (ALU).
    """
    # Write header
    header = f">{header_id} {header_desc}\n".encode('utf-8')
    sys.stdout.buffer.write(header)

    # Pre-encode sequence to bytes
    seq_bytes = sequence.encode('utf-8')
    seq_len = len(seq_bytes)
    
    # We maintain a pointer in the source sequence
    # to handle line wrapping correctly across the repeating pattern.
    pos = 0
    
    # Efficiently write chunks
    while n > 0:
        line_len = min(n, LINE_LENGTH)
        remain = line_len
        line = bytearray()
        
        while remain > 0:
            # Determine how much we can take from the current position to the end of ALU
            chunk_len = min(remain, seq_len - pos)
            line.extend(seq_bytes[pos : pos + chunk_len])
            
            pos += chunk_len
            remain -= chunk_len
            
            # Reset ALU pointer if we hit the end
            if pos >= seq_len:
                pos = 0
                
        line.append(10) # Append newline (ASCII 10)
        sys.stdout.buffer.write(line)
        n -= line_len

def make_random_fasta(header_id: str, header_desc: str, table: List[Tuple[str, float]], n: int, rng: MyRandom):
    """
    Generates DNA sequences by weighted random selection.
    Uses bisect (Binary Search) for probability lookup.
    """
    # Write header
    header = f">{header_id} {header_desc}\n".encode('utf-8')
    sys.stdout.buffer.write(header)

    # Prepare lookup tables
    probs, chars = make_cumulative(table)
    
    # Buffer for output
    # We construct bytearrays directly for speed
    while n > 0:
        line_len = min(n, LINE_LENGTH)
        line = bytearray()
        
        # Generate 'line_len' characters
        for _ in range(line_len):
            r = rng.gen(1.0)
            
            # NATIVE LIBRARY USAGE: bisect
            # bisect_left finds the first index where probs[i] >= r
            # This is effectively our binary search matching the random number
            # against cumulative probabilities.
            idx = bisect.bisect_left(probs, r)
            
            # Fallback for floating point rounding edge cases (rare but possible)
            if idx >= len(chars):
                idx = len(chars) - 1
                
            line.append(chars[idx])
            
        line.append(10) # Append newline
        sys.stdout.buffer.write(line)
        n -= line_len

# --- Main Execution ---

def main():
    # Default to 1000 if no argument provided, for safety
    n = 1000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass

    # Initialize Random State ONCE
    rng = MyRandom(SEED)

    # 1. Repeat FASTA (ALU) - 2 * N
    make_repeat_fasta('ONE', 'Homo sapiens alu', ALU, n * 2)

    # 2. Random FASTA (IUB) - 3 * N
    make_random_fasta('TWO', 'IUB ambiguity codes', IUB, n * 3, rng)

    # 3. Random FASTA (Homo Sapiens) - 5 * N
    make_random_fasta('THREE', 'Homo sapiens frequency', HOMOSAPIENS, n * 5, rng)

if __name__ == "__main__":
    main()