#!/usr/bin/env python3
"""
Reverse-Complement DNA Sequence Algorithm
Reads FASTA format from stdin and outputs reverse-complement to stdout
"""

import sys

# Complement mapping using native str.translate() for performance
COMPLEMENT_TABLE = str.maketrans(
    'ACGTUMRWSYKVHDBNacgtumrwsykvhdbn',
    'TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn'
)

def process_fasta():
    """
    Process FASTA format from stdin line-by-line.
    Grows data with buffered reads without pre-allocation.
    """
    sequence_id = None
    sequence_desc = None
    sequence_lines = []
    
    for line in sys.stdin:
        line = line.rstrip('\n\r')
        
        if line.startswith('>'):
            # Process previous sequence if exists
            if sequence_id is not None:
                output_reverse_complement(sequence_id, sequence_desc, sequence_lines)
            
            # Parse new header
            header_parts = line[1:].split(None, 1)
            sequence_id = header_parts[0]
            sequence_desc = header_parts[1] if len(header_parts) > 1 else ''
            sequence_lines = []
        else:
            # Accumulate sequence data (buffered growth)
            sequence_lines.append(line)
    
    # Process final sequence
    if sequence_id is not None:
        output_reverse_complement(sequence_id, sequence_desc, sequence_lines)

def output_reverse_complement(seq_id, seq_desc, seq_lines):
    """
    Calculate and output reverse-complement in FASTA format.
    Uses native string operations for efficiency.
    """
    # Join all sequence lines
    sequence = ''.join(seq_lines)
    
    # Calculate reverse-complement using native operations:
    # 1. Translate to complement using str.translate()
    # 2. Reverse using slice notation
    reverse_comp = sequence.translate(COMPLEMENT_TABLE)[::-1]
    
    # Output header
    if seq_desc:
        print(f'>{seq_id} {seq_desc}')
    else:
        print(f'>{seq_id}')
    
    # Output sequence in 60-character lines (FASTA standard)
    line_width = 60
    for i in range(0, len(reverse_comp), line_width):
        print(reverse_comp[i:i + line_width])

if __name__ == '__main__':
    process_fasta()
