#!/usr/bin/env python3
import sys
from collections import Counter

def read_dna_sequence(path: str) -> str:
    """Read a DNA file and return a single uppercase sequence string."""
    seq_parts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                # Header line; skip
                continue
            seq_parts.append(line)
    return "".join(seq_parts).upper()

def kmer_counts(seq: str, k: int) -> Counter:
    """Return counts of all k-length substrings in seq using a native Counter."""
    n = len(seq)
    if n < k:
        return Counter()
    # Native hash map via Counter
    counts = Counter(seq[i:i+k] for i in range(n - k + 1))
    return counts

def print_frequency_table(counts: Counter, k: int) -> None:
    """Print k-mer frequencies sorted by descending frequency then lexicographically."""
    total = sum(counts.values())
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    print(f"\n{k}-mer frequency table:")
    for kmer, cnt in items:
        freq = (cnt / total) * 100.0
        print(f"{kmer} {freq:6.3f}")

def print_specific_counts(seq: str, kmers) -> None:
    """Print counts for specific k-mers."""
    if not kmers:
        return
    # Group kmers by length to avoid recomputing everything from scratch per k-mer
    by_k = {}
    for kmer in kmers:
        by_k.setdefault(len(kmer), []).append(kmer)

    for k, group in by_k.items():
        counts = kmer_counts(seq, k)
        for kmer in group:
            print(f"{kmer} {counts.get(kmer, 0)}")

def main(argv):
    if len(argv) < 2:
        print(f"Usage: {argv[0]} <dna_file> [k1 k2 ...]")
        sys.exit(1)

    dna_file = argv[1]
    # Optional ks from command line; default to some typical values
    if len(argv) > 2:
        ks = [int(x) for x in argv[2:]]
    else:
        ks = [1, 2, 3, 4, 6, 12, 18]

    seq = read_dna_sequence(dna_file)

    # Example: print frequency tables for k = 1 and 2
    for k in ks[:2]:
        counts = kmer_counts(seq, k)
        print_frequency_table(counts, k)

    # Example: print counts for some specific k-mers
    # You can change this list to whatever you want to query
    specific_kmers = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    print("\nSpecific k-mer counts:")
    print_specific_counts(seq, specific_kmers)

if __name__ == "__main__":
    main(sys.argv)
