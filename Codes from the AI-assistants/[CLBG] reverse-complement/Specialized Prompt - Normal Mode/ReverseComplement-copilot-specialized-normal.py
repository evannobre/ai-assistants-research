import sys

# Define DNA complements
COMPLEMENT = {
    'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A',
    'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S', 'Y': 'R',
    'K': 'M', 'V': 'B', 'H': 'D', 'D': 'H', 'B': 'V',
    'N': 'N'
}

def reverse_complement(seq):
    """Returns the reverse complement of a DNA sequence."""
    return "".join(COMPLEMENT.get(base, base) for base in reversed(seq))

def process_fasta():
    """Reads a FASTA file from stdin and outputs the reverse complement."""
    header = None
    sequence = []

    for line in sys.stdin:
        line = line.strip()
        if line.startswith(">"):  # FASTA header
            if header:  # Process previous sequence
                print(header)
                print(reverse_complement("".join(sequence)))
            header = line  # Store new header
            sequence = []
        else:
            sequence.append(line)

    # Output last sequence
    if header:
        print(header)
        print(reverse_complement("".join(sequence)))

if __name__ == "__main__":
    process_fasta()
