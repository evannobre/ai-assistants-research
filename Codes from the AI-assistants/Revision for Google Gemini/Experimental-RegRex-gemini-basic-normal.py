import sys
import re

def solve_regex_redux():
    # 1. Read all input from standard input
    data = sys.stdin.read()
    initial_len = len(data)
    
    # 2. Clean the sequence: remove FASTA headers (>...) and newlines
    # The regex >.*\n|\n efficiently matches both targets in one pass
    cleaned_seq = re.sub(r'>.*\n|\n', '', data)
    cleaned_len = len(cleaned_seq)
    
    # 3. Count variant matches (The 9 regex-redux benchmark patterns)
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
    
    for variant in variants:
        # re.findall returns a list of all non-overlapping matches
        count = len(re.findall(variant, cleaned_seq))
        print(f"{variant} {count}")
        
    # 4. Perform sequential substitutions
    # The replacements inject uppercase characters and symbols to form new targets
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]
    
    mutated_seq = cleaned_seq
    for pattern, replacement in substitutions:
        mutated_seq = re.sub(pattern, replacement, mutated_seq)
        
    final_len = len(mutated_seq)
    
    # 5. Output the required lengths
    print(f"\n{initial_len}\n{cleaned_len}\n{final_len}")

if __name__ == '__main__':
    # Typically executed via command line: python regex_redux.py < input.fasta
    solve_regex_redux()