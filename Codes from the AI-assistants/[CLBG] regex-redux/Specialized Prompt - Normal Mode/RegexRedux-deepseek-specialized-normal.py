import sys
import re
from collections import defaultdict

def main():
    # Read entire input from stdin
    data = sys.stdin.read()
    
    # Record initial sequence length (with descriptions and linefeeds)
    initial_length = len(data)
    
    # Remove FASTA descriptions and linefeeds
    processed = re.sub(r'>.*?\n|\n', '', data)
    processed_length = len(processed)
    
    # Count patterns
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
        count = len(re.findall(pattern, processed))
        counts.append((pattern, count))
    
    # Magic replacements
    magic_patterns = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\\|[^|][^|]*\\|', '-')
    ]
    
    for pattern, replacement in magic_patterns:
        processed = re.sub(pattern, replacement, processed)
    
    final_length = len(processed)
    
    # Output results
    for pattern, count in counts:
        print(f"{pattern} {count}")
    
    print(f"\n{initial_length}\n{processed_length}\n{final_length}")

if __name__ == "__main__":
    main()