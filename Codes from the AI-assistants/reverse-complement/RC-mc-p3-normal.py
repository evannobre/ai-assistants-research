#!/usr/bin/env python3
import sys

# Build complement translation table using native str.maketrans
_complement_map = {
    'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A',
    'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S',
    'Y': 'R', 'K': 'M', 'V': 'B', 'H': 'D',
    'D': 'H', 'B': 'V', 'N': 'N',
}

# Add lowercase equivalents for robustness
complement_pairs = {}
for k, v in _complement_map.items():
    complement_pairs[k] = v
    complement_pairs[k.lower()] = v.lower()

COMPLEMENT_TABLE = str.maketrans(complement_pairs)

LINE_WIDTH = 60  # standard FASTA wrapping


def write_reverse_complement(header, chunks, out):
    """Given a header and list of sequence chunks, write reverse-complement FASTA."""
    if header is None:
        return
    # Join chunks into a single sequence string
    seq = "".join(chunks)
    # Reverse and complement using native operations
    rev_comp = seq[::-1].translate(COMPLEMENT_TABLE)

    # Write header
    out.write(header + "\n")

    # Write sequence wrapped to LINE_WIDTH
    for i in range(0, len(rev_comp), LINE_WIDTH):
        out.write(rev_comp[i:i + LINE_WIDTH] + "\n")


def main():
    current_header = None
    current_chunks = []

    # Read stdin line-by-line (buffered by Python's IO)
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue  # skip empty lines if any

        if line.startswith(">"):
            # New record: flush previous one
            if current_header is not None:
                write_reverse_complement(current_header, current_chunks, sys.stdout)
            current_header = line
            current_chunks = []
        else:
            # Sequence line
            current_chunks.append(line)

    # Flush last record at EOF
    if current_header is not None:
        write_reverse_complement(current_header, current_chunks, sys.stdout)


if __name__ == "__main__":
    main()
