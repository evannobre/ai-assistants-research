#!/usr/bin/env python3
import sys
import re

# Read the entire FASTA file from stdin
sequence_input = sys.stdin.read()

# Original length including description lines and linefeeds
initial_length = len(sequence_input)

# Remove description lines and newlines
sequence_cleaned = re.sub(r'>.*\n|\n', '', sequence_input)
cleaned_length = len(sequence_cleaned)

# DNA 8-mer regex patterns (forward + reverse complement)
patterns = [
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

# Count pattern matches
for pattern in patterns:
    count = len(re.findall(pattern, sequence_cleaned, flags=re.IGNORECASE))
    print(f"{pattern} {count}")

# Magic substitution patterns
substitutions = [
    (r'tHa[Nt]', '<4>'),
    (r'aND|caN|Ha[DS]|WaS', '<3>'),
    (r'a[NSt]|BY', '<2>'),
    (r'<[^>]*>', '|'),
    (r'\|[^|][^|]*\|', '-')
]

# Apply substitutions in order
substituted_sequence = sequence_cleaned
for pattern, replacement in substitutions:
    substituted_sequence = re.sub(pattern, replacement, substituted_sequence, flags=re.IGNORECASE)

# Final substituted length
substituted_length = len(substituted_sequence)

# Output sequence lengths
print()
print(initial_length)
print(cleaned_length)
print(substituted_length)
