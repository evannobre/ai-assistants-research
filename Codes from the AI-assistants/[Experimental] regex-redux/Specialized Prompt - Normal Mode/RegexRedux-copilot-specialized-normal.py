#!/usr/bin/env python3
import sys
import re

# Precompiled regex patterns for speed
regex_patterns = [
    b'agggtaaa|tttaccct',
    b'[cgt]gggtaaa|tttaccc[acg]',
    b'a[act]ggtaaa|tttacc[agt]t',
    b'ag[act]gtaaa|tttac[agt]ct',
    b'agg[act]taaa|ttta[agt]cct',
    b'aggg[acg]aaa|ttt[cgt]ccct',
    b'agggt[cgt]aa|tt[acg]accct',
    b'agggta[cgt]a|t[acg]taccct',
    b'agggtaa[cgt]|[acg]ttaccct'
]

substitutions = [
    (b'B', b'(c|g|t)'),
    (b'D', b'(a|g|t)'),
    (b'H', b'(a|c|t)'),
    (b'K', b'(g|t)'),
    (b'M', b'(a|c)'),
    (b'N', b'(a|c|g|t)'),
    (b'R', b'(a|g)'),
    (b'S', b'(c|g)'),
    (b'V', b'(a|c|g)'),
    (b'W', b'(a|t)'),
    (b'Y', b'(c|t)')
]

def main():
    # Read and filter input
    raw = sys.stdin.buffer.read()
    initial_len = len(raw)

    # Remove headers and newlines
    sequence = re.sub(b'>.*\n|\n', b'', raw)
    cleaned_len = len(sequence)

    # Pattern matching
    for pat in regex_patterns:
        count = len(re.findall(pat, sequence))
        print(f"{pat.decode()} {count}")

    # Substitutions
    for key, val in substitutions:
        sequence = sequence.replace(key, val)

    print(f"\nInitial Length: {initial_len}")
    print(f"Cleaned Length: {cleaned_len}")
    print(f"Final Length: {len(sequence)}")

if __name__ == "__main__":
    main()
