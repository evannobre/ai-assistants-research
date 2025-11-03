import sys
import re

def main():
    data = sys.stdin.read()
    ilen = len(data)
    
    seq = re.sub(r'>[^\n]*\n', '', data)
    seq = seq.replace('\n', '')
    clen = len(seq)
    
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
    
    counts = []
    for pat in patterns:
        cnt = len(re.findall(pat, seq))
        counts.append((pat, cnt))
    
    magic_patterns = [
        (r'tHa[Nt]', r'<4>'),
        (r'aND|caN|Ha[DS]|WaS', r'<3>'),
        (r'a[NSt]|BY', r'<2>'),
        (r'<[^>]*>', r'|'),
        (r'\|[^|][^|]*\|', r'-')
    ]
    
    current = seq
    for pat, repl in magic_patterns:
        current = re.sub(pat, repl, current)
    flen = len(current)
    
    for pat, cnt in counts:
        print(f"{pat} {cnt}")
    
    print()
    print(ilen)
    print(clen)
    print(flen)

if __name__ == '__main__':
    main()