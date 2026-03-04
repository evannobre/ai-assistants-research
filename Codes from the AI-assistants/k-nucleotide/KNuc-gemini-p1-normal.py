import sys
from collections import Counter

def get_frequencies(sequence, length):
    """Counts occurrences of sub-sequences of a specific length."""
    # This sliding window uses native slicing and the built-in hash map (Counter)
    counts = Counter(sequence[i:i+length] for i in range(len(sequence) - length + 1))
    return counts

def print_sorted_freq(sequence, length):
    """Sorts and prints frequencies for a given length."""
    counts = get_frequencies(sequence, length)
    total = sum(counts.values())
    
    # Sort by value (descending), then by key (alphabetical)
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    for kmer, count in sorted_counts:
        percentage = (count * 100) / total
        print(f"{kmer} {percentage:.3f}")
    print()

def print_specific_count(sequence, kmer):
    """Finds the count for a specific k-mer string."""
    counts = get_frequencies(sequence, len(kmer))
    print(f"{counts.get(kmer, 0)}\t{kmer}")

def main():
    # Read from stdin (native way to handle large DNA files)
    lines = sys.stdin
    for line in lines:
        if line.startswith(">THREE"):
            break
            
    # Join the sequence lines and convert to uppercase
    dna_seq = "".join(line.strip() for line in lines).upper()

    # 1. Print sorted frequencies for 1-nucleotide and 2-nucleotide
    print_sorted_freq(dna_seq, 1)
    print_sorted_freq(dna_seq, 2)

    # 2. Print specific counts for requested sequences
    for s in ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]:
        print_specific_count(dna_seq, s)

if __name__ == "__main__":
    main()