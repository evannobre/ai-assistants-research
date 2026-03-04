#!/usr/bin/env python3
import sys
import re

# Read entire stdin
data = sys.stdin.read()
length1 = len(data)

# Remove FASTA descriptions and newlines
# Pattern: description lines starting with '>' and any newline, or any newline
header_newline_re = re.compile(r'>.*\n|\n')
sequence = header_newline_re.sub('', data)
length2 = len(sequence)

# 8-mer patterns to count (in order)
patterns = [
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

# Count matches in the original data (not the newline-stripped sequence)
for p in patterns:
    cre = re.compile(p)
    count = 0
    # Use finditer to explicitly iterate through matches
    for _ in cre.finditer(data):
        count += 1
    # Print pattern and count
    print(f"{p} {count}")

# Magic patterns and replacements (apply sequentially)
magic_patterns = [
    (r'tHa[Nt]', '<4>'),
    (r'aND|caN|Ha[DS]|WaS', '<3>'),
    (r'a[NSt]|BY', '<2>'),
    (r'<[^>]*>', '|'),
    (r'\\|[^|][^|]*\\|', '-')
]

# Apply each replacement in order to the original data string
modified = data
for pat, repl in magic_patterns:
    cre = re.compile(pat)
    modified = cre.sub(repl, modified)

length3 = len(modified)

# Print the three recorded lengths
print()
print(length1)
print(length2)
print(length3)
