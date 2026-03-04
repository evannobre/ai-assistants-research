#!/usr/bin/env python3
"""
FASTA sequence generation using Linear Congruential Generator
Optimized for memory efficiency and performance on 8GB RAM system
"""

import sys
from array import array
from itertools import accumulate

# LCG constants (from benchmark specifications)
IM = 139968
IA = 3877
IC = 29573
SEED = 42

# Line width for FASTA format
LINE_WIDTH = 60

# IUB ambiguity codes with probabilities
IUB = [
    ('a', 0.27),
    ('c', 0.12),
    ('g', 0.12),
    ('t', 0.27),
    ('B', 0.02),
    ('D', 0.02),
    ('H', 0.02),
    ('K', 0.02),
    ('M', 0.02),
    ('N', 0.02),
    ('R', 0.02),
    ('S', 0.02),
    ('V', 0.02),
    ('W', 0.02),
    ('Y', 0.02),
]

# Homo sapiens frequency distribution
HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]


class LCG:
    """Linear Congruential Generator for pseudo-random number generation"""
    
    def __init__(self, seed=SEED):
        self.last = seed
    
    def next(self):
        """Generate next random number in range [0, 1)"""
        self.last = (self.last * IA + IC) % IM
        return self.last / IM


def make_cumulative(table):
    """Convert probability table to cumulative distribution"""
    chars = array('u', (item[0] for item in table))
    probs = list(accumulate(item[1] for item in table))
    return chars, probs


def select_random(cumulative_probs, chars, random_value):
    """Binary search to find character based on random value"""
    probs = cumulative_probs
    lo, hi = 0, len(probs)
    
    while hi > lo:
        mid = (lo + hi) // 2
        if random_value < probs[mid]:
            hi = mid
        else:
            lo = mid + 1
    
    return chars[lo]


def repeat_fasta(header, seq, n):
    """Generate repeating sequence"""
    print(f'>{header}')
    
    seq_len = len(seq)
    seq_bytes = seq.encode('ascii')
    k = 0
    
    # Process in chunks to avoid excessive memory usage
    chunk_size = LINE_WIDTH * 1000  # 1000 lines at a time
    
    while n > 0:
        chunk = min(chunk_size, n)
        lines = []
        
        for _ in range((chunk + LINE_WIDTH - 1) // LINE_WIDTH):
            if n <= 0:
                break
                
            line_len = min(LINE_WIDTH, n)
            line = bytearray(line_len)
            
            for i in range(line_len):
                line[i] = seq_bytes[k]
                k = (k + 1) % seq_len
            
            lines.append(line.decode('ascii'))
            n -= line_len
        
        sys.stdout.write('\n'.join(lines) + '\n')


def random_fasta(header, table, n, lcg):
    """Generate random sequence based on probability distribution"""
    print(f'>{header}')
    
    chars, probs = make_cumulative(table)
    
    # Generate in chunks for memory efficiency
    chunk_size = LINE_WIDTH * 1000  # 1000 lines at a time
    
    while n > 0:
        chunk = min(chunk_size, n)
        lines = []
        
        for _ in range((chunk + LINE_WIDTH - 1) // LINE_WIDTH):
            if n <= 0:
                break
            
            line_len = min(LINE_WIDTH, n)
            line = array('u', (
                select_random(probs, chars, lcg.next())
                for _ in range(line_len)
            ))
            
            lines.append(line.tounicode())
            n -= line_len
        
        sys.stdout.write('\n'.join(lines) + '\n')


def main():
    """Main execution function"""
    # Default value for benchmarking
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    # ALU sequence (repeating)
    alu = (
        'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
        'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
        'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
        'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
        'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
        'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
        'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
    )
    
    # Initialize LCG
    lcg = LCG()
    
    # Generate sequences
    repeat_fasta('ONE Homo sapiens alu', alu, n * 2)
    random_fasta('TWO IUB ambiguity codes', IUB, n * 3, lcg)
    random_fasta('THREE Homo sapiens frequency', HOMOSAPIENS, n * 5, lcg)


if __name__ == '__main__':
    main()
