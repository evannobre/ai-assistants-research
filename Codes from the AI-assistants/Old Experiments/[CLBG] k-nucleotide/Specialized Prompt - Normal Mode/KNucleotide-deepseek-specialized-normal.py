import sys
import re
from collections import Counter
from typing import Dict, List, Tuple

def read_fasta() -> str:
    """Read FASTA format from stdin and return the DNA sequence THREE"""
    data = sys.stdin.read()
    # Extract sequence THREE (the last sequence in the file)
    parts = re.split(r'>.*\n', data)
    three = ''.join(parts[-1].split())
    return three.upper()

def count_knucleotides(seq: str, k: int) -> Counter:
    """Count all k-nucleotides in all reading frames"""
    counts = Counter()
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i+k]
        counts[kmer] += 1
    return counts

def print_frequencies(counts: Counter, k: int):
    """Print frequencies sorted by descending count and ascending k-mer"""
    total = sum(counts.values())
    for kmer, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        percent = (count / total) * 100
        print(f"{kmer} {percent:.3f}")

def main():
    dna = read_fasta()
    
    # Count and print 1-nucleotide frequencies
    print("\n1-nucleotide frequencies:")
    counts_1 = count_knucleotides(dna, 1)
    print_frequencies(counts_1, 1)
    
    # Count and print 2-nucleotide frequencies
    print("\n2-nucleotide frequencies:")
    counts_2 = count_knucleotides(dna, 2)
    print_frequencies(counts_2, 2)
    
    # Specific nucleotide sequences to count
    targets = {
        3: ['GGT'],
        4: ['GGTA'],
        6: ['GGTATT'],
        12: ['GGTATTTTAATT'],
        18: ['GGTATTTTAATTTATAGT']
    }
    
    # Count and print specific sequences
    print("\nSpecific sequence counts:")
    for k, kmers in targets.items():
        counts = count_knucleotides(dna, k)
        for kmer in kmers:
            print(f"{counts.get(kmer, 0)}\t{kmer}")

if __name__ == "__main__":
    main()