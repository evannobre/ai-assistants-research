import sys

# Complement mapping dictionary
COMPLEMENT = {
    'A': 'T', 'T': 'A', 'U': 'A',
    'C': 'G', 'G': 'C',
    'M': 'K', 'K': 'M',
    'R': 'Y', 'Y': 'R',
    'W': 'W', 'S': 'S',
    'V': 'B', 'B': 'V',
    'H': 'D', 'D': 'H',
    'N': 'N',
    'a': 't', 't': 'a', 'u': 'a',
    'c': 'g', 'g': 'c',
    'm': 'k', 'k': 'm',
    'r': 'y', 'y': 'r',
    'w': 'w', 's': 's',
    'v': 'b', 'b': 'v',
    'h': 'd', 'd': 'h',
    'n': 'n'
}

def reverse_complement(seq):
    # Reverse the sequence and complement each base
    return ''.join([COMPLEMENT.get(base, base) for base in reversed(seq)])

def process_fasta():
    header = None
    sequence = []
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('>'):
            # Output previous sequence if exists
            if header is not None:
                print(header)
                print(reverse_complement(''.join(sequence)))
            
            # Start new sequence
            header = line
            sequence = []
        else:
            sequence.append(line)
    
    # Output the last sequence
    if header is not None:
        print(header)
        print(reverse_complement(''.join(sequence)))

if __name__ == "__main__":
    process_fasta()