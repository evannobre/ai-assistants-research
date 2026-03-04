#!/usr/bin/env python3
"""
Memory-optimized version for very large FASTA files
"""

import sys
import re

def process_large_fasta():
    # Compile patterns once
    header_pattern = re.compile(r'>.*\n')
    linefeed_pattern = re.compile(r'\n')
    
    # DNA counting patterns
    dna_patterns = [
        (re.compile(r"agggtaaa|tttaccct"), "agggtaaa|tttaccct"),
        (re.compile(r"[cgt]gggtaaa|tttaccc[acg]"), "[cgt]gggtaaa|tttaccc[acg]"),
        (re.compile(r"a[act]ggtaaa|tttacc[agt]t"), "a[act]ggtaaa|tttacc[agt]t"),
        (re.compile(r"ag[act]gtaaa|tttac[agt]ct"), "ag[act]gtaaa|tttac[agt]ct"),
        (re.compile(r"agg[act]taaa|ttta[agt]cct"), "agg[act]taaa|ttta[agt]cct"),
        (re.compile(r"aggg[acg]aaa|ttt[cgt]ccct"), "aggg[acg]aaa|ttt[cgt]ccct"),
        (re.compile(r"agggt[cgt]aa|tt[acg]accct"), "agggt[cgt]aa|tt[acg]accct"),
        (re.compile(r"agggta[cgt]a|t[acg]taccct"), "agggta[cgt]a|t[acg]taccct"),
        (re.compile(r"agggtaa[cgt]|[acg]ttaccct"), "agggtaa[cgt]|[acg]ttaccct")
    ]
    
    # Replacement patterns
    replacement_patterns = [
        (re.compile(r"tHa[Nt]"), "<4>"),
        (re.compile(r"aND|caN|Ha[DS]|WaS"), "<3>"),
        (re.compile(r"a[NSt]|BY"), "<2>"),
        (re.compile(r"<[^>]*>"), "|"),
        (re.compile(r"\\|[^|][^|]*\\|"), "-")
    ]
    
    # Read and process in chunks
    buffer = []
    total_len = 0
    clean_data = []
    clean_len = 0
    
    # First pass: remove headers and linefeeds, count initial length
    for line in sys.stdin:
        total_len += len(line)
        if line.startswith('>'):
            continue
        clean_line = line.rstrip('\n')
        clean_data.append(clean_line)
        clean_len += len(clean_line)
    
    # Combine cleaned data
    data = ''.join(clean_data)
    
    # Count DNA patterns
    for pattern, pattern_str in dna_patterns:
        count = len(pattern.findall(data))
        print(f"{pattern_str} {count}")
    
    # Apply replacements
    processed = data
    for pattern, replacement in replacement_patterns:
        processed = pattern.sub(replacement, processed)
    
    final_len = len(processed)
    
    print(f"\n{total_len}\n{clean_len}\n{final_len}")

if __name__ == "__main__":
    process_large_fasta()