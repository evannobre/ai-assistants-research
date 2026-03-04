#!/usr/bin/env python3
"""
Regex-Redux Benchmark Implementation
Reads FASTA format data and performs regex matching and replacement operations.
"""

import sys
import re


def main():
    # Step 1: Read all input from stdin and record the initial sequence length
    input_data = sys.stdin.read()
    initial_length = len(input_data)
    
    # Step 2: Remove FASTA sequence descriptions and linefeeds
    # Remove lines starting with '>' (FASTA headers)
    # Remove all newline characters
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(sequence)
    
    # Step 3: Count matches for each DNA 8-mer pattern
    # These patterns represent DNA sequences and their reverse complements
    variant_patterns = [
        r'agggtaaa|tttaccct',
        r'[cgt]gggtaaa|tttaccc[acg]',
        r'a[act]ggtaaa|tttacc[agt]t',
        r'ag[act]gtaaa|tttac[agt]ct',
        r'agg[act]taaa|ttta[agt]cct',
        r'aggg[acg]aaa|ttt[cgt]ccct',
        r'agggt[cgt]aa|tt[acg]accct',
        r'agggta[cgt]a|t[acg]taccct',
        r'agggtaa[cgt]|[acg]ttaccct',
    ]
    
    # Count and print matches for each pattern
    for pattern in variant_patterns:
        count = len(re.findall(pattern, sequence))
        print(f'{pattern} {count}')
    
    # Step 4: Perform magic regex pattern replacements
    # These replacements are done sequentially on the same sequence
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-'),
    ]
    
    # Apply each substitution pattern in order
    for pattern, replacement in substitutions:
        sequence = re.sub(pattern, replacement, sequence)
    
    final_length = len(sequence)
    
    # Step 5: Write the three recorded sequence lengths
    print()
    print(initial_length)
    print(cleaned_length)
    print(final_length)


if __name__ == '__main__':
    main()
