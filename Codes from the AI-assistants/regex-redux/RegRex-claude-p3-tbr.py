#!/usr/bin/env python3
"""
regex-redux implementation following the benchmark specification.
Uses native Python re library for all regex operations.
"""

import sys
import re


def main():
    # Read all input from stdin
    input_data = sys.stdin.read()
    
    # Record initial sequence length
    initial_length = len(input_data)
    
    # Remove FASTA sequence descriptions (lines starting with '>') and linefeeds
    # Pattern: remove '>' lines and all newline characters
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    
    # Record cleaned sequence length
    cleaned_length = len(sequence)
    
    # DNA 8-mer patterns (with reverse complements and wildcards)
    variant_patterns = [
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
    
    # Count and print matches for each variant pattern
    for pattern in variant_patterns:
        count = len(re.findall(pattern, sequence))
        print(f'{pattern} {count}')
    
    # Magic substitution patterns and their replacements
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    # Apply each substitution in order
    modified_sequence = sequence
    for pattern, replacement in substitutions:
        modified_sequence = re.sub(pattern, replacement, modified_sequence)
    
    # Record final sequence length
    final_length = len(modified_sequence)
    
    # Print the three recorded sequence lengths
    print()
    print(initial_length)
    print(cleaned_length)
    print(final_length)


if __name__ == '__main__':
    main()
