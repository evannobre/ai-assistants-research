import sys
import re

def main():
    data = sys.stdin.read()
    
    # 1. Preprocess to get a single contiguous sequence
    seq = re.sub(r'>.*\n', '', data)   # drop headers
    seq = seq.replace('\n', '')        # drop newlines

    # 2. Count fixed patterns
    patterns = [
        r'agggtaaa|tttaccct',
        r'[cgt]gggtaaa|tttaccc[acg]',
        r'a[act]ggtaaa|tttacc[agt]t',
        r'ag[act]gtaaa|tttac[agt]c',
        r'agg[act]taaa|ttta[agt]cct',
        r'aggg[acg]aaa|ttt[cgt]ccct',
        r'agggt[cgt]aa|tt[acg]accct',
        r'agggta[cgt]a|t[acg]taccct',
        r'agggtaa[cgt]|[acg]ttaccct'
    ]
    for pat in patterns:
        count = len(re.findall(pat, seq))
        print(f"{pat} {count}")

    # 3. Remove patterns and measure lengths
    removals = [
        r'<!--.*?-->',          # HTML/XML comments
        r'<[^>]*>',             # tags
        r'//.*?$' ,             # single-line comments (if any)
        r'/\*.*?\*/'            # multi-line comments (if any)
    ]
    orig_len = len(data)
    cleaned = data
    for pat in removals:
        cleaned = re.sub(pat, '', cleaned, flags=re.DOTALL | re.MULTILINE)
    removed_len = len(cleaned)
    delta = orig_len - removed_len

    print(f"\n{orig_len} {removed_len} {delta}")

if __name__ == "__main__":
    main()
