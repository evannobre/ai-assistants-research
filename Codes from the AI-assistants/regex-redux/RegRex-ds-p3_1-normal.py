import sys
import re

def main():
    # Read all input from stdin
    input_data = sys.stdin.read()
    
    # Record initial length
    initial_length = len(input_data)
    
    # 1. Remove FASTA sequence descriptions and linefeeds
    # Match ">...\n" OR "\n"
    cleaned = re.sub(r'>.*\n|\n', '', input_data)
    
    # Record cleaned length
    cleaned_length = len(cleaned)
    
    # 2. Count patterns
    patterns = [
        r"agggtaaa|tttaccct",
        r"[cgt]gggtaaa|tttaccc[acg]",
        r"a[act]ggtaaa|tttacc[agt]t",
        r"ag[act]gtaaa|tttac[agt]ct",
        r"agg[act]taaa|ttta[agt]cct",
        r"aggg[acg]aaa|ttt[cgt]ccct",
        r"agggt[cgt]aa|tt[acg]accct",
        r"agggta[cgt]a|t[acg]taccct",
        r"agggtaa[cgt]|[acg]ttaccct"
    ]
    
    for pattern in patterns:
        count = len(re.findall(pattern, cleaned))
        print(f"{pattern} {count}")
    
    # 3. Apply substitution patterns
    substitutions = [
        (r"tHa[Nt]", "<4>"),
        (r"aND|caN|Ha[DS]|WaS", "<3>"),
        (r"a[NSt]|BY", "<2>"),
        (r"<[^>]*>", "|"),
        (r"\\|[^|][^|]*\\|", "-")
    ]
    
    transformed = cleaned
    for pattern, replacement in substitutions:
        transformed = re.sub(pattern, replacement, transformed)
    
    # Record final length
    final_length = len(transformed)
    
    # 4. Print lengths
    print(f"\n{initial_length}\n{cleaned_length}\n{final_length}")

if __name__ == "__main__":
    main()