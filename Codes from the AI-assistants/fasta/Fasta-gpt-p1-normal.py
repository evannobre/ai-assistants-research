#!/usr/bin/env python3
import sys

# --- Naïve LCG RNG (classic FASTA benchmark constants) ---
# These constants match the common FASTA benchmark reference.
IM = 139968
IA = 3877
IC = 29573

seed = 42  # initial seed

def lcg_rand():
    """Return a float in [0, 1) using a naïve LCG."""
    global seed
    seed = (IA * seed + IC) % IM
    return seed / IM


# --- FASTA output helpers ---
LINE_WIDTH = 60

def write_fasta_header(name, desc):
    sys.stdout.write(f">{name} {desc}\n")

def repeat_fasta(seq, n):
    """Write n bases by repeating seq cyclically, width 60."""
    seq = seq.strip()
    L = len(seq)
    idx = 0

    while n > 0:
        chunk_len = LINE_WIDTH if n >= LINE_WIDTH else n
        # Build chunk naively (no fancy slicing tricks across wrap)
        out = []
        for _ in range(chunk_len):
            out.append(seq[idx])
            idx += 1
            if idx == L:
                idx = 0
        sys.stdout.write("".join(out) + "\n")
        n -= chunk_len

def make_cumulative(pairs):
    """Convert (char, prob) list into (char, cumulative_prob) list."""
    cum = 0.0
    out = []
    for ch, p in pairs:
        cum += p
        out.append((ch, cum))
    # Ensure last cumulative is exactly 1.0-ish (naïve fix)
    out[-1] = (out[-1][0], 1.0)
    return out

def pick_from_cumulative(cum_pairs, r):
    """Naïvely pick by linear scan on cumulative probabilities."""
    for ch, cp in cum_pairs:
        if r < cp:
            return ch
    return cum_pairs[-1][0]  # fallback

def random_fasta(cum_pairs, n):
    """Write n bases sampled from cum_pairs using LCG, width 60."""
    while n > 0:
        chunk_len = LINE_WIDTH if n >= LINE_WIDTH else n
        out = []
        for _ in range(chunk_len):
            r = lcg_rand()
            out.append(pick_from_cumulative(cum_pairs, r))
        sys.stdout.write("".join(out) + "\n")
        n -= chunk_len


# --- Benchmark data (FASTA simulation standard) ---
ALU = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

IUB = [
    ("a", 0.27), ("c", 0.12), ("g", 0.12), ("t", 0.27),
    ("B", 0.02), ("D", 0.02), ("H", 0.02), ("K", 0.02),
    ("M", 0.02), ("N", 0.02), ("R", 0.02), ("S", 0.02),
    ("V", 0.02), ("W", 0.02), ("Y", 0.02),
]

HOMO_SAPIENS = [
    ("a", 0.3029549426680),
    ("c", 0.1979883004921),
    ("g", 0.1975473066391),
    ("t", 0.3015094502008),
]

def main():
    # Standard FASTA benchmark input: one integer n
    # Output lengths: 2n, 3n, 5n for the three sections
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else int(sys.stdin.readline().strip())
    except Exception:
        sys.stderr.write("Usage: fasta.py <n>\n")
        return 2

    iub_cum = make_cumulative(IUB)
    hs_cum = make_cumulative(HOMO_SAPIENS)

    write_fasta_header("ONE", "Homo sapiens alu")
    repeat_fasta(ALU, 2 * n)

    write_fasta_header("TWO", "IUB ambiguity codes")
    random_fasta(iub_cum, 3 * n)

    write_fasta_header("THREE", "Homo sapiens frequency")
    random_fasta(hs_cum, 5 * n)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
