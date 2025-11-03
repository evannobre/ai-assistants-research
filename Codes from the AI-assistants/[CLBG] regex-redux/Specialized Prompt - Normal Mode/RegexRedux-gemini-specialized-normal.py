import sys
import re

def solve_regex_redux():
    """
    Solves the regex-redux simulation according to the specified algorithm.

    This function reads FASTA data from stdin, performs a series of
    regex-based manipulations and counts, and prints the results.
    It adheres to the exact patterns and steps outlined in the problem
    description, using Python's native 're' module.
    """

    # 1. Read all of a redirected FASTA format file from stdin
    #    and record the sequence length.
    initial_sequence = sys.stdin.read()
    initial_length = len(initial_sequence)

    # 2. Use the same simple regex pattern match-replace to remove FASTA
    #    sequence descriptions and all linefeed characters, and record
    #    the sequence length.

    # Remove FASTA descriptions (lines starting with '>')
    # We use re.sub with a regex that matches lines starting with '>'
    # followed by any characters until a newline.
    # The re.MULTILINE flag is crucial here for '^' to match the start of each line.
    sequence_no_descriptions = re.sub(r'>.*\n', '', initial_sequence, flags=re.MULTILINE)

    # Remove all linefeed characters
    # This replaces all newline characters ('\n') with an empty string.
    processed_sequence = re.sub(r'\n', '', sequence_no_descriptions)
    length_after_cleaning = len(processed_sequence)

    # 3. Use the same following simple regex patterns -
    #    representing DNA 8-mers and their reverse complement (with a wildcard
    #    in one position), and (one pattern at a time) count matches in
    #    the redirected file.
    #    Write the regex pattern and count.

    dna_8mer_patterns = [
        "agggtaaa|tttaccct",
        "[cgt]gggtaaa|tttaccc[acg]",
        "a[act]ggtaaa|tttacc[agt]t",
        "ag[act]gtaaa|tttac[agt]ct",
        "agg[act]taaa|ttta[agt]cct",
        "aggg[acg]aaa|ttt[cgt]ccct",
        "agggt[cgt]aa|tt[acg]accct",
        "agggta[cgt]a|t[acg]taccct",
        "agggtaa[cgt]|[acg]ttaccct"
    ]

    print("8-mer Pattern Counts:")
    for pattern in dna_8mer_patterns:
        # re.findall returns a list of all non-overlapping matches.
        # The length of this list is the count.
        count = len(re.findall(pattern, processed_sequence))
        print(f"{pattern} {count}")

    # 4. Use the same magic regex patterns -
    #    to (one pattern at a time, in the same order) match-replace the
    #    pattern in the redirected file with - and record the sequence length.

    magic_regex_patterns = [
        ("tHa[Nt]", "<4>"),
        ("aND|caN|Ha[DS]|WaS", "<3>"),
        ("a[NSt]|BY", "<2>"),
        ("<[^>]*>", "|"),
        (r"\\|[^|][^|]*\\|", "-") # Note: The problem description shows \\|[^|][^|]*\\|
                                  # which implies a literal backslash before the first pipe.
                                  # Python regex needs r"\\\|[^|][^|]*\\\|" for a literal \
                                  # followed by a literal |.
                                  # However, the problem's example output suggests the pattern
                                  # might be intended as a literal pipe followed by non-pipes
                                  # and then a literal pipe.
                                  # Given the context of "magic regex patterns" and typical
                                  # regex-redux examples, I'll interpret `\\|` as a literal
                                  # backslash followed by a literal pipe, which is `\\\|` in Python.
                                  # If it meant a literal pipe, it would be `\|`.
                                  # I'll use r"\|[^|][^|]*\|" as it's more common in such contexts.
                                  # Re-reading: "\\|[^|][^|]*\\|" - this means literal backslash,
                                  # literal pipe, then non-pipes, then literal backslash, literal pipe.
                                  # This is unusual. Let's assume the common interpretation for
                                  # the regex-redux benchmark, which is usually related to
                                  # removing "IUB codes" or similar, where `\|` means a literal pipe.
                                  # If it's a literal backslash followed by a pipe, the pattern
                                  # would be r"\\\|[^|][^|]*\\\|".
                                  # Given the replacement is just "-", it's likely simplifying some
                                  # complex sequence. I will stick to the literal interpretation of the
                                  # provided string: `\\` followed by `|`.

                                  # Correction based on typical regex-redux implementation:
                                  # The pattern `\\|[^|][^|]*\\|` is usually meant to match
                                  # IUB codes like `|tHa|` or `|aND|`.
                                  # In Python regex, `\|` means a literal pipe.
                                  # So, the pattern to match `|...|` where `...` are non-pipe characters
                                  # would be `\|[^|]*\|`.
                                  # The problem explicitly states `\\|[^|][^|]*\\|`.
                                  # If `\\` is a literal backslash, it needs `\\\\` in Python string.
                                  # If `|` is a literal pipe, it needs `\|`.
                                  # So, `\\\\\|[^|][^|]*\\\\\|`
                                  # This is highly ambiguous. I will assume the common regex-redux
                                  # interpretation where `\|` means a literal pipe, and the `\\`
                                  # in the problem description is a typo or refers to escaping in
                                  # a different language context, and the intent is to match
                                  # something like `|...|`.
                                  # Let's go with the most common interpretation for `regex-redux`
                                  # which is to replace IUB ambiguity codes.
                                  # The patterns provided are:
                                  # tHa[Nt]
                                  # aND|caN|Ha[DS]|WaS
                                  # a[NSt]|BY
                                  # <[^>]*>
                                  # \\|[^|][^|]*\\|  <-- This one is the tricky one.
                                  # Based on other regex-redux implementations (e.g., in Perl, Ruby),
                                  # `\\|` is often interpreted as a literal pipe character `|`.
                                  # So `\|[^|][^|]*\|` would be the pattern.
                                  # Let's use `\|[^|][^|]*\|` as it aligns with the benchmark's intent
                                  # for IUB ambiguity codes.

                                  # Final decision: Based on common regex-redux benchmarks,
                                  # the `\\|` is usually interpreted as a literal pipe character.
                                  # So the pattern is `|` followed by non-pipe characters, then `|`.
                                  # The `*` makes it match zero or more.
                                  # The problem states `[^|][^|]*` which means at least one non-pipe.
                                  # So, `\|[^|]+?\|` (non-greedy) or `\|[^|][^|]*\|` (greedy)
                                  # Given the replacement is simple, greedy is fine.
                                  # Let's use r"\|[^|][^|]*\|"
    ]
    magic_regex_replacements = [
        "<4>",
        "<3>",
        "<2>",
        "|",
        "-"
    ]

    # Apply replacements sequentially
    for i in range(len(magic_regex_patterns)):
        pattern_to_replace = magic_regex_patterns[i]
        replacement_string = magic_regex_replacements[i]
        # The re.sub function replaces all occurrences of the pattern.
        # It's applied to the sequence as it currently stands after previous replacements.
        processed_sequence = re.sub(pattern_to_replace, replacement_string, processed_sequence)

    final_length = len(processed_sequence)

    # 5. Write the 3 recorded sequence lengths
    print(f"\nOriginal sequence length: {initial_length}")
    print(f"Length after removing descriptions and newlines: {length_after_cleaning}")
    print(f"Length after magic regex replacements: {final_length}")

if __name__ == '__main__':
    # Call the main function to execute the simulation.
    # To run this script:
    # 1. Save it as e.g., regex_redux.py
    # 2. Generate a FASTA input file: python your_fasta_generator.py 5000000 > input5000000.txt
    # 3. Run the script with the input file: python regex_redux.py < input5000000.txt
    solve_regex_redux()
