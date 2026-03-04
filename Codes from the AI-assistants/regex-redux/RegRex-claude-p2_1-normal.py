#!/usr/bin/env python3
"""
Regex-Redux Benchmark
Optimized for multi-core processing using native libraries
"""

import sys
import re
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

# DNA patterns to count
PATTERNS = [
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

# IUB replacement codes
IUB_CODES = [
    (r'tHa[Nt]', '<4>'),
    (r'aND|caN|Ha[DS]|WaS', '<3>'),
    (r'a[NSt]|BY', '<2>'),
    (r'<[^>]*>', '|'),
    (r'\|[^|][^|]*\|', '-'),
]


def count_pattern(args):
    """Count occurrences of a pattern in the sequence"""
    pattern, sequence = args
    return f"{pattern} {len(re.findall(pattern, sequence))}"


def main():
    # Read entire input
    input_data = sys.stdin.read()
    initial_length = len(input_data)
    
    # Remove FASTA description lines and newlines
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(sequence)
    
    # Count patterns in parallel using all CPU cores
    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        # Prepare arguments for parallel processing
        pattern_args = [(pattern, sequence) for pattern in PATTERNS]
        results = executor.map(count_pattern, pattern_args)
    
    # Print pattern counts
    for result in results:
        print(result)
    
    # Perform IUB code replacements sequentially
    # (These are interdependent, so parallel processing isn't beneficial)
    modified_sequence = sequence
    for pattern, replacement in IUB_CODES:
        modified_sequence = re.sub(pattern, replacement, modified_sequence)
    
    # Print sequence lengths
    print()
    print(initial_length)
    print(cleaned_length)
    print(len(modified_sequence))


if __name__ == '__main__':
    main()