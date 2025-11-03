import sys
import re

def main():
    # Read entire input
    input_data = sys.stdin.read()
    initial_length = len(input_data)

    # Remove FASTA headers and line breaks
    sequence = re.sub(r'>.*\n|\n', '', input_data)
    sequence_length = len(sequence)

    # Patterns to count
    regex_patterns = [
        "agggtaaa|tttaccct",
        "[cgt]gggtaaa|tttaccc[acg]",
        "a[act]ggtaaa|tttacc[agt]t",
        "ag[act]gtaaa|tttac[agt]ct",
        "agg[act]taaa|ttta[agt]cct",
        "aggg[acg]aaa|ttt[cgt]ccct",
        "agggt[cgt]aa|tt[acg]accct",
        "agggta[cgt]a|t[acg]taccct",
        "agggtaa[cgt]|[acg]ttaccct",
    ]

    for pattern in regex_patterns:
        count = len(re.findall(pattern, sequence, flags=re.IGNORECASE))
        print(f"{pattern} {count}")

    # Substitution map (IUB ambiguity codes)
    substitutions = {
        'B': '(c|g|t)',
        'D': '(a|g|t)',
        'H': '(a|c|t)',
        'K': '(g|t)',
        'M': '(a|c)',
        'N': '(a|c|g|t)',
        'R': '(a|g)',
        'S': '(c|g)',
        'V': '(a|c|g)',
        'W': '(a|t)',
        'Y': '(c|t)',
    }

    # Perform substitution
    def iub_sub(match):
        return substitutions[match.group(0)]

    replaced_sequence = re.sub(
        '|'.join(substitutions.keys()), iub_sub, sequence, flags=re.IGNORECASE
    )
    replaced_length = len(replaced_sequence)

    print(f"\n{initial_length}\n{sequence_length}\n{replaced_length}")

if __name__ == "__main__":
    main()
