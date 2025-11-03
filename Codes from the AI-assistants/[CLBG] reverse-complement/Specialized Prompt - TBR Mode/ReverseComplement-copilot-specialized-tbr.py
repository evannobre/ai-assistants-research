import sys

# Define the complement mapping for each base/ambiguity code.
COMPLEMENT = {
    'A': 'T',
    'T': 'A',
    'U': 'A',  # Treat U as T.
    'C': 'G',
    'G': 'C',
    'M': 'K',  # A or C ➜ K (complement to T or G)
    'R': 'Y',  # A or G ➜ Y (complement to T or C)
    'W': 'W',  # A or T ➜ W (self-complementary)
    'S': 'S',  # C or G ➜ S (self-complementary)
    'Y': 'R',  # C or T ➜ R (complement to G or A)
    'K': 'M',  # G or T ➜ M (complement to C or A)
    'V': 'B',  # A or C or G ➜ B
    'H': 'D',  # A or C or T ➜ D
    'D': 'H',  # A or G or T ➜ H
    'B': 'V',  # C or G or T ➜ V
    'N': 'N'   # Any ➜ N
}

def reverse_complement(sequence):
    """
    Compute the reverse complement of a DNA sequence.
    The function iterates the given sequence in reverse order,
    mapping each base to its complement according to the COMPLEMENT dictionary.
    """
    # Using list comprehension for efficiency.
    rev_comp = [COMPLEMENT.get(base.upper(), base) for base in reversed(sequence)]
    return ''.join(rev_comp)

def process_fasta(stream):
    """
    Process each FASTA record from the input stream.
    It buffers the sequence until a new header is encountered.
    Upon reaching a new record or the end of the file, it computes and outputs
    the reverse complement for the buffered sequence.
    """
    header = None
    seq_lines = []
    
    for line in stream:
        line = line.rstrip('\n')
        if not line:
            continue  # Skip empty lines
        
        # Start of a new FASTA record
        if line.startswith(">"):
            if header is not None:
                # Combine sequence lines
                sequence = ''.join(seq_lines)
                # Compute the reverse complement
                rc_sequence = reverse_complement(sequence)
                # Output header and reverse complement sequences in FASTA format
                print(header)
                # Optionally, wrap output lines at 60 characters per line
                for i in range(0, len(rc_sequence), 60):
                    print(rc_sequence[i:i+60])
            
            # Set the header for the new record and reset the sequence buffer
            header = line
            seq_lines = []
        else:
            # Accumulate this line into the sequence buffer
            seq_lines.append(line.strip())
    
    # Process the final record in the file if it exists.
    if header is not None:
        sequence = ''.join(seq_lines)
        rc_sequence = reverse_complement(sequence)
        print(header)
        for i in range(0, len(rc_sequence), 60):
            print(rc_sequence[i:i+60])

if __name__ == "__main__":
    process_fasta(sys.stdin)
