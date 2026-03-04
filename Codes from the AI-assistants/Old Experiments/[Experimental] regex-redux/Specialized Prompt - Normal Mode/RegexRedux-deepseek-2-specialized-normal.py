import sys
import re
from io import StringIO

def chunked_processing(input_file):
    # Process in chunks if memory becomes an issue
    buf = StringIO()
    header_pattern = re.compile(r'>.*\n')
    newline_pattern = re.compile(r'\n')
    
    for line in input_file:
        if not header_pattern.match(line):
            buf.write(newline_pattern.sub('', line))
    return buf.getvalue()

def main():
    seq = chunked_processing(sys.stdin) if False else sys.stdin.read()
    # Rest of the implementation remains the same
    # ...

# Read entire input at once (faster for this benchmark)
    with sys.stdin as f:
        seq = f.read()
    
    # Get original length
    initial_len = len(seq)
    
    # Remove headers and newlines
    seq = re.sub(r'>.*\n|\n', '', seq)
    cleaned_len = len(seq)
    
    # Define pattern variants to count
    variants = [
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
    
    # Count each variant
    counts = {}
    for pattern in variants:
        compiled = re.compile(pattern, re.IGNORECASE)
        counts[pattern] = len(compiled.findall(seq))
    
    # Replacement patterns (pre-compiled for performance)
    replacements = [
        (re.compile(r'tHa[Nt]'), '<4>'),
        (re.compile(r'aND|caN|Ha[DS]|WaS'), '<3>'),
        (re.compile(r'a[NSt]|BY'), '<2>'),
        (re.compile(r'<[^>]*>'), '|'),
        (re.compile(r'\|[^|][^|]*\|'), '-')
    ]
    
    # Apply all replacements sequentially
    for pattern, repl in replacements:
        seq = pattern.sub(repl, seq)
    
    # Output results
    print("\n".join(f"{pattern} {counts[pattern]}" for pattern in variants))
    print(f"\n{initial_len}\n{cleaned_len}\n{len(seq)}")

if __name__ == "__main__":
    main()