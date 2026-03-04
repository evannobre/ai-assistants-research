import sys
import re

def main():
    # 1. Read all input
    data = sys.stdin.read()
    len_original = len(data)

    # 2. Strip headers and newlines
    # Remove FASTA headers: lines starting with '>'
    data_no_headers = re.sub(r"^>.*\n", "", data, flags=re.MULTILINE)
    # Remove newlines
    seq = re.sub(r"\n", "", data_no_headers)
    len_clean = len(seq)

    # 3. Variant patterns to count
    variants = [
        r"agggtaaa|tttaccct",
        r"[cgt]gggtaaa|tttaccc[acg]",
        r"a[act]ggtaaa|tttacc[agt]t",
        r"ag[act]gtaaa|tttac[agt]ct",
        r"agg[act]taaa|ttta[agt]cct",
        r"aggg[acg]aaa|ttt[cgt]ccct",
        r"agggt[cgt]aa|tt[acg]accct",
        r"agggta[cgt]a|t[acg]taccct",
        r"agggtaa[cgt]|[acg]ttaccct",
    ]

    # 4. Count matches using compiled regexes
    counts = []
    for pat in variants:
        regex = re.compile(pat)
        count = len(regex.findall(seq))
        counts.append((pat, count))

    # 5. Substitution rules
    subs = [
        ("B", "(c|g|t)"),
        ("D", "(a|g|t)"),
        ("H", "(a|c|t)"),
        ("K", "(g|t)"),
        ("M", "(a|c)"),
        ("N", "(a|c|g|t)"),
        ("R", "(a|g)"),
        ("S", "(c|g)"),
        ("V", "(a|c|g)"),
        ("W", "(a|t)"),
        ("Y", "(c|t)"),
    ]

    seq_final = seq
    for key, repl in subs:
        # key is a literal character; escape it to be safe
        seq_final = re.sub(key, repl, seq_final)

    len_final = len(seq_final)

    # 6. Print results
    print(len_original)
    print(len_clean)
    for pat, count in counts:
        print(f"{pat} {count}")
    print(len_final)

if __name__ == "__main__":
    main()
