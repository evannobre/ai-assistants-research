#!/usr/bin/env python3
"""
k_nucleotide.py
Count k-mer frequencies from a DNA file (FASTA or plain). Uses only native libraries.
Usage examples:
  python k_nucleotide.py --file genome.fa --k 1 2 3
  python k_nucleotide.py --file genome.fa --query "GGT" "GGTA"
"""

import argparse
import collections
import mmap
import os
import re
import sys

VALID = re.compile(rb'[ACGT]')

def read_sequence_bytes(path):
    """Return a bytes object with only ACGT (uppercase) from the file."""
    # Try memory-mapping for large files
    with open(path, 'rb') as f:
        try:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            raw = mm.read()
            mm.close()
        except (ValueError, OSError):
            # fallback to normal read
            f.seek(0)
            raw = f.read()
    # Remove FASTA headers and non-ACGT characters, uppercase
    # Replace lowercase with uppercase by mapping bytes
    raw = raw.replace(b'\r', b'\n')
    lines = raw.split(b'\n')
    seq_parts = []
    for line in lines:
        if not line:
            continue
        if line.startswith(b'>'):
            continue
        # Keep only A,C,G,T or a,c,g,t
        # Convert to uppercase quickly
        up = line.upper()
        # Filter bytes not in ACGT
        filtered = VALID.findall(up)
        if filtered:
            seq_parts.append(b''.join(filtered))
    return b''.join(seq_parts)

def count_kmers(seq_bytes, k):
    """Count k-mers in bytes sequence using collections.Counter."""
    n = len(seq_bytes)
    if k <= 0 or k > n:
        return collections.Counter()
    c = collections.Counter()
    # sliding window
    for i in range(n - k + 1):
        kmer = seq_bytes[i:i+k]
        c[kmer] += 1
    return c

def format_percent(count, total):
    return f"{(count/total*100):.3f}"

def main():
    parser = argparse.ArgumentParser(description="k-nucleotide simulation using native libs")
    parser.add_argument('--file', '-f', required=True, help='Input DNA file (FASTA or plain)')
    parser.add_argument('--k', '-k', type=int, nargs='*', default=[1,2], help='k values to compute frequencies for')
    parser.add_argument('--query', '-q', nargs='*', help='Specific k-mers to report counts for')
    args = parser.parse_args()

    seq = read_sequence_bytes(args.file)
    if not seq:
        print("No sequence data found.", file=sys.stderr)
        sys.exit(1)

    # For each requested k, compute counts and print sorted frequencies
    for k in args.k:
        counter = count_kmers(seq, k)
        total = sum(counter.values())
        print(f"\n=== k={k} total={total} distinct={len(counter)} ===")
        # Print top 25 by count
        for kmer, cnt in counter.most_common(25):
            print(f"{kmer.decode('ascii')} {cnt} {format_percent(cnt, total)}%")
        # If queries provided, print their counts
        if args.query:
            print("\nQuery counts:")
            for q in args.query:
                qb = q.upper().encode('ascii')
                print(f"{q} -> {counter.get(qb, 0)}")

if __name__ == '__main__':
    main()
