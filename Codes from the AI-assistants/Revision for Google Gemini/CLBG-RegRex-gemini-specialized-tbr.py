import sys
import re
from concurrent.futures import ProcessPoolExecutor

def count_matches(args):
    """
    Worker function to count regex matches.
    Using finditer is more memory-efficient than findall because it 
    yields match objects instead of allocating a list of large strings.
    """
    pattern, sequence = args
    count = sum(1 for _ in re.finditer(pattern, sequence))
    return pattern, count

def main():
    # 1. Read all redirected FASTA format file from stdin
    stdin_data = sys.stdin.read()
    initial_len = len(stdin_data)

    # 2. Use simple regex to remove FASTA descriptions and linefeeds
    # '>' followed by anything up to a newline, OR just a newline.
    cleaned_seq = re.sub(r'>.*\n|\n', '', stdin_data)
    cleaned_len = len(cleaned_seq)

    # 3. Simple regex patterns for DNA 8-mers counting
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

    # Map the counting task across available CPU cores. 
    # On Ubuntu, ProcessPoolExecutor uses fork(), so the memory footprint 
    # remains exceptionally light (copy-on-write).
    with ProcessPoolExecutor() as executor:
        args = [(var, cleaned_seq) for var in variants]
        results = executor.map(count_matches, args)

    # 4. Write the regex pattern and count
    for pattern, count in results:
        print(f"{pattern} {count}")

    # 5. Magic regex patterns for sequential match-replace
    magic_patterns = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')  # Escaped pipe character matching
    ]

    # Perform sequential replacements
    final_seq = cleaned_seq
    for pattern, replacement in magic_patterns:
        final_seq = re.sub(pattern, replacement, final_seq)

    final_len = len(final_seq)

    # 6. Write the 3 recorded sequence lengths
    print()
    print(initial_len)
    print(cleaned_len)
    print(final_len)

if __name__ == '__main__':
    main()