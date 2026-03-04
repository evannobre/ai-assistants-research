import sys
from collections import defaultdict

def read_fasta_sequence_from_stdin(label='THREE'):
    sequence_lines = []
    in_target = False
    for line in sys.stdin:
        if line.startswith('>'):
            in_target = label in line
        elif in_target:
            sequence_lines.append(line.strip())
    return ''.join(sequence_lines).upper()

def count_kmers(sequence, k):
    counts = defaultdict(int)
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
    return counts

def print_frequencies(counts):
    total = sum(counts.values())
    freq_list = [(k, v * 100 / total) for k, v in counts.items()]
    freq_list.sort(key=lambda x: (-x[1], x[0]))
    for kmer, percent in freq_list:
        print(f"{kmer} {percent:.3f}")

def print_specific_counts(counts, targets):
    for target in targets:
        print(f"{counts.get(target, 0)}\t{target}")

def main():
    sequence = read_fasta_sequence_from_stdin()
    
    # Frequencies for k=1 and k=2
    for k in [1, 2]:
        counts = count_kmers(sequence, k)
        print_frequencies(counts)
        print()

    # Specific counts for listed kmers
    target_kmers = [
        "GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"
    ]
    max_k = max(len(kmer) for kmer in target_kmers)
    counts = count_kmers(sequence, max_k)  # count max K and reuse

    print_specific_counts(counts, target_kmers)

if __name__ == '__main__':
    main()
