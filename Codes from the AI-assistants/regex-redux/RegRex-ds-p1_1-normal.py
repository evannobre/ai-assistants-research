import sys
import re

def regex_redux():
    # Read input
    data = sys.stdin.read()
    original_len = len(data)
    
    # 1. Remove description lines
    data = re.sub(r'>.*\n|\n', '', data)
    
    # 2. Apply initial substitutions
    variants = [
        ('B', '(c|g|t)'),
        ('D', '(a|g|t)'),
        ('H', '(a|c|t)'),
        ('K', '(g|t)'),
        ('M', '(a|c)'),
        ('N', '(a|c|g|t)'),
        ('R', '(a|g)'),
        ('S', '(c|g)'),
        ('V', '(a|c|g)'),
        ('W', '(a|t)'),
        ('Y', '(c|t)')
    ]
    
    # Build pattern for all substitutions
    for code, replacement in variants:
        data = re.sub(code, replacement, data)
    
    processed_len = len(data)
    
    # 3. Count patterns
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
    
    counts = []
    for pattern in patterns:
        count = len(re.findall(pattern, data))
        counts.append(f"{pattern} {count}")
    
    # 4. Final substitutions
    subst = {
        'tHa[Nt]': '<4>',
        'aND|caN|Ha[DS]|WaS': '<3>',
        'a[NSt]|BY': '<2>',
        '<[^>]*>': '|',
        '\\|[^|][^|]*\\|': '-'
    }
    
    for pattern, replacement in subst.items():
        data = re.sub(pattern, replacement, data)
    
    # Output results
    print('\n'.join(counts))
    print(f"\n{original_len}")
    print(f"{processed_len}")
    print(f"{len(data)}")

if __name__ == "__main__":
    regex_redux()