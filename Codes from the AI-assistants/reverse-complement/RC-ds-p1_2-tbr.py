#!/usr/bin/env python3
import sys

def reverse_complement(dna_seq: str) -> str:
    """Return reverse complement using only built-in functions."""
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
                  'a': 't', 't': 'a', 'c': 'g', 'g': 'c',
                  'N': 'N', 'n': 'n'}
    
    # Build complement string using list comprehension
    rc_list = [complement.get(base, base) for base in reversed(dna_seq)]
    return ''.join(rc_list)

def process_file(filename: str):
    """Process FASTA file line by line."""
    with open(filename, 'r') as f:
        header = None
        seq_parts = []
        
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if header:
                    # Process previous sequence
                    full_seq = ''.join(seq_parts)
                    rc = reverse_complement(full_seq)
                    print(f"{header}_rc")
                    print(rc)
                
                # Start new sequence
                header = line
                seq_parts = []
            else:
                seq_parts.append(line)
        
        # Process last sequence
        if header:
            full_seq = ''.join(seq_parts)
            rc = reverse_complement(full_seq)
            print(f"{header}_rc")
            print(rc)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dna_file.fasta>")
        sys.exit(1)
    
    process_file(sys.argv[1])