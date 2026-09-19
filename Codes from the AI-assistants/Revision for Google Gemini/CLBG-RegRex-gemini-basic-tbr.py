import sys
import re
from multiprocessing import Pool

def count_matches(args):
    """
    Counts the occurrences of a regex pattern in the sequence.
    Using finditer is more memory efficient than findall.
    """
    pattern, sequence = args
    count = sum(1 for _ in re.finditer(pattern, sequence))
    return f"{pattern} {count}"

def main():
    # 1. Read all of a redirected FASTA format file from stdin
    seq = sys.stdin.read()
    
    # Record the initial sequence length
    initial_len = len(seq)
    
    # 2. Use match-replace to remove FASTA sequence descriptions and linefeeds
    # >.* matches the description lines, \n matches the linefeed characters
    seq = re.sub(r'>.*|\n', '', seq)
    
    # Record the cleaned sequence length
    cleaned_len = len(seq)
    
    # 3. DNA 8-mers and their reverse complement patterns to count
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
    
    # Execute the counting in parallel to improve performance 
    with Pool() as pool:
        # Map the count_matches function to our patterns and the cleaned sequence
        results = pool.map(count_matches, [(pat, seq) for pat in variants])
        
    # 4. Write the regex pattern and count
    for result in results:
        print(result)
        
    # 5. Use the same magic regex patterns to match-replace sequentially
    # Note: These MUST be done sequentially, as each replacement acts upon 
    # the modified string from the previous step.
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')  # Escaped pipes to match literal '|'
    ]
    
    for pattern, replacement in substitutions:
        seq = re.sub(pattern, replacement, seq)
        
    # Record the final sequence length
    final_len = len(seq)
    
    # 6. Write the 3 recorded sequence lengths
    print()
    print(initial_len)
    print(cleaned_len)
    print(final_len)

if __name__ == '__main__':
    main()