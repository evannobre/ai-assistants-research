import sys

def reverse_complement(seq, complement):
    return ''.join(complement.get(base, base) for base in reversed(seq))

def fasta_reverse_complement(stdin, stdout):
    complement = {
        'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A',
        'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S',
        'Y': 'R', 'K': 'M', 'V': 'B', 'H': 'D',
        'D': 'H', 'B': 'V', 'N': 'N'
    }

    seq_id = None
    description = ""
    sequence = []

    for line in stdin:
        line = line.rstrip('\n')
        if line.startswith('>'):
            if seq_id:
                # Output current sequence
                full_seq = ''.join(sequence)
                rev_comp = reverse_complement(full_seq, complement)
                stdout.write(f"{seq_id} {description}\n")
                for i in range(0, len(rev_comp), 60):
                    stdout.write(rev_comp[i:i+60] + '\n')
            # Start new sequence
            parts = line[1:].split(maxsplit=1)
            seq_id = '>' + parts[0]
            description = parts[1] if len(parts) > 1 else ""
            sequence = []
        else:
            sequence.append(line.upper())

    if seq_id:
        full_seq = ''.join(sequence)
        rev_comp = reverse_complement(full_seq, complement)
        stdout.write(f"{seq_id} {description}\n")
        for i in range(0, len(rev_comp), 60):
            stdout.write(rev_comp[i:i+60] + '\n')

if __name__ == "__main__":
    fasta_reverse_complement(sys.stdin, sys.stdout)
