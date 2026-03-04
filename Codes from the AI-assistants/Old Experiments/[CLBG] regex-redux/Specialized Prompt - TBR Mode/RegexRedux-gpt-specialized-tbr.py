import sys, re

# Step 1
data = sys.stdin.read()
initial_len = len(data)

# Step 2
header_nl = re.compile(r"^>.*\n?|\n", re.MULTILINE)
clean_seq = header_nl.sub("", data)
clean_len = len(clean_seq)

# Step 3
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
for pat in patterns:
    count = len(re.findall(pat, data))
    print(f"{pat} {count}")

# Step 4
magic = [
    (r"tHa[Nt]",    "<4>"),
    (r"aND|caN|Ha[DS]|WaS", "<3>"),
    (r"a[NSt]|BY",  "<2>"),
    (r"<[^>]*>",    "|"),
    (r"\|[^|][^|]*\|", "-")
]
mutated = data
for pat, repl in magic:
    mutated = re.sub(pat, repl, mutated)

final_len = len(mutated)

# Step 5
print(f"\n{initial_len} {clean_len} {final_len}")
