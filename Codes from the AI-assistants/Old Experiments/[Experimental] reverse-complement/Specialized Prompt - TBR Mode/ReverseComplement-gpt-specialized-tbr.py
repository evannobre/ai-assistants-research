#!/usr/bin/env python3
import sys
import argparse

# Build a translation table for fast byte-wise complement
# Works on ASCII bytes: ord('A')=65, etc.
# We include both uppercase and lowercase, and map anything else to itself.
_COMP_TABLE = bytes.maketrans(
    b"ACGTacgt",
    b"TGCAtgca"
)

def reverse_complement(seq: bytes) -> bytes:
    """
    Compute the reverse complement of a DNA sequence (bytes).
    Non-ACGT letters pass through unchanged.
    """
    # 1) Translate to complement, 2) reverse
    return seq.translate(_COMP_TABLE)[::-1]

def main():
    parser = argparse.ArgumentParser(
        description="Compute the reverse complement of a DNA sequence."
    )
    parser.add_argument(
        "sequence",
        metavar="SEQ",
        type=str,
        help="DNA sequence (ACGT only) or '-' to read from STDIN"
    )
    args = parser.parse_args()

    # Read sequence (strip whitespace/newlines)
    if args.sequence == "-":
        data = sys.stdin.read().encode('ascii')
    else:
        data = args.sequence.encode('ascii')

    data = b"".join(data.split())  # remove any whitespace

    # Compute reverse complement
    rc = reverse_complement(data)

    # Write to stdout as text
    sys.stdout.buffer.write(rc)
    sys.stdout.buffer.write(b"\n")

if __name__ == "__main__":
    main()
