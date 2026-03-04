import sys
import re

def main():
    # 1. Read all from stdin
    # We read the entire stream into memory as required by the benchmark
    raw_data = sys.stdin.read()
    initial_length = len(raw_data)

    # 2. Remove FASTA descriptions and linefeeds
    # >.*?\n matches the header; \n matches line breaks
    sequence = re.sub(r'>.*?\n|\n', '', raw_data)
    cleaned_length = len(sequence)

    # 3. DNA 8-mer Counting
    # These represent DNA sequences and their reverse complements
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

    for pattern in variants:
        # We count non-overlapping matches as per standard regex-redux rules
        count = len(re.findall(pattern, sequence))
        print(f"{pattern} {count}")

    # 4. Magic Regex Substitutions
    # We perform these sequentially on the SAME sequence string
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]

    final_sequence = sequence
    for pattern, replacement in substitutions:
        final_sequence = re.sub(pattern, replacement, final_sequence)

    # 5. Output results
    print(f"\n{initial_length}")
    print(f"{cleaned_length}")
    print(f"{len(final_sequence)}")

if __name__ == "__main__":
    main()