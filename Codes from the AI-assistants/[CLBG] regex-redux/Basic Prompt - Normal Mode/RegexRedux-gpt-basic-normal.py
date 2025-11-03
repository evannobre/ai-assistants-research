#!/usr/bin/env python3
import sys
import re

# Read full input from stdin
data = sys.stdin.read()
initial_length = len(data)

# Remove description lines and newlines using simple regex
cleaned = re.sub(r'>[^\n]*\n|\n', '', data)
cleaned_length = len(cleaned)

# DNA 8-mer and reverse complement patterns
eight_mer_patterns = [
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

# Count matches for each pattern in the cleaned sequence
for pattern in eight_mer_patterns:
    count = len(re.findall(pattern, cleaned, re.IGNORECASE))
    print(f"{pattern} {count}")

# Replacement regex patterns and their replacements
replacement_patterns = [
    (re.compile('tHa[Nt]'), '<4>'),
    (re.compile('aND|caN|Ha[DS]|WaS'), '<3>'),
    (re.compile('a[NSt]|BY'), '<2>'),
    (re.compile('<[^>]*>'), '|'),
    (re.compile(r'\|[^|][^|]*\|'), '-'),
]

# Apply replacements sequentially
replaced = cleaned
for regex, repl in replacement_patterns:
    replaced = regex.sub(repl, replaced)

final_length = len(replaced)

# Print sequence lengths
print()
print(initial_length)
print(cleaned_length)
print(final_length)
