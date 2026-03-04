import sys
import re

def solve():
    # 1. Read all from stdin
    initial_content = sys.stdin.read()
    initial_length = len(initial_content)

    # 2. Clean FASTA: remove descriptions and linefeeds
    # Sequence descriptions start with '>' and end with a newline
    cleaned_sequence = re.sub(r'>.*\n|\n', '', initial_content)
    cleaned_length = len(cleaned_sequence)

    # 3. 8-mer patterns to count
    variants = [
        'agggtaaa|tttaccct',
        '[cgt]gggtaaa|tttaccc[acg]',
        'a[act]ggtaaa|tttacc[agt]t',
        'ag[act]gtaaa|tttac[agt]ct',
        'agg[act]taaa|ttta[agt]cct',
        'aggg[acg]aaa|ttt[cgt]ccct',
        'agggt[cgt]aa|tt[acg]accct',
        'agggta[cgt]a|t[acg]taccct',
        'agggtaa[cgt]|[acg]ttaccct'
    ]

    for variant in variants:
        count = len(re.findall(variant, cleaned_sequence))
        print(f"{variant} {count}")

    # 4. Magic regex replacements
    # Note: These must be done in order on the same sequence string
    subst = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]

    final_sequence = cleaned_sequence
    for pattern, replacement in subst:
        final_sequence = re.sub(pattern, replacement, final_sequence)

    # 5. Final results
    print(f"\n{initial_length}")
    print(cleaned_length)
    print(len(final_sequence))

if __name__ == "__main__":
    solve()