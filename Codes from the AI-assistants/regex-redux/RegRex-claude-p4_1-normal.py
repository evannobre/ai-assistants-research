#!/usr/bin/env python3
"""
Regex-Redux: FASTA sequence processing benchmark
Uses native 're' module for regex operations
"""

import sys
import re

def main():
    # Read all input from stdin
    input_data = sys.stdin.read()
    
    # Record initial sequence length
    initial_length = len(input_data)
    
    # Remove FASTA descriptions and linefeeds
    # Pattern: remove lines starting with '>' and all newline characters
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(sequence)
    
    # Define the 8-mer patterns (DNA sequences and reverse complements)
    patterns = [
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
    
    # Count matches for each pattern
    for pattern in patterns:
        count = len(re.findall(pattern, sequence))
        print(f'{pattern} {count}')
    
    # Define magic patterns and their replacements
    replacements = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    # Apply replacements one at a time
    result_sequence = sequence
    for pattern, replacement in replacements:
        result_sequence = re.sub(pattern, replacement, result_sequence)
    
    final_length = len(result_sequence)
    
    # Write the three recorded sequence lengths
    print()
    print(initial_length)
    print(cleaned_length)
    print(final_length)

if __name__ == '__main__':
    main()