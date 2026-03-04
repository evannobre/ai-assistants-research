#!/usr/bin/env python3
"""
Regex-Redux Benchmark Implementation
Reads DNA sequence, counts patterns, and performs substitutions using native regex
"""

import re
import sys

def main():
    # Read all input
    input_data = sys.stdin.read()
    initial_len = len(input_data)
    
    # Step 1: Remove sequence descriptions and newlines
    # Keep only the DNA sequence data
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_len = len(sequence)
    
    # Step 2: Count occurrences of specific patterns
    # These are the standard regex-redux patterns
    patterns = [
        r'agggtaaa|tttaccct',
        r'[cgt]gggtaaa|tttaccc[acg]',
        r'a[act]ggtaaa|tttacc[agt]t',
        r'ag[act]gtaaa|tttac[agt]ct',
        r'agg[act]taaa|ttt[agt]cct',
        r'aggg[acg]aaa|ttt[cgt]ccct',
        r'agggt[cgt]aa|tt[acg]accct',
        r'agggta[cgt]a|t[acg]taccct',
        r'agggtaa[cgt]|[acg]ttaccct',
    ]
    
    # Count matches for each pattern
    for pattern in patterns:
        count = len(re.findall(pattern, sequence))
        print(f'{pattern} {count}')
    
    # Step 3: Perform substitutions
    # IUB code replacements
    substitutions = {
        'tHa[Nt]': '<4>',
        'aND|caN|Ha[DS]|WaS': '<3>',
        'a[NSt]|BY': '<2>',
        '<[^>]*>': '|',
        '\\|[^|][^|]*\\|': '-',
    }
    
    result = sequence
    for pattern, replacement in substitutions.items():
        result = re.sub(pattern, replacement, result)
    
    # Step 4: Output lengths
    print()
    print(initial_len)
    print(cleaned_len)
    print(len(result))

if __name__ == '__main__':
    main()
