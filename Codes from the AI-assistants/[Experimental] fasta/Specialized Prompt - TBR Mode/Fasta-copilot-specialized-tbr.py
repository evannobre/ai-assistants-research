#!/usr/bin/env python3
"""
FASTA simulation using a naive LCG.
Produces three sequences:
  1) A repeating 'alu' pattern
  2) A random sequence with IUB ambiguity codes
  3) A random sequence with Homo sapiens DNA frequencies

Memory usage is O(1), output is line-wrapped at 60 chars.
"""

import sys

# -----------------------------
# 1) Naïve LCG implementation
# -----------------------------
class LCG:
    def __init__(self, seed=42):
        # parameters from the original fasta benchmark
        self._a = 3877
        self._c = 29573
        self._m = 139968
        self._state = seed

    def next_int(self):
        """Produce next int in [0, m)."""
        self._state = (self._state * self._a + self._c) % self._m
        return self._state

    def next_float(self):
        """Produce a float in [0.0, 1.0)."""
        return self.next_int() / self._m


# ----------------------------------------
# 2) Build cumulative distributions once
# ----------------------------------------
def build_cumulative(dist):
    """
    Given a list of (symbol, probability) pairs summing to 1.0,
    return a list of (threshold, symbol) where threshold is
    the cumulative probability.
    """
    cum = []
    total = 0.0
    for sym, prob in dist:
        total += prob
        cum.append((total, sym))
    return cum


# --------------------------------------
# 3) Generate a random sequence as a str
# --------------------------------------
def random_sequence(lcg, cumulative, size, line_width=60):
    """
    Stream out `size` chars selected by sampling `cumulative`
    with `lcg`. Yields lines of up to `line_width` chars.
    """
    buf = []
    count = 0
    for _ in range(size):
        r = lcg.next_float()
        # find first threshold > r
        for thresh, sym in cumulative:
            if r < thresh:
                buf.append(sym)
                break

        count += 1
        if count == line_width:
            yield "".join(buf)
            buf = []
            count = 0

    if buf:
        yield "".join(buf)


# ------------------------------------
# 4) Repeat-pattern sequence generator
# ------------------------------------
def repeat_sequence(pattern, size, line_width=60):
    """
    Stream out `size` chars by repeating `pattern`,
    yielding lines of up to `line_width` chars.
    """
    pat_len = len(pattern)
    buf = []
    count = 0
    for i in range(size):
        buf.append(pattern[i % pat_len])
        count += 1
        if count == line_width:
            yield "".join(buf)
            buf = []
            count = 0

    if buf:
        yield "".join(buf)


# -----------------------
# 5) Main FASTA routine
# -----------------------
def fasta(n=1000000):
    lcg = LCG(seed=42)

    # 5.1) Sequence ONE: the "alu" repeat
    alu_pattern = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACT"
        "GCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    sys.stdout.write(">ONE Homo sapiens alu\n")
    for line in repeat_sequence(alu_pattern, n):
        sys.stdout.write(line + "\n")

    # 5.2) Sequence TWO: IUB ambiguity codes
    iub = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]
    iub_cum = build_cumulative(iub)
    sys.stdout.write(">TWO IUB ambiguity codes\n")
    for line in random_sequence(lcg, iub_cum, n):
        sys.stdout.write(line + "\n")

    # 5.3) Sequence THREE: Homo sapiens DNA frequencies
    homo = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]
    homo_cum = build_cumulative(homo)
    sys.stdout.write(">THREE Homo sapiens frequency\n")
    for line in random_sequence(lcg, homo_cum, n):
        sys.stdout.write(line + "\n")


# ------------------
# 6) Entry-point
# ------------------
if __name__ == "__main__":
    # allow overriding N on the command line
    try:
        N = int(sys.argv[1])
    except (IndexError, ValueError):
        N = 1000000
    fasta(N)
