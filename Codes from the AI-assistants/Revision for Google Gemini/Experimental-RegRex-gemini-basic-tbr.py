import sys
import re
from multiprocessing import Pool

# 1. Define the counting function at the module level for parallel processing.
# We use re.finditer() which is highly memory efficient since it yields 
# match objects as an iterator rather than building a massive list in memory.
def count_pattern(args):
    pattern, sequence = args
    count = sum(1 for _ in re.finditer(pattern, sequence))
    return pattern, count

def main():
    # 2. Read and Measure Input
    # Read the entire block from standard input using native sys module
    seq = sys.stdin.read()
    initial_length = len(seq)

    # 3. Clean the Sequence
    # Remove FASTA headers and newlines
    seq = re.sub(r'>.*\n|\n', '', seq)
    cleaned_length = len(seq)

    # 4. Count Variant Patterns
    # These are the standard regex-redux benchmark patterns
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

    # Map the counting task across available CPU cores natively
    with Pool() as pool:
        results = pool.map(count_pattern, [(pat, seq) for pat in variants])

    for pattern, count in results:
        print(f"{pattern} {count}")

    # 5. Apply Substitutions
    # These must be applied sequentially
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]

    final_seq = seq
    for pattern, replacement in substitutions:
        final_seq = re.sub(pattern, replacement, final_seq)

    # 6. Report Results
    print()
    print(initial_length)
    print(cleaned_length)
    print(len(final_seq))

if __name__ == '__main__':
    main()