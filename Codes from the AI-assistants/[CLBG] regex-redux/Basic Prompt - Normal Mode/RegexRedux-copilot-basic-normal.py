import sys
import re

# Read entire input from stdin
fasta = sys.stdin.read()
initial_len = len(fasta)

# Remove FASTA descriptions (">..." lines) and all linefeeds
sequence = re.sub(r'>[^\n]*\n|\n', '', fasta)
cleaned_len = len(sequence)

# List of DNA 8-mer regex patterns (counted individually)
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
    count = len(re.findall(pattern, sequence, flags=re.IGNORECASE))
    print(f"{pattern} {count}")

# Replacement rules and their targets
magic_patterns = [
    (re.compile(r"tHa[Nt]", flags=re.IGNORECASE), "<4>"),
    (re.compile(r"aND|caN|Ha[DS]|WaS", flags=re.IGNORECASE), "<3>"),
    (re.compile(r"a[NSt]|BY", flags=re.IGNORECASE), "<2>"),
    (re.compile(r"<[^>]*>"), "|"),
    (re.compile(r"\|[^|][^|]*\|"), "-")
]

# Apply substitutions sequentially
modified_seq = sequence
for regex, replacement in magic_patterns:
    modified_seq = regex.sub(replacement, modified_seq)

final_len = len(modified_seq)

# Output the 3 sequence lengths
print(f"\n{initial_len}\n{cleaned_len}\n{final_len}")
