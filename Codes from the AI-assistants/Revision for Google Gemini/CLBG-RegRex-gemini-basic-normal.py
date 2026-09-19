import sys
import re

def main():
    # 1. Read all of a redirected FASTA format file from stdin
    #    and record the sequence length
    seq = sys.stdin.read()
    initial_len = len(seq)

    # 2. Use regex pattern match-replace to remove FASTA sequence descriptions 
    #    and all linefeed characters, and record the sequence length
    seq = re.sub(r'>.*\n|\n', '', seq)
    cleaned_len = len(seq)

    # 3. The 9 simple regex patterns for DNA 8-mers and reverse complements
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

    # Count matches in the file, one pattern at a time, and print
    for variant in variants:
        count = len(re.findall(variant, seq))
        print(f"{variant} {count}")

    # 4. The 5 magic regex patterns and their replacements
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')  # Note: Escaped pipe `\|` to match literal character
    ]

    # Match-replace sequentially on the cleaned sequence
    final_seq = seq
    for pattern, replacement in substitutions:
        final_seq = re.sub(pattern, replacement, final_seq)

    # 5. Write the 3 recorded sequence lengths
    print()
    print(initial_len)
    print(cleaned_len)
    print(len(final_seq))

if __name__ == '__main__':
    main()