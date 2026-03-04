import sys
import re
from collections import Counter

def main():
    # Read entire input stream (could be from file or stdin)
    sequence = sys.stdin.read()

    # Remove description lines and newlines
    sequence = re.sub(r'>.*\n|\n', '', sequence)

    # Initial length of sequence
    initial_length = len(sequence)

    # Define variants to count
    variants = [
        'agggtaaa|tttaccct',
        '[cgt]gggtaaa|tttaccc[acg]',
        'a[act]ggtaaa|tttacc[agt]t',
        'ag[act]gtaaa|tttac[agt]ct',
        'agg[act]taaa|ttta[agt]cct',
        'aggg[acg]aaa|ttt[cgt]ccct',
        'agggt[cgt]aa|tt[acg]accct',
        'agggta[cgt]a|t[acg]taccct',
        'agggtaa[cgt]|[acg]ttaccct',
    ]

    # Count occurrences of each pattern
    for variant in variants:
        pattern = re.compile(variant, re.IGNORECASE)
        count = len(pattern.findall(sequence))
        print(f"{variant} {count}")

    # Substitutions as per the benchmark
    substitutions = {
        'B': '(c|g|t)',
        'D': '(a|g|t)',
        'H': '(a|c|t)',
        'K': '(g|t)',
        'M': '(a|c)',
        'N': '(a|c|g|t)',
        'R': '(a|g)',
        'S': '(c|g)',
        'V': '(a|c|g)',
        'W': '(a|t)',
        'Y': '(c|t)',
    }

    # Apply all substitutions
    sub_sequence = sequence
    for key, val in substitutions.items():
        sub_sequence = re.sub(key, val, sub_sequence)

    # Output final lengths
    print(f"\n{initial_length}")
    print(f"{len(sequence)}")
    print(f"{len(sub_sequence)}")

if __name__ == '__main__':
    main()
