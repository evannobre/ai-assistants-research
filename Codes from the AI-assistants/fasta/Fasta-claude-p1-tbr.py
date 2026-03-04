#!/usr/bin/env python3
"""
FASTA sequence generation using Linear Congruential Generator (LCG)
Based on the Computer Language Benchmarks Game FASTA benchmark
"""

import sys
from typing import List, Tuple

# LCG constants (from the benchmark specification)
IM = 139968
IA = 3877
IC = 29573
LAST = 42

# Line width for output
LINE_LENGTH = 60

class LCG:
    """Linear Congruential Generator for pseudo-random number generation"""
    
    def __init__(self, seed: int = LAST):
        self.last = seed
    
    def gen_random(self, max_val: float = 1.0) -> float:
        """Generate next random number in range [0, max_val)"""
        self.last = (self.last * IA + IC) % IM
        return max_val * self.last / IM


def make_cumulative(genelist: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """Convert probability list to cumulative probability distribution"""
    cumulative = []
    cp = 0.0
    for char, prob in genelist:
        cp += prob
        cumulative.append((char, cp))
    return cumulative


def select_random(cumulative: List[Tuple[str, float]], r: float) -> str:
    """Binary search to select character based on random value"""
    lo, hi = 0, len(cumulative) - 1
    
    while hi > lo + 1:
        mid = (hi + lo) // 2
        if r < cumulative[mid][1]:
            hi = mid
        else:
            lo = mid
    
    return cumulative[hi][0]


def make_repeat_fasta(desc: str, src: str, n: int):
    """Generate repeated FASTA sequence"""
    print(f'>{desc}')
    src_len = len(src)
    s = src * ((n // src_len) + 1)
    
    for i in range(0, n, LINE_LENGTH):
        line_end = min(i + LINE_LENGTH, n)
        print(s[i:line_end])


def make_random_fasta(desc: str, genelist: List[Tuple[str, float]], n: int):
    """Generate random FASTA sequence using LCG"""
    print(f'>{desc}')
    
    cumulative = make_cumulative(genelist)
    lcg = LCG()
    
    # Generate in chunks for efficiency
    chars = []
    for i in range(n):
        r = lcg.gen_random(1.0)
        chars.append(select_random(cumulative, r))
        
        if len(chars) == LINE_LENGTH or i == n - 1:
            print(''.join(chars))
            chars = []


def main():
    """Main FASTA simulation"""
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    # IUB ambiguity codes
    iub = [
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
    
    # Homo sapiens frequency
    homosapiens = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008),
    ]
    
    # ALU repeating sequence
    alu = (
        'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
        'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
        'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
        'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
        'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
        'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
        'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
    )
    
    # Generate sequences
    make_repeat_fasta('ONE Homo sapiens alu', alu, n * 2)
    make_random_fasta('TWO IUB ambiguity codes', iub, n * 3)
    make_random_fasta('THREE Homo sapiens frequency', homosapiens, n * 5)


if __name__ == '__main__':
    main()
