import sys
import re
from collections import Counter

def read_sequence(label):
    data = sys.stdin.read().upper()
    match = re.search(rf">{label}\n([A-Z\n]+)", data)
    if not match:
        return ""
    return "".join(match.group(1).splitlines())

def count_kmers(seq, k):
    return Counter(seq[i:i+k] for i in range(len(seq) - k + 1))

def print_freq(counter, k):
    total = sum(counter.values())
    sorted_items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    for kmer, count in sorted_items:
        percentage = 100.0 * count / total
        print(f"{kmer} {percentage:.3f}")

def print_specific_counts(counter, targets):
    for target in targets:
        print(f"{counter.get(target, 0)}\t{target}")

def main():
    seq = read_sequence("THREE")

    # 1-mer and 2-mer frequencies
    for k in [1, 2]:
        kmers = count_kmers(seq, k)
        print_freq(kmers, k)
        print()

    # Targeted counts for longer kmers
    targets = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    for k in [3, 4, 6, 12, 18]:
        kmers = count_kmers(seq, k)
        print_specific_counts(kmers, [t for t in targets if len(t) == k])

if __name__ == "__main__":
    main()