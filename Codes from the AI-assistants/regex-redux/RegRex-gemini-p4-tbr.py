import sys
import re
from multiprocessing import Pool, cpu_count

# Global variable to hold the clean sequence for workers
# This leverages Linux Copy-on-Write (COW) to avoid pickling 
# large strings across processes.
SEQUENCE = ""

def count_pattern(pattern_string):
    """
    Worker function to count matches of a specific regex pattern.
    """
    # Using re.findall is generally faster than finditer for simple counts 
    # in Python due to C-level optimization, provided memory is sufficient.
    return len(re.findall(pattern_string, SEQUENCE))

def main():
    global SEQUENCE
    
    # 1. Read all of a redirected FASTA format file from stdin
    # We read as bytes first for efficiency, then decode, or read as text.
    # Standard Python strings (unicode) are required for regex-redux logic usually.
    raw_input = sys.stdin.read()
    initial_len = len(raw_input)

    # 2. Remove FASTA sequence descriptions and newlines
    # Pattern: >.*\n|\n
    # We explicitly compile regexes for clarity and potential reuse speedup
    cleanup_pattern = re.compile(r'>.*\n|\n')
    SEQUENCE = cleanup_pattern.sub('', raw_input)
    clean_len = len(SEQUENCE)

    # Free up the memory of the raw input immediately
    del raw_input

    # 3. Define the counting patterns
    # These represent DNA 8-mers and their reverse complement
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

    # 4. Execute Parallel Counting
    # We use a Pool to distribute the regex counting across available CPU cores.
    # Note: We do NOT pass SEQUENCE as an argument to avoid serialization overhead.
    with Pool(processes=cpu_count()) as pool:
        # map_async allows the main process to continue doing the replacement work
        # while the workers count patterns.
        results_async = pool.map_async(count_pattern, variants)
        
        # 5. Perform the "Magic" Replacements (Sequential)
        # This runs in the main process while the pool handles the counting.
        # We work on a copy or let the logic replace strictly. 
        # Since we need the length AFTER all replacements, we do this on a new variable 
        # or the existing one. However, the workers are reading 'SEQUENCE'. 
        # Therefore, we must perform replacements on a variable that does not 
        # interfere with the global 'SEQUENCE' being read by workers.
        
        # We create a local reference for manipulation.
        # Since strings are immutable in Python, 'replaced_seq = SEQUENCE' 
        # and subsequent operations creates new strings, preserving the 
        # global 'SEQUENCE' for the workers.
        replaced_seq = SEQUENCE
        
        substitutions = [
            (r'tHa[Nt]', '<4>'),
            (r'aND|caN|Ha[DS]|WaS', '<3>'),
            (r'a[NSt]|BY', '<2>'),
            (r'<[^>]*>', '|'),
            (r'\|[^|][^|]*\|', '-')
        ]

        for pattern, replacement in substitutions:
            # We assume the pattern is simple enough that compilation 
            # overhead is negligible, but clean code suggests:
            replaced_seq = re.sub(pattern, replacement, replaced_seq)

        final_len = len(replaced_seq)
        
        # Retrieve counting results
        counts = results_async.get()

    # 6. Output Results
    # Print pattern counts
    for variant, count in zip(variants, counts):
        print(f"{variant} {count}")

    # Print lengths
    print(f"\n{initial_len}")
    print(f"{clean_len}")
    print(f"{final_len}")

if __name__ == '__main__':
    main()