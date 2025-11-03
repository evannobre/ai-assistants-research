#!/usr/bin/env python3
"""
reverse_complement.py

Compute the reverse complement of a DNA sequence from the command line.
Uses only Python's standard library (argparse, sys).
"""
import argparse
import sys

# Construct translation table for complements
def build_complement_table():
    bases = 'ACGTacgt'
    complements = 'TGCAtgca'
    return str.maketrans(bases, complements)

# Compute reverse complement
def reverse_complement(seq, table):
    # Translate then reverse
    return seq.translate(table)[::-1]

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description='Compute the reverse complement of a DNA sequence.'
    )
    parser.add_argument(
        '-s', '--sequence',
        help='Input DNA sequence (A, C, G, T only).',
        required=False
    )
    parser.add_argument(
        '-f', '--file',
        help='Path to a file containing a DNA sequence.',
        required=False
    )
    return parser.parse_args()

# Main entry
def main():
    args = parse_args()
    # Read sequence from arg or file or stdin
    if args.sequence:
        seq = args.sequence.strip()
    elif args.file:
        with open(args.file) as fh:
            seq = fh.read().strip()
    else:
        # Read from stdin
        seq = sys.stdin.read().strip()

    if not seq:
        print('Error: No sequence provided.', file=sys.stderr)
        sys.exit(1)

    # Validate
    if any(base not in 'ACGTacgt' for base in seq):
        print('Error: Sequence contains invalid characters.', file=sys.stderr)
        sys.exit(1)

    table = build_complement_table()
    rc = reverse_complement(seq, table)
    print(rc)

if __name__ == '__main__':
    main()
