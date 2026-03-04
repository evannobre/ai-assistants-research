#!/usr/bin/env python3
import sys
from collections import defaultdict

def read_sequence(path: str) -> str:
    seq_parts = []
    with open(path, "r") as f:
        for line in f:
            if not line.startswith(">"):
                seq_parts.append(line.strip().upper())
    return "".join(seq_parts)


def kmer_frequencies(seq: str, k: int) -> dict:
    freq = defaultdict(int)
    limit = len(seq) - k + 1
    for i in range(limit):
        freq[seq[i:i+k]] += 1
    return freq


def print_frequency_table(freq: dict, k: int):
    total = sum(freq.values())
    items = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    for kmer, count in items:
        pct = (count / total) * 100
        print(f"{kmer} {pct:.3f}")


def print_pattern_count(freq: dict, pattern: str):
    print(f"{freq.get(pattern, 0)}\t{pattern}")


def main():
    if len(sys.argv) < 2:
        print("Usage: ./k_nucleotide.py <dna_file>")
        sys.exit(1)

    seq = read_sequence(sys.argv[1])

    # Required k values
    ks = [1, 2, 3, 4, 6, 12, 18]

    # Precompute all frequencies
    freq_map = {k: kmer_frequencies(seq, k) for k in ks}

    # Print frequency tables
    print_frequency_table(freq_map[1], 1)
    print()
    print_frequency_table(freq_map[2], 2)
    print()

    # Specific patterns
    patterns = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    for p in patterns:
        print_pattern_count(freq_map[len(p)], p)


if __name__ == "__main__":
    main()
