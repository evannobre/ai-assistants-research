import sys

# LCG parameters
IM = 139968
IA = 3877
IC = 29573
seed = 42

def random_max(max_val):
    """Naïve LCG implementation as specified"""
    global seed
    seed = (seed * IA + IC) % IM
    return max_val * seed / IM

def make_cumulative(prob_dict):
    """Convert probabilities to cumulative probabilities (naïve linear search approach)"""
    # Create sorted list of (nucleotide, probability)
    items = list(prob_dict.items())
    
    # Build cumulative probabilities
    cumulative = []
    total = 0.0
    for key, prob in items:
        total += prob
        cumulative.append((key, total))
    
    return cumulative

def select_nucleotide(cumulative):
    """Select nucleotide using cumulative probabilities with linear search"""
    r = random_max(1.0)
    
    # Linear search through cumulative probabilities
    for nucleotide, cum_prob in cumulative:
        if r <= cum_prob:
            return nucleotide
    
    # Fallback (shouldn't reach here if probabilities sum to 1)
    return cumulative[-1][0]

def repeat_fasta(src, n):
    """Generate DNA by repeating source sequence"""
    width = 60
    r = len(src)
    s = src + src + src[:n % r]
    
    for j in range(n // width):
        i = j * width % r
        print(s[i:i+width])
    
    if n % width:
        print(s[-(n % width):])

def random_fasta(table, n):
    """Generate DNA using weighted random selection from table"""
    width = 60
    
    # Create cumulative probabilities
    cumulative = make_cumulative(table)
    
    # Generate sequence
    for j in range(n // width):
        line = []
        for i in range(width):
            line.append(select_nucleotide(cumulative))
        print(''.join(line))
    
    if n % width:
        line = []
        for i in range(n % width):
            line.append(select_nucleotide(cumulative))
        print(''.join(line))

def main():
    # Parse command line argument
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 1000
    
    # ALU sequence to copy
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAG"
        "GCGGGCGGATCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGG"
        "TGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGC"
        "GCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAAC"
        "CCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCC"
        "TGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    
    # IUB ambiguity codes with probabilities
    iub = {
        'a': 0.27,
        'c': 0.12,
        'g': 0.12,
        't': 0.27,
        'B': 0.02,
        'D': 0.02,
        'H': 0.02,
        'K': 0.02,
        'M': 0.02,
        'N': 0.02,
        'R': 0.02,
        'S': 0.02,
        'V': 0.02,
        'W': 0.02,
        'Y': 0.02
    }
    
    # Homo sapiens frequencies
    homosapiens = {
        'a': 0.3029549426680,
        'c': 0.1979883004921,
        'g': 0.1975473066391,
        't': 0.3015094502008
    }
    
    # Reset seed for reproducible output
    global seed
    seed = 42
    
    # Write FASTA format
    print(f">ONE Homo sapiens alu")
    repeat_fasta(alu, n * 2)
    
    print(f">TWO IUB ambiguity codes")
    random_fasta(iub, n * 3)
    
    print(f">THREE Homo sapiens frequency")
    random_fasta(homosapiens, n * 5)

if __name__ == "__main__":
    main()