import sys
from collections import Counter

def get_sequence():
    """Extracts sequence THREE from the FASTA file in stdin."""
    found = False
    lines = []
    for line in sys.stdin:
        if line.startswith(">THREE"):
            found = True
            continue
        if found:
            if line.startswith(">"):
                break
            lines.append(line.strip().upper())
    return "".join(lines)

def count_nucleotides(sequence, length):
    """Updates a hash table (Counter) with k-nucleotide frequencies."""
    counts = Counter()
    for i in range(len(sequence) - length + 1):
        k_nucleotide = sequence[i:i + length]
        counts[k_nucleotide] += 1
    return counts

def print_frequencies(counts):
    """Sorts and prints percentage frequency for 1 and 2-nucleotide sequences."""
    total = sum(counts.values())
    # Sort by descending count, then ascending key
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    for key, count in sorted_counts:
        percentage = (count * 100) / total
        print(f"{key} {percentage:.3f}")
    print()

def print_count(counts, sequence_to_find):
    """Prints the raw count for a specific k-nucleotide sequence."""
    print(f"{counts.get(sequence_to_find, 0)}\t{sequence_to_find}")

def main():
    dna_seq = get_sequence()
    
    # 1. Frequency for 1-nucleotide and 2-nucleotide
    print_frequencies(count_nucleotides(dna_seq, 1))
    print_frequencies(count_nucleotides(dna_seq, 2))
    
    # 2. Specific counts for 3, 4, 6, 12, and 18-nucleotides
    for s in ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]:
        counts = count_nucleotides(dna_seq, len(s))
        print_count(counts, s)

if __name__ == "__main__":
    main()