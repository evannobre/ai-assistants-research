#!/usr/bin/env python3
import sys
from collections import Counter

def read_fasta_three(stdin):
    name = None
    seq_parts = []
    capture = False
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            name = line[1:].split()[0]
            capture = (name == 'THREE')
            seq_parts = []
            continue
        if capture:
            seq_parts.append(line.upper())
    return ''.join(seq_parts)

def update_counts(frame_start, k, seq, counts):
    n = len(seq)
    end = n - k + 1
    # iterate positions in this frame
    code_map = {'A':0, 'C':1, 'G':2, 'T':3}
    mask = (1 << (2*k)) - 1  # keep only 2*k bits if needed

    # build first key for position frame_start
    key = 0
    for j in range(frame_start, frame_start + k):
        key = (key << 2) | code_map[seq[j]]
    counts[key] += 1

    for i in range(frame_start + 1, end):
        key = ((key << 2) | code_map[seq[i + k - 1]]) & mask
        counts[key] += 1

def percent(count, total):
    return (count / total) * 100.0 if total else 0.0

def main():
    seq = read_fasta_three(sys.stdin)
    if not seq:
        print("No sequence THREE found on stdin", file=sys.stderr)
        return

    # Count 1- and 2-nucleotide sequences
    counts_1 = Counter()
    counts_2 = Counter()
    for frame in (0, 1, 2):
        update_counts(frame, 1, seq, counts_1)
        update_counts(frame, 2, seq, counts_2)

    # Combine totals and print sorted by descending frequency then ascending key
    total1 = sum(counts_1.values())
    total2 = sum(counts_2.values())

    def print_freq(counter, total):
        items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        for k, c in items:
            print(f"{k} {percent(c, total):.3f}")

    # Output 1-nucleotide frequencies
    print("1-nucleotide frequencies:")
    print_freq(counts_1, total1)
    print()

    # Output 2-nucleotide frequencies
    print("2-nucleotide frequencies:")
    print_freq(counts_2, total2)
    print()

    # Count specific lengths and sequences
    lengths = [3, 4, 6, 12, 18]
    targets = {
        3: ["GGT"],
        4: ["GGTA"],
        6: ["GGTATT"],
        12: ["GGTATTTTAATT"],
        18: ["GGTATTTTAATTTATAGT"]
    }

    # For each length, build a Counter by frames
    for L in lengths:
        c = Counter()
        for frame in (0,1,2):
            update_counts(frame, L, seq, c)
        print(f"{L}-nucleotide counts (total distinct {len(c)}):")
        for t in targets.get(L, []):
            print(f"{t} {c.get(t, 0)}")
        print()

if __name__ == "__main__":
    main()
