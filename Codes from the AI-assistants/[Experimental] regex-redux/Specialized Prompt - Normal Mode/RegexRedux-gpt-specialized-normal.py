#!/usr/bin/env python3
import sys
import re

def main():
    # Read entire input
    data = sys.stdin.read()

    # Initial input length
    initial_length = len(data)

    # Remove FASTA headers (lines starting with '>') and newlines
    sequence = re.sub(r'>.*\n|\n', '', data)
    cleaned_length = len(sequence)

    # List of regex patterns to count
    patterns = [
        r'agggtaaa|tttaccct',
        r'[cgt]gggtaaa|tttaccc[acg]',
        r'a[act]ggtaaa|tttacc[agt]t',
        r'ag[act]gtaaa|tttac[agt]ct',
        r'agg[act]taaa|ttta[agt]cct',
        r'aggg[acg]aaa|ttt[cgt]ccct',
        r'agggt[cgt]aa|tt[acg]accct',
        r'agggta[cgt]a|t[acg]taccct',
        r'agggtaa[cgt]|[acg]ttaccct'
    ]

    # Count and display pattern matches
    for pattern in patterns:
        count = len(re.findall(pattern, sequence, flags=re.IGNORECASE))
        print(f"{pattern} {count}")

    # Substitution patterns
    substitutions = [
        (r'B', '(c|g|t)'),
        (r'D', '(a|g|t)'),
        (r'H', '(a|c|t)'),
        (r'K', '(g|t)'),
        (r'M', '(a|c)'),
        (r'N', '(a|c|g|t)'),
        (r'R', '(a|g)'),
        (r'S', '(c|g)'),
        (r'V', '(a|c|g)'),
        (r'W', '(a|t)'),
        (r'Y', '(c|t)')
    ]

    # Apply all substitutions
    substituted_sequence = sequence
    for pattern, repl in substitutions:
        substituted_sequence = re.sub(pattern, repl, substituted_sequence)

    # Final output lengths
    print(f"\n{initial_length}")
    print(f"{cleaned_length}")
    print(f"{len(substituted_sequence)}")

if __name__ == "__main__":
    main()
