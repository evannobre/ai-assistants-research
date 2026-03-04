import sys
import re
from collections import defaultdict

def main():
    # Read all input from stdin
    data = sys.stdin.read()
    
    # Record original sequence length
    initial_length = len(data)
    
    # 1. Remove FASTA sequence descriptions and all linefeed characters
    # Using the same simple regex pattern match-replace
    # Pattern: remove lines starting with '>' and all newlines
    cleaned = re.sub(r'>.*\n|\n', '', data)
    cleaned_length = len(cleaned)
    
    # Store for later use
    sequence_lower = cleaned.lower()
    
    # 2. Count matches for each pattern (case-insensitive)
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
    
    # Count matches for each pattern
    counts = []
    for pattern in patterns:
        # Count all matches (non-overlapping)
        count = len(re.findall(pattern, sequence_lower))
        counts.append(count)
        print(f"{pattern} {count}")
    
    # 3. Perform the magic replacements on the original data
    # Note: We use the original data (with headers and newlines) for replacements
    magic_patterns = [
        r"tHa[Nt]",
        r"aND|caN|Ha[DS]|WaS",
        r"a[NSt]|BY",
        r"<[^>]*>",
        r"\\|[^|][^|]*\\|"
    ]
    
    magic_replacements = [
        "<4>",
        "<3>",
        "<2>",
        "|",
        "-"
    ]
    
    # Apply replacements sequentially on the original data
    replaced_data = data
    for pattern, replacement in zip(magic_patterns, magic_replacements):
        replaced_data = re.sub(pattern, replacement, replaced_data)
    
    # Remove FASTA headers and newlines from the replaced data
    # (same operation as before)
    final_cleaned = re.sub(r'>.*\n|\n', '', replaced_data)
    final_length = len(final_cleaned)
    
    # 4. Output the three recorded lengths
    print(f"\n{initial_length}")
    print(cleaned_length)
    print(final_length)

if __name__ == "__main__":
    main()