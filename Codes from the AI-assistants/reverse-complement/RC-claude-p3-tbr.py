#!/usr/bin/env python3
"""
Reverse complement FASTA sequence processor.
Reads FASTA format from stdin and writes reverse complement to stdout.
"""

import sys

# Complement mapping using str.maketrans for efficient translation
COMPLEMENT_MAP = str.maketrans(
    'ACGTMRWSYKVHDBNacgtmrwsykvhdbn',
    'TGCAKYWSRMBDHVNtgcakywsrmbdhvn'
)

def process_fasta():
    """
    Process FASTA input line-by-line, growing data incrementally.
    Writes reverse complement sequences to stdout.
    """
    sequence_lines = []
    header = None
    
    for line in sys.stdin:
        line = line.rstrip('\n\r')
        
        if line.startswith('>'):
            # Process previous sequence if exists
            if header is not None:
                write_reverse_complement(header, sequence_lines)
            
            # Start new sequence
            header = line
            sequence_lines = []
        else:
            # Accumulate sequence data
            sequence_lines.append(line)
    
    # Process last sequence
    if header is not None:
        write_reverse_complement(header, sequence_lines)

def write_reverse_complement(header, sequence_lines):
    """
    Write the reverse complement of a sequence in FASTA format.
    
    Args:
        header: FASTA header line (with >)
        sequence_lines: List of sequence lines to process
    """
    # Write header
    print(header)
    
    # Join all sequence lines into single string
    sequence = ''.join(sequence_lines)
    
    # Create reverse complement using translate and reverse
    rev_comp = sequence.translate(COMPLEMENT_MAP)[::-1]
    
    # Write in 60-character lines (standard FASTA format)
    for i in range(0, len(rev_comp), 60):
        print(rev_comp[i:i+60])

if __name__ == '__main__':
    process_fasta()
