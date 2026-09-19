#!/usr/bin/env python3
"""
FASTA sequence generator using Naïve LCG arithmetic.
Optimized for streaming I/O to maintain O(1) memory complexity.
Targets Ubuntu 24.04 LTS / Python 3.12+ constraints.
"""
import sys
import bisect
import argparse

# --- LCG CONSTANTS ---
IM = 139968
IA = 3877
IC = 29573
SEED = 42
LINE_LENGTH = 60

def make_cumulative(distribution):
    """
    Transforms individual probabilities into cumulative thresholds 
    and maps them to a bytearray for native C-backed binary searching.
    """
    cumulative = []
    chars = bytearray()
    total = 0.0
    for prob, char in distribution:
        total += prob
        cumulative.append(total)
        chars.extend(char)
    return cumulative, chars

def repeat_fasta(header, n, sequence):
    """
    Streams a repeated sequence with O(1) memory footprint.
    By pre-multiplying the sequence buffer, we avoid bounds-checking 
    logic inside the generation loop.
    """
    sys.stdout.buffer.write(header + b'\n')
    seq_len = len(sequence)
    
    # Pre-extend sequence to cover at least LINE_LENGTH plus the cycle
    extended_seq = sequence * ((LINE_LENGTH // seq_len) + 2)
    
    pos = 0
    full_lines = n // LINE_LENGTH
    
    # Write chunks line by line directly to the system buffer
    for _ in range(full_lines):
        sys.stdout.buffer.write(extended_seq[pos:pos+LINE_LENGTH] + b'\n')
        pos = (pos + LINE_LENGTH) % seq_len
        
    rem = n % LINE_LENGTH
    if rem > 0:
        sys.stdout.buffer.write(extended_seq[pos:pos+rem] + b'\n')

def random_fasta(header, n, distribution, current_seed):
    """
    Streams a randomized sequence using naïve LCG arithmetic.
    State is managed locally for performance and returned for next iteration.
    """
    sys.stdout.buffer.write(header + b'\n')
    cumulative, chars = make_cumulative(distribution)
    
    # Mapping globals to local scope circumvents Python's lookup overhead
    local_ia = IA
    local_ic = IC
    local_im = IM
    local_seed = current_seed
    
    # Reusable buffer to prevent memory reallocation
    buf = bytearray(LINE_LENGTH + 1)
    buf[-1] = 10  # ASCII value for newline (\n)
    
    full_lines = n // LINE_LENGTH
    for _ in range(full_lines):
        for i in range(LINE_LENGTH):
            # Naïve Linear Congruential Generator arithmetic
            local_seed = (local_seed * local_ia + local_ic) % local_im
            r = local_seed / local_im
            
            # Offloading the search to Python's C-compiled bisect library
            idx = bisect.bisect(cumulative, r)
            buf[i] = chars[idx]
            
        sys.stdout.buffer.write(buf)
        
    # Handle the remaining nucleotides if N isn't perfectly divisible by 60
    rem = n % LINE_LENGTH
    if rem > 0:
        for i in range(rem):
            local_seed = (local_seed * local_ia + local_ic) % local_im
            r = local_seed / local_im
            idx = bisect.bisect(cumulative, r)
            buf[i] = chars[idx]
            
        buf[rem] = 10
        sys.stdout.buffer.write(buf[:rem+1])
        
    return local_seed

def main():
    parser = argparse.ArgumentParser(description="FASTA Benchmark Generator")
    parser.add_argument("n", type=int, help="Number of nucleotides to generate")
    args = parser.parse_args()
    n = args.n

    # 1. Homo sapiens alu (Length: n * 2)
    alu_seq = (
        b"GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        b"GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        b"CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        b"ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        b"GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        b"AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        b"AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    repeat_fasta(b">ONE Homo sapiens alu", n * 2, alu_seq)

    # 2. IUB ambiguity codes (Length: n * 3)
    iub_dist = [
        (0.27, b'a'), (0.12, b'c'), (0.12, b'g'), (0.27, b't'),
        (0.02, b'B'), (0.02, b'D'), (0.02, b'H'), (0.02, b'K'),
        (0.02, b'M'), (0.02, b'N'), (0.02, b'R'), (0.02, b'S'),
        (0.02, b'V'), (0.02, b'W'), (0.02, b'Y')
    ]
    seed_after_iub = random_fasta(b">TWO IUB ambiguity codes", n * 3, iub_dist, SEED)

    # 3. Homo sapiens frequency (Length: n * 5)
    homo_sapiens_dist = [
        (0.3029549426680, b'a'),
        (0.1979883004921, b'c'),
        (0.1975473066391, b'g'),
        (0.3015094502008, b't')
    ]
    random_fasta(b">THREE Homo sapiens frequency", n * 5, homo_sapiens_dist, seed_after_iub)

if __name__ == "__main__":
    main()