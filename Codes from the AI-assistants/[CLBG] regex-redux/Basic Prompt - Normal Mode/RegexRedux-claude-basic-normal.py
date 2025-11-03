#!/usr/bin/env python3
"""
Regex Redux Algorithm Implementation
Follows the exact specification for processing FASTA format data
using native regex operations without optimization.
"""

import sys
import re

def main():
    # Step 1: Read all input from stdin and record sequence length
    input_data = sys.stdin.read()
    original_length = len(input_data)
    
    # Step 2: Remove FASTA sequence descriptions and linefeeds
    # Remove lines starting with '>' (FASTA headers)
    # Remove all linefeed characters
    sequence_data = re.sub(r'>.*\n', '', input_data)
    sequence_data = re.sub(r'\n', '', sequence_data)
    cleaned_length = len(sequence_data)
    
    # Step 3: Count matches for DNA 8-mers and reverse complements
    # These patterns represent DNA 8-mers with wildcards
    dna_patterns = [
        r'agggtaaa|tttaccct',
        r'[cgt]gggtaaa|tttaccc[acg]',
        r'a[act]ggtaaa|tttacc[agt]t',
        r'ag[act]gtaaa|tttac[agt]ct',
        r'agg[act]taaa|ttta[agt]cct',
        r'aggg[acg]aaa|ttt[cgt]ccct',
        r'agggt[cgt]aa|tt[acg]accct',
        r'agggta[cgt]a|t[acg]taccct',
        r'agggtaa[cgt]|[acg]ttaccct'
    ]
    
    # Count matches for each pattern and print results
    for pattern in dna_patterns:
        matches = re.findall(pattern, sequence_data, re.IGNORECASE)
        count = len(matches)
        print(f"{pattern} {count}")
    
    # Step 4: Apply magic regex replacements
    # These patterns are applied one at a time in order
    magic_patterns = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    # Apply each replacement pattern in sequence
    modified_sequence = sequence_data
    for pattern, replacement in magic_patterns:
        modified_sequence = re.sub(pattern, replacement, modified_sequence)
    
    final_length = len(modified_sequence)
    
    # Step 5: Write the three recorded sequence lengths
    print()
    print(f"{original_length}")
    print(f"{cleaned_length}")
    print(f"{final_length}")

if __name__ == "__main__":
    main()