#!/usr/bin/env python3
"""
Regex Redux Algorithm Implementation
Uses native Python libraries for maximum performance
"""

import re
import sys
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

def regex_redux_solution():
    # Read input from stdin
    input_data = sys.stdin.read()
    
    # Store original length
    original_length = len(input_data)
    
    # Step 1: Remove sequence descriptions and newlines
    # This regex removes FASTA sequence descriptions (lines starting with '>') and newlines
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(sequence)
    
    # Step 2: Define regex patterns to count
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
    
    # Step 3: Count pattern matches using multiprocessing for performance
    def count_pattern(pattern):
        return len(re.findall(pattern, sequence, re.IGNORECASE))
    
    # Use ThreadPoolExecutor for I/O bound regex operations
    with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
        counts = list(executor.map(count_pattern, patterns))
    
    # Step 4: Define replacement patterns
    replacements = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    # Step 5: Apply replacements sequentially
    result_sequence = sequence
    for pattern, replacement in replacements:
        result_sequence = re.sub(pattern, replacement, result_sequence, flags=re.IGNORECASE)
    
    final_length = len(result_sequence)
    
    # Output results
    for i, (pattern, count) in enumerate(zip(patterns, counts)):
        print(f"{pattern} {count}")
    
    print(f"\n{original_length}")
    print(f"{cleaned_length}")
    print(f"{final_length}")

def optimized_regex_redux():
    """
    Optimized version with pre-compiled patterns and memory-efficient processing
    """
    input_data = sys.stdin.read()
    original_length = len(input_data)
    
    # Pre-compile regex patterns for better performance
    cleanup_pattern = re.compile(r'>.*\n|\n')
    sequence = cleanup_pattern.sub('', input_data)
    cleaned_length = len(sequence)
    
    # Pre-compile counting patterns
    count_patterns = [
        re.compile(r'agggtaaa|tttaccct', re.IGNORECASE),
        re.compile(r'[cgt]gggtaaa|tttaccc[acg]', re.IGNORECASE),
        re.compile(r'a[act]ggtaaa|tttacc[agt]t', re.IGNORECASE),
        re.compile(r'ag[act]gtaaa|tttac[agt]ct', re.IGNORECASE),
        re.compile(r'agg[act]taaa|ttta[agt]cct', re.IGNORECASE),
        re.compile(r'aggg[acg]aaa|ttt[cgt]ccct', re.IGNORECASE),
        re.compile(r'agggt[cgt]aa|tt[acg]accct', re.IGNORECASE),
        re.compile(r'agggta[cgt]a|t[acg]taccct', re.IGNORECASE),
        re.compile(r'agggtaa[cgt]|[acg]ttaccct', re.IGNORECASE)
    ]
    
    # Count patterns using list comprehension for efficiency
    counts = [len(pattern.findall(sequence)) for pattern in count_patterns]
    
    # Pre-compile replacement patterns
    replacement_patterns = [
        (re.compile(r'tHa[Nt]', re.IGNORECASE), '<4>'),
        (re.compile(r'aND|caN|Ha[DS]|WaS', re.IGNORECASE), '<3>'),
        (re.compile(r'a[NSt]|BY', re.IGNORECASE), '<2>'),
        (re.compile(r'<[^>]*>'), '|'),
        (re.compile(r'\|[^|][^|]*\|'), '-')
    ]
    
    # Apply replacements with compiled patterns
    result_sequence = sequence
    for pattern, replacement in replacement_patterns:
        result_sequence = pattern.sub(replacement, result_sequence)
    
    final_length = len(result_sequence)
    
    # Output results
    pattern_strings = [
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
    
    for pattern_str, count in zip(pattern_strings, counts):
        print(f"{pattern_str} {count}")
    
    print(f"\n{original_length}")
    print(f"{cleaned_length}")
    print(f"{final_length}")

def memory_efficient_regex_redux():
    """
    Memory-efficient version for very large inputs
    """
    import mmap
    
    # For very large files, use memory mapping
    with open(0, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            input_data = mmapped_file.read().decode('utf-8')
    
    original_length = len(input_data)
    
    # Process in chunks if needed for extremely large datasets
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(sequence)
    
    # Use generator expressions for memory efficiency
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
    
    counts = []
    for pattern in patterns:
        count = len(re.findall(pattern, sequence, re.IGNORECASE))
        counts.append(count)
        print(f"{pattern} {count}")
    
    # Apply replacements
    replacements = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    result_sequence = sequence
    for pattern, replacement in replacements:
        result_sequence = re.sub(pattern, replacement, result_sequence, re.IGNORECASE)
    
    final_length = len(result_sequence)
    
    print(f"\n{original_length}")
    print(f"{cleaned_length}")
    print(f"{final_length}")

if __name__ == "__main__":
    # Choose the implementation based on your needs:
    # optimized_regex_redux()        # Best for most cases
    # memory_efficient_regex_redux() # For very large inputs
    # regex_redux_solution()         # Basic implementation with multiprocessing
    
    optimized_regex_redux()