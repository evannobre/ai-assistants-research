import sys

# Dictionary of complement bases
complements = {
    'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A',
    'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S', 'Y': 'R',
    'K': 'M', 'V': 'B', 'H': 'D', 'D': 'H', 'B': 'V',
    'N': 'N'
}

def reverse_complement(sequence):
    """Returns the reverse complement of a DNA sequence."""
    return ''.join(complements.get(base, base) for base in reversed(sequence))

def process_fasta():
    """Reads a FASTA file from stdin line-by-line and processes sequences."""
    sequence_id = None
    description = None
    sequence_parts = []

    for line in sys.stdin:
        line = line.strip()
        if line.startswith(">"):
            # If there's an existing sequence, process it
            if sequence_id:
                print(f">{sequence_id} {description}")
                print(reverse_complement(''.join(sequence_parts)))

            # Start a new sequence
            parts = line.split(maxsplit=1)
            sequence_id = parts[0][1:]
            description = parts[1] if len(parts) > 1 else ''
            sequence_parts = []
        else:
            sequence_parts.append(line)

    # Process the last sequence in the file
    if sequence_id:
        print(f">{sequence_id} {description}")
        print(reverse_complement(''.join(sequence_parts)))

if __name__ == "__main__":
    process_fasta()
