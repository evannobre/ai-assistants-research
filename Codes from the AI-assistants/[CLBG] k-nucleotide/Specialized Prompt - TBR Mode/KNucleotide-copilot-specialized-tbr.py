#!/usr/bin/env python3
import sys
from collections import Counter

def read_fasta_stream(stream):
    """
    Read all lines from a FASTA-formatted stream (stdin),
    skip header lines (beginning with '>'), and concatenate
    the sequence into one uppercase string.
    """
    pieces = []
    for line in stream:
        if line.startswith('>'):
            continue
        pieces.append(line.strip().upper())
    return ''.join(pieces)

def count_kmers(seq, k, counter):
    """
    Slide a window of length k over seq and increment counts
    in the supplied Counter.
    """
    n = len(seq)
    for i in range(n - k + 1):
        kmer = seq[i:i+k]
        counter[kmer] += 1

def report_frequencies(counter, total, fmt="{kmer} {pct:.3f}%"):
    """
    Print k-mer frequencies sorted by:
      1. descending count
      2. ascending k-mer string
    """
    items = sorted(counter.items(),
                   key=lambda kv: (-kv[1], kv[0]))
    for kmer, cnt in items:
        pct = cnt * 100.0 / total
        print(fmt.format(kmer=kmer, pct=pct))

def report_specific_counts(counter, patterns):
    """
    For each pattern in patterns, print pattern and its raw count.
    """
    for pat in patterns:
        print(f"{counter.get(pat, 0)}\t{pat}")

def main():
    # 1. Read the entire DNA sequence from stdin
    seq = read_fasta_stream(sys.stdin)

    # 2. Prepare Counters for all k up to 18
    counters = {k: Counter() for k in (1,2,3,4,6,12,18)}

    # 3. Count k-mers for each desired k
    for k in counters:
        count_kmers(seq, k, counters[k])

    # 4. Report 1- and 2-mer frequencies
    for k in (1,2):
        total = sum(counters[k].values())
        print(f"\n--- {k}-nucleotide frequencies ({total} total) ---")
        report_frequencies(counters[k])

    # 5. Report counts for the specific patterns
    patterns = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT"
    ]
    print("\n--- Specific pattern counts ---")
    report_specific_counts(counters[max(len(p) for p in patterns)], patterns)

if __name__ == "__main__":
    main()
