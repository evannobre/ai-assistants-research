import sys
from collections import Counter

def count_frequencies(sequence, k):
    """Counts the frequencies of k-mers in a sequence."""
    counts = Counter()
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
    return counts

def print_sorted_frequencies(total_count, frequencies):
    """Prints the frequencies sorted by count (descending) and then by key (ascending)."""
    sorted_freqs = sorted(
        frequencies.items(),
        key=lambda item: (-item[1], item[0])
    )
    for kmer, count in sorted_freqs:
        percentage = (count * 100.0) / total_count
        print(f"{kmer} {percentage:.3f}")
    print()

def find_specific_kmer_count(frequencies, kmer):
    """Finds the count of a specific k-mer."""
    return frequencies.get(kmer, 0)

if __name__ == "__main__":
    # 1. Read the Input
    sequence = ""
    for line in sys.stdin:
        if not line.startswith('>'):
            sequence += line.strip()

    sequence = sequence.upper()

    # 2. Frequency Counting (k=1 and k=2)
    freq1 = count_frequencies(sequence, 1)
    freq2 = count_frequencies(sequence, 2)

    # 4. Sorting and Output
    total_len_1 = len(sequence)
    print_sorted_frequencies(total_len_1, freq1)

    total_len_2 = len(sequence) - 1
    if total_len_2 < 0:
        total_len_2 = 0
    print_sorted_frequencies(total_len_2, freq2)


    # 3. Frequency Counting (Specific k-mers)
    specific_kmers = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    for kmer in specific_kmers:
        k = len(kmer)
        freq_k = count_frequencies(sequence, k)
        count = find_specific_kmer_count(freq_k, kmer)
        print(f"{count}\t{kmer}")