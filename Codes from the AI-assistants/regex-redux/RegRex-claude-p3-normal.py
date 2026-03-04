#!/usr/bin/env python3
"""
regex-redux: Pattern matching and replacement on FASTA format data
Uses native Python re library for regex operations
"""

import sys
import re


def main():
    # Read all input from stdin
    input_data = sys.stdin.read()
    
    # Record initial sequence length
    initial_length = len(input_data)
    
    # Remove FASTA sequence descriptions (lines starting with >) and linefeeds
    # Pattern matches description lines and newlines
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    
    # Record cleaned sequence length
    cleaned_length = len(sequence)
    
    # Define the 9 variant patterns to count
    # These represent DNA 8-mers and their reverse complements with wildcards
    variant_patterns = [
        'agggtaaa|tttaccct',
        '[cgt]gggtaaa|tttaccc[acg]',
        'a[act]ggtaaa|tttacc[agt]t',
        'ag[act]gtaaa|tttac[agt]ct',
        'agg[act]taaa|ttta[agt]cct',
        'aggg[acg]aaa|ttt[cgt]ccct',
        'agggt[cgt]aa|tt[acg]accct',
        'agggta[cgt]a|t[acg]taccct',
        'agggtaa[cgt]|[acg]ttaccct'
    ]
    
    # Count matches for each variant pattern
    for pattern in variant_patterns:
        count = len(re.findall(pattern, sequence))
        print(f"{pattern} {count}")
    
    # Define magic patterns and their replacements
    # These perform IUB code substitutions
    magic_substitutions = [
        ('tHa[Nt]', '<4>'),
        ('aND|caN|Ha[DS]|WaS', '<3>'),
        ('a[NSt]|BY', '<2>'),
        ('<[^>]*>', '|'),
        ('\\|[^|][^|]*\\|', '-')
    ]
    
    # Apply each substitution in order
    modified_sequence = sequence
    for pattern, replacement in magic_substitutions:
        modified_sequence = re.sub(pattern, replacement, modified_sequence)
    
    # Record final sequence length
    final_length = len(modified_sequence)
    
    # Write the three recorded sequence lengths
    print()
    print(initial_length)
    print(cleaned_length)
    print(final_length)


if __name__ == '__main__':
    main()
