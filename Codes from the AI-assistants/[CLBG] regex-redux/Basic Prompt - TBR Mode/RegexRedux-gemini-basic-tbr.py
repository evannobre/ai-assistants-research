# The Computer Language Benchmarks Game
# https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
#
# Contributed by Jeremy Zerfas
# Copied from the D language implementation by Dave Fladebo
# and then modified to be more Pythonic.
#
# NOTE: This is a modified version of the benchmark code to use modern
# Python features like concurrent.futures and to clearly follow the

# specified algorithm.

import sys
import re
from concurrent.futures import ProcessPoolExecutor

def count_matches(pattern: bytes, text: bytes) -> int:
    """
    Counts all non-overlapping matches of a pattern in a text.
    The pattern and text are expected to be bytes.
    """
    return len(re.findall(pattern, text))


def main():
    """
    Main function to execute the regex-redux benchmark.
    """
    # 1. Read input from stdin and get the initial length.
    # Reading as bytes is often more efficient for this type of processing.
    sequence_bytes = sys.stdin.buffer.read()
    initial_len = len(sequence_bytes)

    # 2. Clean the sequence by removing FASTA headers and newlines.
    # The regex removes lines starting with '>' and all newline characters.
    cleaned_sequence = re.sub(rb'>.*\n|\n', b'', sequence_bytes)
    clean_len = len(cleaned_sequence)

    # 3. Define the patterns to be counted and count them concurrently.
    variants = [
        b'agggtaaa|tttaccct',
        b'[cgt]gggtaaa|tttaccc[acg]',
        b'a[act]ggtaaa|tttacc[agt]t',
        b'ag[act]gtaaa|tttac[agt]ct',
        b'agg[act]taaa|ttta[agt]cct',
        b'aggg[acg]aaa|ttt[cgt]ccct',
        b'agggt[cgt]aa|tt[acg]accct',
        b'agggta[cgt]a|t[acg]taccct',
        b'agggtaa[cgt]|[acg]ttaccct'
    ]

    # Use a ProcessPoolExecutor to run counting tasks in parallel.
    # This is a modern and high-level way to manage a pool of processes.
    with ProcessPoolExecutor() as executor:
        # map() applies the function to each item in the iterables.
        # It distributes the work among the available processes.
        counts = list(executor.map(count_matches, variants, [cleaned_sequence] * len(variants)))

    # Print the results from the counting phase.
    for pattern, count in zip(variants, counts):
        # Decode from bytes to string for printing.
        print(f'{pattern.decode("utf-8")} {count}')

    # 4. Perform the sequential "magic" replacements.
    # The patterns and their replacements are defined in a specific order.
    magic_replacements = [
        (b'tHa[Nt]', b'<4>'),
        (b'aND|caN|Ha[DS]|WaS', b'<3>'),
        (b'a[NSt]|BY', b'<2>'),
        (b'<[^>]*>', b'|'),
        (b'\\|[^|][^|]*\\|', b'-')
    ]

    # The replacements are applied one after another on the evolving sequence.
    temp_sequence = cleaned_sequence
    for pattern, replacement in magic_replacements:
        temp_sequence = re.sub(pattern, replacement, temp_sequence)

    # 5. Calculate the final length after all replacements.
    final_len = len(temp_sequence)

    # 6. Print the three recorded lengths.
    print()  # An empty line for formatting, as per benchmark output.
    print(initial_len)
    print(clean_len)
    print(final_len)


if __name__ == "__main__":
    main()
