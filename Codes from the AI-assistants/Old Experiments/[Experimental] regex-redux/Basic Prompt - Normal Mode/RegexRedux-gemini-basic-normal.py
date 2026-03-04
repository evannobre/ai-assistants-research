import re
import sys

def solve_regex_redux(input_data):
    """
    Solves the regex-redux simulation using native Python libraries.

    Args:
        input_data (str): The raw input string (e.g., DNA sequence).

    Returns:
        tuple: A tuple containing:
            - original_length (int)
            - cleaned_length (int)
            - counts (list of tuples: (pattern, count))
            - final_length (int)
    """

    # 1. Read Input (already provided as input_data for this function)
    # In a real script, you'd read from stdin or a file:
    # input_data = sys.stdin.read()

    original_length = len(input_data)

    # 2. Initial Cleanup
    # Remove all lines starting with '>' and all newline characters
    # Using re.sub with multiline flag to target lines starting with '>'
    # Then removing all newlines
    cleaned_sequence = re.sub(r'>.*\n|\n', '', input_data)
    cleaned_length = len(cleaned_sequence)

    # 3. Define Counting Patterns
    # These are common patterns used in regex-redux benchmarks
    counting_patterns = [
        "agggtaaa|tttcccta",
        "[cgt]gggtaaa|tttccc[acg]",
        "a[act]ggtaaa|tttcc[agt]t",
        "ag[act]gtaaa|tttac[agt]t",
        "agg[act]taaa|ttta[agt]cct",
        "aggg[act]aaa|ttta[agt]cc",
        "agggt[act]aa|ttta[agt]tcc",
        "agggta[act]a|ttt[agt]tcc",
        "agggtaa[act]|tt[agt]tccc"
    ]

    # 4. Count Pattern Occurrences
    counts = []
    for pattern_str in counting_patterns:
        # re.findall returns a list of all non-overlapping matches
        # The length of this list is the count
        count = len(re.findall(pattern_str, cleaned_sequence))
        counts.append((pattern_str, count))

    # 5. Define Replacement Rules
    # These are common replacement rules used in regex-redux benchmarks
    replacement_rules = [
        (r"agggtaaa|tttcccta", "B"),
        (r"[cgt]gggtaaa|tttccc[acg]", "X"),
        (r"a[act]ggtaaa|tttcc[agt]t", "Y"),
        (r"ag[act]gtaaa|tttac[agt]t", "Z"),
        (r"agg[act]taaa|ttta[agt]cct", "O"),
        (r"aggg[act]aaa|ttta[agt]cc", "P"),
        (r"agggt[act]aa|ttta[agt]tcc", "Q"),
        (r"agggta[act]a|ttt[agt]tcc", "R"),
        (r"agggtaa[act]|tt[agt]tccc", "S")
    ]

    # 6. Apply Replacements
    # Start with the cleaned sequence
    modified_sequence = cleaned_sequence
    for pattern_str, replacement_str in replacement_rules:
        # re.sub replaces all occurrences of the pattern with the replacement string
        modified_sequence = re.sub(pattern_str, replacement_str, modified_sequence)

    final_length = len(modified_sequence)

    return original_length, cleaned_length, counts, final_length

if __name__ == "__main__":
    # Example Usage:
    # In a real benchmark, this would read from sys.stdin or a file.
    # For demonstration, let's create a dummy input.
    # A common input is a large DNA sequence.
    # You can download a sample from: http://benchmarksgame-team.pages.debian.net/benchmarksgame/program/regexredux-python-2.html
    # Look for the 'fasta' input.

    # Example dummy input (truncated for brevity)
    # A real input would be much larger (e.g., 25MB)
    dummy_input = """>SOME_HEADER_1
agggtaaaagggtaaaagggtaaaagggtaaa
tttccctatttccctatttccctatttcccta
>SOME_HEADER_2
[cgt]gggtaaa[cgt]gggtaaa
tttccc[acg]tttccc[acg]
"""

    original_len, cleaned_len, pattern_counts, final_len = solve_regex_redux(dummy_input)

    # 7. Report Results
    print(f"Original length: {original_len}")
    print(f"Cleaned length: {cleaned_len}")
    print("\nPattern Counts:")
    for pattern, count in pattern_counts:
        print(f"{pattern} {count}")
    print(f"\nFinal length: {final_len}")

    # To run with a real large input (e.g., from a file named 'dna.txt'):
    # with open('dna.txt', 'r') as f:
    #     large_dna_input = f.read()
    # original_len, cleaned_len, pattern_counts, final_len = solve_regex_redux(large_dna_input)
    # print(f"Original length: {original_len}")
    # print(f"Cleaned length: {cleaned_len}")
    # print("\nPattern Counts:")
    # for pattern, count in pattern_counts:
    #     print(f"{pattern} {count}")
    # print(f"\nFinal length: {final_len}")