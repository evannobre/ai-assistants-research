#!/usr/bin/env python3
"""
Regex-Redux DNA Sequence Processor
Optimized for performance using native Python libraries
"""

import sys
import re
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp


# DNA variant patterns to search for
VARIANTS = [
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

# Substitution patterns for IUB code
SUBSTITUTIONS = {
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


def count_pattern(args):
    """
    Count matches for a single pattern in the sequence.
    Used for parallel processing.
    
    Args:
        args: Tuple of (pattern, sequence)
    
    Returns:
        Tuple of (pattern, count)
    """
    pattern, seq = args
    return pattern, len(re.findall(pattern, seq))


def main():
    """
    Main algorithm for regex-redux benchmark:
    1. Read and clean input (remove FASTA headers and newlines)
    2. Count variant patterns in parallel
    3. Perform IUB code substitutions
    4. Report sequence lengths
    """
    
    # Step 1: Read entire input efficiently
    # Using sys.stdin.read() is faster than readlines() for large inputs
    input_data = sys.stdin.read()
    initial_length = len(input_data)
    
    # Step 2: Remove FASTA description lines and newlines
    # Compile regex once for efficiency
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(sequence)
    
    # Step 3: Count variant patterns in parallel
    # Use number of CPU cores for optimal parallelization
    # Create list of tasks for the process pool
    tasks = [(pattern, sequence) for pattern in VARIANTS]
    
    # Process patterns in parallel using all available cores
    # This significantly speeds up the search on multi-core systems
    cpu_count = mp.cpu_count()
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        results = executor.map(count_pattern, tasks)
    
    # Print pattern match counts
    for pattern, count in results:
        print(f'{pattern} {count}')
    
    # Step 4: Perform substitutions sequentially
    # Note: Substitutions are done sequentially as they depend on previous results
    # and the sequence needs to be modified in a specific order
    result_sequence = sequence
    
    # Compile all substitution patterns once for efficiency
    compiled_subs = [(re.compile(key), value) 
                     for key, value in SUBSTITUTIONS.items()]
    
    # Apply each substitution to the result sequence
    for pattern, replacement in compiled_subs:
        result_sequence = pattern.sub(replacement, result_sequence)
    
    final_length = len(result_sequence)
    
    # Step 5: Report results
    print()
    print(initial_length)
    print(cleaned_length)
    print(final_length)


if __name__ == '__main__':
    # Set recursion limit if needed for very large sequences
    sys.setrecursionlimit(10**6)
    main()
