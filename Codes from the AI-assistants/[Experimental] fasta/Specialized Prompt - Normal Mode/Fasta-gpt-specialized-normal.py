#!/usr/bin/env python3

import sys

# LCG constants (glibc-like)
MODULUS = 2**31
MULTIPLIER = 1103515245
INCREMENT = 12345

# DNA bases
DNA_BASES = ['A', 'C', 'G', 'T']

class LCG:
    def __init__(self, seed=42):
        self.state = seed

    def next(self):
        self.state = (MULTIPLIER * self.state + INCREMENT) % MODULUS
        return self.state

    def next_float(self):
        return self.next() / MODULUS

    def next_base(self):
        return DNA_BASES[self.next() % 4]


def generate_fasta(sequence_id, description, length, seed=42, line_length=60, out=sys.stdout):
    rng = LCG(seed)
    print(f">{sequence_id} {description}", file=out)

    # Generate and write the sequence in chunks
    written = 0
    buffer = []

    while written < length:
        line = ''.join(rng.next_base() for _ in range(min(line_length, length - written)))
        buffer.append(line)
        written += len(line)

    print('\n'.join(buffer), file=out)


def main():
    if len(sys.argv) < 2:
        print("Usage: ./fasta_sim.py <sequence_length>", file=sys.stderr)
        sys.exit(1)

    try:
        sequence_length = int(sys.argv[1])
        if sequence_length <= 0:
            raise ValueError("Length must be positive.")
    except ValueError:
        print("Invalid sequence length. Must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    generate_fasta("LCG_SIM", "Naive LCG-generated DNA sequence", sequence_length)


if __name__ == "__main__":
    main()
