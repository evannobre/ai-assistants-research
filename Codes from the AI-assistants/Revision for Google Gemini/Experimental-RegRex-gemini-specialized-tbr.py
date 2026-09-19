import sys
import re
from concurrent.futures import ThreadPoolExecutor

def count_matches(pattern_string, text):
    """
    Finds and counts all non-overlapping matches for a given regex pattern.
    Executed concurrently by worker threads.
    """
    pattern = re.compile(pattern_string, re.IGNORECASE)
    return pattern_string, len(pattern.findall(text))

def main():
    # 1. In-Memory I/O
    # Reads the entire FASTA payload directly into RAM.
    seq = sys.stdin.read()
    initial_length = len(seq)

    # 2. Data Cleaning
    # Strips out the FASTA descriptions (lines starting with '>') and all line breaks.
    seq = re.sub(r'>.*?\n|\n', '', seq)
    cleaned_length = len(seq)

    # 3. Concurrent Counting (Read-Only Phase)
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

    # Spin up a thread pool. The 're' C-extension releases the GIL, 
    # giving us true multi-threading for pattern matching without 
    # duplicating the 'seq' string in our 8 GB RAM space.
    with ThreadPoolExecutor() as executor:
        # Map the counting function to the patterns
        futures = [executor.submit(count_matches, var, seq) for var in variants]
        
        # Ensure results print in the exact order the benchmark expects
        for future in futures:
            pattern, count = future.result()
            print(f"{pattern} {count}")

    # 4. Sequential Replacements (Mutation Phase)
    # Reassigning 'seq' ensures the old string buffers are flagged for garbage collection.
    substitutions = [
        (r'tHa[Nt]', '<4>'),
        (r'aND|caN|Ha[DS]|WaS', '<3>'),
        (r'a[NSt]|BY', '<2>'),
        (r'<[^>]*>', '|'),
        (r'\|[^|][^|]*\|', '-')
    ]

    for pattern, replacement in substitutions:
        seq = re.sub(pattern, replacement, seq)

    # 5. Output Checksums
    print(f"\n{initial_length}")
    print(f"{cleaned_length}")
    print(len(seq))

if __name__ == '__main__':
    main()