#!/usr/bin/env python3
"""
regex-redux simulation implementation
Uses native Python libraries and follows the exact algorithm specification
"""

import sys
import re
from io import StringIO

def read_stdin():
    """Read all input from stdin"""
    return sys.stdin.read()

def main():
    # Read all input
    data = read_stdin()
    
    # Record initial sequence length
    initial_len = len(data)
    
    # 1. Remove FASTA sequence descriptions and linefeeds
    # Pattern to remove FASTA headers (lines starting with '>')
    data = re.sub(r'>.*\n', '', data)
    # Remove linefeed characters
    data = re.sub(r'\n', '', data)
    
    # Record sequence length after cleanup
    clean_len = len(data)
    
    # 2. Count matches for each DNA pattern
    patterns = [
        r"agggtaaa|tttaccct",
        r"[cgt]gggtaaa|tttaccc[acg]",
        r"a[act]ggtaaa|tttacc[agt]t",
        r"ag[act]gtaaa|tttac[agt]ct",
        r"agg[act]taaa|ttta[agt]cct",
        r"aggg[acg]aaa|ttt[cgt]ccct",
        r"agggt[cgt]aa|tt[acg]accct",
        r"agggta[cgt]a|t[acg]taccct",
        r"agggtaa[cgt]|[acg]ttaccct"
    ]
    
    # Count and write pattern matches
    for pattern in patterns:
        count = len(re.findall(pattern, data))
        print(f"{pattern} {count}")
    
    # 3. Apply replacement patterns
    # Make a copy for replacements
    processed = data
    
    # Define replacement patterns and their replacements
    replacement_patterns = [
        (r"tHa[Nt]", "<4>"),
        (r"aND|caN|Ha[DS]|WaS", "<3>"),
        (r"a[NSt]|BY", "<2>"),
        (r"<[^>]*>", "|"),
        (r"\\|[^|][^|]*\\|", "-")
    ]
    
    # Apply replacements one at a time
    for pattern, replacement in replacement_patterns:
        processed = re.sub(pattern, replacement, processed)
    
    # Record final sequence length
    final_len = len(processed)
    
    # Write the 3 recorded sequence lengths
    print(f"\n{initial_len}\n{clean_len}\n{final_len}")

def generate_test_file():
    """
    Helper function to generate test FASTA data
    Usage: python script.py 5000000 > input5000000.txt
    """
    import random
    
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
            
            # FASTA header
            print(">ONE Homo sapiens alu")
            
            # Define DNA bases
            bases = ['a', 'c', 'g', 't']
            
            # Write DNA sequence
            chars_written = 0
            line_length = 60
            
            while chars_written < n:
                line_chars = min(line_length, n - chars_written)
                line = ''.join(random.choice(bases) for _ in range(line_chars))
                print(line)
                chars_written += line_chars
                
        except ValueError:
            print("Usage: python script.py <sequence_length>")
            sys.exit(1)

if __name__ == "__main__":
    # Check if we should generate test data
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        generate_test_file()
    else:
        main()