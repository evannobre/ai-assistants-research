import re
import sys

def main():
    data = sys.stdin.read()
    
    # Remove FASTA headers (lines starting with '>') and newlines
    seq = re.sub(r'>.*\n?', '', data)
    seq = re.sub(r'\n', '', seq)
    
    len_clean = len(seq)
    len1 = len_clean
    len2 = len_clean
    
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
    
    for pat in patterns:
        count = len(re.findall(pat, seq, flags=re.IGNORECASE))
        print(f"{pat} {count}")
    
    # Perform the replacements in order
    seq = re.sub(r'tHa[Nt]', '<4>', seq, flags=re.IGNORECASE)
    seq = re.sub(r'aND|caN|Ha[DS]|WaS', '<3>', seq, flags=re.IGNORECASE)
    seq = re.sub(r'a[NSt]|BY', '<2>', seq, flags=re.IGNORECASE)
    seq = re.sub(r'<[^>]*>', '|', seq)
    seq = re.sub(r'\|[^|][^|]*\|', '-', seq)
    
    len3 = len(seq)
    
    print()
    print(len1)
    print(len2)
    print(len3)

if __name__ == "__main__":
    main()