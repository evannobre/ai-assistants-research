#!/usr/bin/env python3
import sys
import argparse

# Native translation table for complement
COMPLEMENT_TABLE = str.maketrans({
    "A": "T", "T": "A",
    "C": "G", "G": "C",
    "N": "N",
    "a": "t", "t": "a",
    "c": "g", "g": "c",
    "n": "n"
})

CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB chunks


def reverse_complement_stream(input_path, output_handle):
    buffer = []

    with open(input_path, "r") as f:
        for line in f:
            if line.startswith(">"):  # FASTA header
                output_handle.write(line)
                continue

            seq = line.strip()
            if not seq:
                continue

            # Complement using native translate
            complemented = seq.translate(COMPLEMENT_TABLE)

            # Store in buffer for final reverse
            buffer.append(complemented)

    # Join and reverse the entire complemented sequence
    full_seq = "".join(buffer)[::-1]

    # Output in FASTA-friendly 60-char lines
    for i in range(0, len(full_seq), 60):
        output_handle.write(full_seq[i:i+60] + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Reverse complement DNA sequence from file."
    )
    parser.add_argument("input_file", help="Path to DNA or FASTA file")
    parser.add_argument("-o", "--output", help="Output file (optional)")

    args = parser.parse_args()

    if args.output:
        with open(args.output, "w") as out:
            reverse_complement_stream(args.input_file, out)
    else:
        reverse_complement_stream(args.input_file, sys.stdout)


if __name__ == "__main__":
    main()
