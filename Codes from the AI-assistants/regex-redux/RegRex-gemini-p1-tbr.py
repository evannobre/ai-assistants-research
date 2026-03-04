import sys
import re
from multiprocessing import Pool

# 1. Define the regex patterns required by the benchmark
VARIANTS = [
    r'agggtaaa|tttaccct',
    r'[cgt]gggtaaa|tttaccc[acg]',
    r'a[act]ggtaaa|tttacc[agt]t',
    r'ag[act]gtaaa|tttac[agt]ct',
    r'agg[act]taaa|ttta[agt]cct',
    r'aggg[acg]aaa|ttt[cgt]ccct',
    r'agggt[cgt]aa|tt[acg]accct',
    r'agggta[cgt]a|t[acg]taccct',
    r'agggtaa[cgt]|[acg]ttaccct',
]

SUBSTITUTIONS = [
    (r'tHa[Nt]', '<4>'),
    (r'aND|caN|Ha[DS]|WaS', '<3>'),
    (r'a[NSt]|BY', '<2>'),
    (r'<[^>]*>', '|'),
    (r'\|[^|][^|]*\|', '-'),
]

def count_pattern(args):
    """
    Worker function to count matches of a pattern in the sequence.
    Arguments are passed as a tuple to satisfy Pool.map requirements.
    """
    pattern, sequence = args
    # We use findall to count non-overlapping occurrences
    return len(re.findall(pattern, sequence))

def main():
    # 2. Read Input
    # Reading from stdin as bytes to handle potential encoding issues gracefully,
    # though strictly the benchmark implies ASCII/UTF-8 compatible DNA data.
    data = sys.stdin.read()
    initial_len = len(data)

    # 3. Remove FASTA headers and newlines
    # Pattern: > followed by anything until newline, OR a newline character
    # We replace these with an empty string.
    seq = re.sub(r'>.*\n|\n', '', data)
    cleaned_len = len(seq)

    # 4. Parallel Counting
    # We pair every pattern with the sequence to pass to the workers
    pool_args = [(pattern, seq) for pattern in VARIANTS]
    
    # Create a pool of workers equal to the number of CPU cores
    with Pool() as pool:
        # map guarantees the order of results matches the order of inputs
        results = pool.map(count_pattern, pool_args)

    # Print the counts immediately as required by the benchmark output format
    for pattern, count in zip(VARIANTS, results):
        print(f"{pattern} {count}")

    # 5. Sequential Substitution
    # These must be done in order, as each substitution alters the sequence
    # for the next one.
    processed_seq = seq
    for pattern, replacement in SUBSTITUTIONS:
        processed_seq = re.sub(pattern, replacement, processed_seq)
    
    final_len = len(processed_seq)

    # 6. Final Output
    print(f"\n{initial_len}")
    print(f"{cleaned_len}")
    print(f"{final_len}")

if __name__ == '__main__':
    main()