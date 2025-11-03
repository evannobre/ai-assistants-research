import sys
from collections import Counter
import re

def read_fasta():
    data = sys.stdin.read()
    # Extract sequence THREE (assuming it's the third sequence in the FASTA)
    parts = re.split(r'>.*\n', data)[1:]  # Skip first split part (before first '>')
    if len(parts) < 3:
        raise ValueError("FASTA file does not contain three sequences")
    sequence = parts[2].replace('\n', '')  # Remove newlines
    return sequence.upper()  # Ensure uppercase

def count_knucleotides(sequence, k):
    counts = Counter()
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
    return counts

def print_frequencies(counts, k):
    total = sum(counts.values())
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    for kmer, count in sorted_items:
        print(f"{kmer} {count/total * 100:.3f}%")

def print_specific_counts(counts, specific_sequences):
    for seq in specific_sequences:
        print(f"{counts.get(seq, 0)}\t{seq}")

def main():
    sequence = read_fasta()
    
    # Count and print 1-nucleotide and 2-nucleotide frequencies
    for k in [1, 2]:
        counts = count_knucleotides(sequence, k)
        print_frequencies(counts, k)
        print()  # Blank line between sections
    
    # Count and print specific sequences for k=3,4,6,12,18
    specific_sequences = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
    for k in [3, 4, 6, 12, 18]:
        counts = count_knucleotides(sequence, k)
        # Filter to only the specific sequences of length k
        filtered_seqs = [seq for seq in specific_sequences if len(seq) == k]
        print_specific_counts(counts, filtered_seqs)

if __name__ == "__main__":
    main()