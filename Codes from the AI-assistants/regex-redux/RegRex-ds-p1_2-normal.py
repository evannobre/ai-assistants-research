def regex_redux_optimized():
    data = sys.stdin.read()
    original_len = len(data)
    
    # Remove description lines and newlines
    data = re.sub(r'>.*\n|\n', '', data)
    
    # Pre-compile all patterns
    variant_patterns = {
        'B': re.compile(r'B'),
        'D': re.compile(r'D'),
        'H': re.compile(r'H'),
        'K': re.compile(r'K'),
        'M': re.compile(r'M'),
        'N': re.compile(r'N'),
        'R': re.compile(r'R'),
        'S': re.compile(r'S'),
        'V': re.compile(r'V'),
        'W': re.compile(r'W'),
        'Y': re.compile(r'Y')
    }
    
    variant_replacements = {
        'B': '(c|g|t)',
        'D': '(a|g|t)',
        'H': '(a|c|t)',
        'K': '(g|t)',
        'M': '(a|c)',
        'N': '(a|c|g|t)',
        'R': '(a|g)',
        'S': '(c|g)',
        'V': '(a|c|g)',
        'W': '(a|t)',
        'Y': '(c|t)'
    }
    
    # Apply substitutions
    for code, pattern in variant_patterns.items():
        data = pattern.sub(variant_replacements[code], data)
    
    # Count patterns with pre-compiled regex
    patterns = [
        re.compile(r'agggtaaa|tttaccct'),
        re.compile(r'[cgt]gggtaaa|tttaccc[acg]'),
        re.compile(r'a[act]ggtaaa|tttacc[agt]t'),
        re.compile(r'ag[act]gtaaa|tttac[agt]ct'),
        re.compile(r'agg[act]taaa|ttta[agt]cct'),
        re.compile(r'aggg[acg]aaa|ttt[cgt]ccct'),
        re.compile(r'agggt[cgt]aa|tt[acg]accct'),
        re.compile(r'agggta[cgt]a|t[acg]taccct'),
        re.compile(r'agggtaa[cgt]|[acg]ttaccct')
    ]
    
    pattern_strings = [
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
    for pattern_str, pattern_obj in zip(pattern_strings, patterns):
        count = len(pattern_obj.findall(data))
        counts.append(f"{pattern_str} {count}")
    
    # Final substitutions
    subst_patterns = [
        (re.compile(r'tHa[Nt]'), r'<4>'),
        (re.compile(r'aND|caN|Ha[DS]|WaS'), r'<3>'),
        (re.compile(r'a[NSt]|BY'), r'<2>'),
        (re.compile(r'<[^>]*>'), r'|'),
        (re.compile(r'\|[^|][^|]*\|'), r'-')
    ]
    
    for pattern, replacement in subst_patterns:
        data = pattern.sub(replacement, data)
    
    # Output
    print('\n'.join(counts))
    print(f"\n{original_len}\n{len(data)}")