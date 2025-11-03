import sys
import re

def solve_regex_redux():
    # 1. Initialization and Input Reading
    fasta_data = sys.stdin.read()
    initial_sequence_length = len(fasta_data)

    # 2. Clean FASTA Data
    # Remove FASTA sequence descriptions
    fasta_data = re.sub(r'^>.*$\n?', '', fasta_data, flags=re.MULTILINE)
    # Remove all linefeed characters
    fasta_data = re.sub(r'\n', '', fasta_data)
    cleaned_sequence_length = len(fasta_data)

    # Define the 8-mer patterns
    regex_patterns_8mers = [
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

    # 3. Count Matches for 8-mer Patterns
    for pattern in regex_patterns_8mers:
        count = len(re.findall(pattern, fasta_data))
        print(f"{pattern} {count}")

    # Define the magic patterns and replacements
    regex_patterns_magic = [
        r'tHa[Nt]',
        r'aND|caN|Ha[DS]|WaS',
        r'a[NSt]|BY',
        r'<[^>]*>',
        r'\\|[^|][^|]*\\|'
    ]
    replacement_strings_magic = [
        '<4>',
        '<3>',
        '<2>',
        '|',
        '-'
    ]

    # 4. Perform Match-Replace for Magic Patterns
    for i in range(len(regex_patterns_magic)):
        pattern = regex_patterns_magic[i]
        replacement = replacement_strings_magic[i]
        fasta_data = re.sub(pattern, replacement, fasta_data)

    final_sequence_length = len(fasta_data)

    # 5. Write Final Sequence Lengths
    print(f"\n{initial_sequence_length}")
    print(f"{cleaned_sequence_length}")
    print(f"{final_sequence_length}")

if __name__ == "__main__":
    solve_regex_redux()