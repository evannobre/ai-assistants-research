import sys
import re
from collections import Counter

def read_sequence_from_stdin():
    data = sys.stdin.read()
    sequence = []
    matched = False
    for line in data.splitlines():
        if line.startswith('>'):
            matched = line.startswith('>THREE')
            continue
        if matched:
            sequence.append(line.strip())
    return ''.join(sequence).upper()

def generate_frequencies(seq, k):
    counts = Counter(seq[i:i+k] for i in range(len(seq)-k+1))
    total = sum(counts.values())
    freq_list = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [(kmer, (count / total) * 100) for kmer, count in freq_list]

def count_specific(seq, targets):
    results = {}
    for target in targets:
        count = sum(1 for i in range(len(seq)-len(target)+1) if seq[i:i+len(target)] == target)
        results[target] = count
    return results

def main():
    sequence = read_sequence_from_stdin()
    
    # 1. Frequencies
    for k in [1, 2]:
        freqs = generate_frequencies(sequence, k)
        for kmer, percent in freqs:
            print(f"{kmer} {percent:.3f}")
        print()

    # 2. Specific fragment counts
    for frag in ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]:
        count = sequence.count(frag)
        print(f"{count}\t{frag}")

if __name__ == "__main__":
    main()
