#!/usr/bin/env python3
import sys
import re

# === Step 1: Read redirected FASTA input from stdin ===
input_data = sys.stdin.read()

# === Step 2: Record original length ===
original_length = len(input_data)

# === Step 3: Remove FASTA headers and newlines ===
# Remove lines starting with '>'
input_cleaned = re.sub(r'>.*\n', '', input_data)
# Remove all linefeeds
input_cleaned = re.sub(r'\n', '', input_cleaned)

# === Step 4: Record cleaned sequence length ===
cleaned_length = len(input_cleaned)

# === Step 5: Define simple DNA regex patterns (with reverse complement variants) ===
patterns = [
    'agggtaaa|tttaccct',
    '[cgt]gggtaaa|tttaccc[acg]',
    'a[act]ggtaaa|tttacc[agt]t',
    'ag[act]gtaaa|tttac[agt]ct',
    'agg[act]taaa|ttta[agt]cct',
    'aggg[acg]aaa|ttt[cgt]ccct',
    'agggt[cgt]aa|tt[acg]accct',
    'agggta[cgt]a|t[acg]taccct',
    'agggtaa[cgt]|[acg]ttaccct'
]

# === Step 6: Count matches for each pattern and print ===
for pat in patterns:
    count = len(re.findall(pat, input_cleaned, re.IGNORECASE))
    print(f"{pat} {count}")

# === Step 7: Define "magic" regex patterns and replacements ===
magic_patterns = [
    (r'tHa[Nt]', '<4>'),
    (r'aND|caN|Ha[DS]|WaS', '<3>'),
    (r'a[NSt]|BY', '<2>'),
    (r'<[^>]*>', '|'),
    (r'\|[^|][^|]*\|', '-')
]

# Apply one pattern at a time to the original input data
transformed = input_data
for pattern, replacement in magic_patterns:
    transformed = re.sub(pattern, replacement, transformed)

# === Step 8: Record length after magic replacements ===
final_length = len(transformed)

# === Step 9: Print all recorded lengths ===
print()
print(original_length)
print(cleaned_length)
print(final_length)
