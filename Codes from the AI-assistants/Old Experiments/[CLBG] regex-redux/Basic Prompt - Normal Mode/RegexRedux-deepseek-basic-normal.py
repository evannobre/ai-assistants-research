import sys
import re

def main():
    # Read all input
    data = sys.stdin.read()
    
    # Record initial length
    initial_len = len(data)
    
    # Remove FASTA headers and newlines
    cleaned = re.sub(r'>.*?\n|\n', '', data)
    cleaned_len = len(cleaned)
    
    # DNA patterns to count
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
    
    # Count each pattern
    counts = []
    for pattern in patterns:
        count = len(re.findall(pattern, cleaned))
        print(pattern, count)
    
    # Magic replacements
    transformations = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\\|[^|][^|]*\\|', '-')
    ]
    
    transformed = cleaned
    for pattern, repl in transformations:
        transformed = re.sub(pattern, repl, transformed)
    final_len = len(transformed)
    
    # Output lengths
    print(f"\n{initial_len}\n{cleaned_len}\n{final_len}")

if __name__ == "__main__":
    main()