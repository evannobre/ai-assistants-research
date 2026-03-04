#!/usr/bin/env python3
import sys
from bisect import bisect_left

IM = 139968
IA = 3877
IC = 29573

seed = 42
WIDTH = 60

def next_rand():
    global seed
    seed = (seed * IA + IC) % IM
    return seed / IM

def cumulative(probs):
    c = []
    s = 0.0
    for p in probs:
        s += p
        c.append(s)
    return c

def pick(symbols, cum):
    # Use stdlib binary search (fast, still "naïve" RNG arithmetic).
    r = next_rand()
    i = bisect_left(cum, r)
    return symbols[i if i < len(symbols) else -1]

def write_lines_from_generator(gen, total_len):
    out = sys.stdout.write
    while total_len > 0:
        k = WIDTH if total_len >= WIDTH else total_len
        # Build one line and write once.
        line = ''.join(next(gen) for _ in range(k))
        out(line + '\n')
        total_len -= k

def fasta_repeat(header, base, total_len):
    out = sys.stdout.write
    out(header + '\n')
    m = len(base)
    idx = 0

    while total_len > 0:
        k = WIDTH if total_len >= WIDTH else total_len
        if idx + k <= m:
            out(base[idx:idx+k] + '\n')
            idx += k
        else:
            # wrap-around
            part1 = base[idx:]
            remain = k - (m - idx)
            part2 = base[:remain]
            out(part1 + part2 + '\n')
            idx = remain
        if idx == m:
            idx = 0
        total_len -= k

def fasta_random(header, symbols, probs, total_len):
    out = sys.stdout.write
    out(header + '\n')
    cum = cumulative(probs)

    def gen():
        while True:
            yield pick(symbols, cum)

    write_lines_from_generator(gen(), total_len)

def main(n):
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    iub_symbols = list("acgtBDHKMNRSVWY")
    iub_probs   = [0.27, 0.12, 0.12, 0.27] + [0.02] * 11

    hs_symbols = list("acgt")
    hs_probs   = [0.3029549426680, 0.1979883004921,
                  0.1975473066391, 0.3015094502008]

    fasta_repeat(">ONE Homo sapiens alu", alu, n * 2)
    fasta_random(">TWO IUB ambiguity codes", iub_symbols, iub_probs, n * 3)
    fasta_random(">THREE Homo sapiens frequency", hs_symbols, hs_probs, n * 5)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    main(n)
