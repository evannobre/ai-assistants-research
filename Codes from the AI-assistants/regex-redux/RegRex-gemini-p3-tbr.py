import sys
import re

def main():
    # 1. Read all of a redirected FASTA format file from stdin
    # Reading binary ensures we handle any encoding issues gracefully, 
    # though standard FASTA is ASCII. We decode to string for regex.
    data = sys.stdin.read()
    
    # Record the sequence length (Length 1)
    initial_len = len(data)

    # 2. Remove FASTA sequence descriptions and all linefeed characters
    # Pattern explanation: 
    #   >.*\n : Matches line starting with > up to the newline (header)
    #   |\n   : OR matches any newline character
    data = re.sub(r'>.*\n|\n', '', data)
    
    # Record the sequence length (Length 2)
    cleaned_len = len(data)

    # 3. Count matches for the DNA 8-mer patterns
    # These represent DNA 8-mers and their reverse complements
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

    for pattern in variants:
        # re.findall returns a list of all non-overlapping matches
        count = len(re.findall(pattern, data))
        print(f"{pattern} {count}")

    # 4. Perform Magic Replacements
    # We map specific patterns to IUB code lengths or symbols
    # Note: Python's re.sub takes the pattern, replacement, and string
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]

    for pattern, replacement in substitutions:
        data = re.sub(pattern, replacement, data)

    # Record the sequence length (Length 3)
    final_len = len(data)

    # 5. Write the 3 recorded sequence lengths
    print(f"\n{initial_len}")
    print(f"{cleaned_len}")
    print(f"{final_len}")

if __name__ == "__main__":
    main()