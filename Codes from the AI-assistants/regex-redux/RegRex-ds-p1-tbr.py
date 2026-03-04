# Using Python as example, but algorithm applies to any language with regex support

import sys, re

def regex_redux():
    # 1. Read and process input
    data = sys.stdin.read()
    
    # Extract DNA sequence (remove FASTA header and newlines)
    sequence = "".join(data.split("\n")[1:]).replace("\n", "")
    
    # Store original sequence length
    initial_length = len(sequence)
    
    # 2. Count patterns using native regex (regex variations for different languages)
    variants = [
        "agggtaaa|tttaccct",          # Pattern 1
        "[cgt]gggtaaa|tttaccc[acg]",  # Pattern 2
        "a[act]ggtaaa|tttacc[agt]t",  # Pattern 3
        "ag[act]gtaaa|tttac[agt]ct",  # Pattern 4
        "agg[act]taaa|ttta[agt]cct",  # Pattern 5
        "aggg[acg]aaa|ttt[cgt]ccct",  # Pattern 6
        "agggt[cgt]aa|tt[acg]accct",  # Pattern 7
        "agggta[cgt]a|t[acg]taccct",  # Pattern 8
        "agggtaa[cgt]|[acg]ttaccct"   # Pattern 9
    ]
    
    # Count occurrences of each pattern
    counts = {}
    for variant in variants:
        # Use native regex engine - compile pattern for better performance
        pattern = re.compile(variant, re.IGNORECASE)
        counts[variant] = len(pattern.findall(sequence))
    
    # 3. Perform IUB code replacements using chained replacements
    # Optimization: Use single-pass replacement where possible
    replacements = [
        (r"B", r"(c|g|t)"),
        (r"D", r"(a|g|t)"),
        (r"H", r"(a|c|t)"),
        (r"K", r"(g|t)"),
        (r"M", r"(a|c)"),
        (r"N", r"(a|c|g|t)"),
        (r"R", r"(a|g)"),
        (r"S", r"(c|g)"),
        (r"V", r"(a|c|g)"),
        (r"W", r"(a|t)"),
        (r"Y", r"(c|t)")
    ]
    
    # Apply replacements
    for code, replacement in replacements:
        pattern = re.compile(code, re.IGNORECASE)
        sequence = pattern.sub(replacement, sequence)
    
    # 4. Output results
    for variant in variants:
        print(f"{variant} {counts[variant]}")
    
    print(f"\n{initial_length}")
    print(len(sequence))

# Alternative: More efficient replacement using single pass
def efficient_replacements(text):
    # Use a single compiled regex with callback for better performance
    replacement_map = {
        'B': '(c|g|t)', 'D': '(a|g|t)', 'H': '(a|c|t)',
        'K': '(g|t)', 'M': '(a|c)', 'N': '(a|c|g|t)',
        'R': '(a|g)', 'S': '(c|g)', 'V': '(a|c|g)',
        'W': '(a|t)', 'Y': '(c|t)'
    }
    
    # Create a single pattern matching any IUB code
    pattern = re.compile(r'[BDHKMNRSVWY]', re.IGNORECASE)
    
    def replace_match(match):
        return replacement_map[match.group().upper()]
    
    return pattern.sub(replace_match, text)