import sys
import re

def main():
    # Read all input from stdin
    input_data = sys.stdin.read()
    
    # Record the initial length (with descriptions and linefeeds)
    initial_length = len(input_data)
    
    # Remove FASTA sequence descriptions and all linefeed characters
    # 1. Remove lines starting with '>'
    # 2. Remove all newline characters
    sequence = re.sub(r'>.*?\n', '', input_data)
    sequence = re.sub(r'\n', '', sequence)
    
    # Record sequence length after cleanup
    clean_length = len(sequence)
    
    # Define the 8-mer patterns to count
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
    
    # Count matches for each pattern (overlapping matches allowed)
    for pattern in patterns:
        # Count all overlapping matches
        count = len(re.findall(f'(?=({pattern}))', sequence, re.IGNORECASE))
        print(f'{pattern} {count}')
    
    # Magic replacement patterns and their replacements
    magic_patterns = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\\|[^|][^|]*\\|', '-')
    ]
    
    # Apply magic replacements in order
    current = sequence
    for pattern, replacement in magic_patterns:
        current = re.sub(pattern, replacement, current, flags=re.IGNORECASE)
    
    # Record final length after all replacements
    final_length = len(current)
    
    # Print the three recorded lengths
    print(f'\n{initial_length}\n{clean_length}\n{final_length}')

if __name__ == "__main__":
    main()