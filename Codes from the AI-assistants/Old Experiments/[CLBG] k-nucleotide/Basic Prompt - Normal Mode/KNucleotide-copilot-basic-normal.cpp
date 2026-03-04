import sys
import re
from collections import Counter

def read_fasta_input():
    data = sys.stdin.read()
    match = re.search(r'>THREE\s+([\w\n]+)', data)
    if not match:
        raise ValueError("DNA sequence THREE not found.")
    sequence = ''.join(match.group(1).split()).upper()
    return sequence

def count_kmers(seq, k):
    counter = Counter()
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i+k]
        counter[kmer] += 1
    return counter

def print_frequencies(counter, total):
    sorted_items = sorted(
        counter.items(),
        key=lambda item: (-item[1], item[0])
    )
    for kmer, count in sorted_items:
        freq = (count / total) * 100
        print(f"{kmer} {freq:.3f}")

def print_specific_kmers(counter, kmers):
    for kmer in kmers:
        print(f"{counter.get(kmer, 0)}\t{kmer}")

def main():
    seq = read_fasta_input()

    # Frequencies for k = 1 and 2
    for k in [1, 2]:
        counter = count_kmers(seq, k)
        total = sum(counter.values())
        print_frequencies(counter, total)
        print()

    # Specific sequences
    for k, kmers in [
        (3, ['GGT']),
        (4, ['GGTA']),
        (6, ['GGTATT']),
        (12, ['GGTATTTTAATT']),
        (18, ['GGTATTTTAATTTATAGT']),
    ]:
        counter = count_kmers(seq, k)
        print_specific_kmers(counter, kmers)

if __name__ == '__main__':
    main()