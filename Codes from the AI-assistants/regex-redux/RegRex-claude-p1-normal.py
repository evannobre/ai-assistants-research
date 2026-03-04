#!/usr/bin/env python3
"""
Regex-Redux Benchmark Implementation
Using Python's native 're' module for maximum performance
"""

import sys
import re

def main():
    # Step 1: Read all input
    input_data = sys.stdin.read()
    initial_length = len(input_data)
    
    # Step 2: Remove comments and newlines
    # Pattern matches lines starting with '>' (headers) and newlines
    cleaned = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(cleaned)
    
    # Step 3: Count pattern occurrences
    # These are the standard DNA sequence patterns to search for
    patterns = [
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
    
    # Count and print pattern matches
    for pattern in patterns:
        count = len(re.findall(pattern, cleaned))
        print(f'{pattern} {count}')
    
    # Step 4: Perform IUB code replacements
    # Define replacement map for IUB ambiguity codes
    iub_codes = {
        'B': '(c|g|t)',
        'D': '(a|g|t)',
        'H': '(a|c|t)',
        'K': '(g|t)',
        'M': '(a|c)',
        'N': '(a|c|g|t)',
        'R': '(a|g)',
        'S': '(c|g)',
        'V': '(a|c|g)',
        'W': '(a|t)',
        'Y': '(c|t)',
    }
    
    # Apply all replacements
    result = cleaned
    for code, replacement in iub_codes.items():
        result = re.sub(code, replacement, result)
    
    # Step 5: Print length statistics
    print()
    print(initial_length)
    print(cleaned_length)
    print(len(result))

if __name__ == '__main__':
    main()
