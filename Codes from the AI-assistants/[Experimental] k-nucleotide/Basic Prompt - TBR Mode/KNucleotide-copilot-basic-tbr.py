import sys
import re
from collections import Counter

def read_sequence(stream):
    """Read all text, strip non-letters, uppercase."""
    data = stream.read()
    return re.sub(r'[^ACGTacgt]', '', data).upper()

def count_kmers(seq, k):
    """Return a Counter of all k-length substrings in seq."""
    # Generator expression feeds slices directly into Counter
    kmers = (seq[i:i+k] for i in range(len(seq) - k + 1))
    return Counter(kmers)

def report_frequencies(counter):
    """Print k-mer frequencies sorted by descending count."""
    total = sum(counter.values())
    for kmer, count in counter.most_common():
        print(f"{kmer} {100 * count / total:6.3f}%")

def query_kmers(counter, queries):
    """Print counts for specific k-mers."""
    for q in queries:
        print(f"{q} {counter[q]}")

def main():
    # 1. Read & clean input
    sequence = read_sequence(sys.stdin)
    
    # 2. For each k, count and report
    for k in [1, 2]:  # example ks; change as needed
        print(f"\n{k}-mer frequencies:")
        ctr = count_kmers(sequence, k)
        report_frequencies(ctr)
    
    # 3. Query specific k-mers (example)
    queries = ["GGT", "GGTA", "GGTC", "GGTG", "GGTGG"]
    print("\nSpecific k-mer counts:")
    # Build one more Counter for the max query length
    max_k = max(len(q) for q in queries)
    ctr_max = count_kmers(sequence, max_k)
    query_kmers(ctr_max, queries)

if __name__ == "__main__":
    main()
