import sys
import bisect

# Constants for LCG
IM = 139968
IA = 3877
IC = 29573
SEED = 42

# LCG implementation as specified
def random_number(max_val):
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

def make_cumulative(table):
    """Convert probability table to cumulative probabilities"""
    # Create list of (nucleotide, probability)
    items = list(table.items())
    
    # Calculate cumulative probabilities (naïve approach)
    cumulative = []
    current = 0.0
    for char, prob in items:
        current += prob
        cumulative.append((char, current))
    
    return cumulative

def select_random(cumulative):
    """Select nucleotide using cumulative probabilities with linear search"""
    r = random_number(1.0)
    
    # Linear search as specified (not binary)
    for char, cum_prob in cumulative:
        if r <= cum_prob:
            return char
    return cumulative[-1][0]  # Fallback

def generate_repeat_fasta(seq, n):
    """Generate DNA by copying from given sequence"""
    out = []
    seq_len = len(seq)
    pos = 0
    
    while n > 0:
        chunk = min(n, seq_len - pos, 60)
        out.append(seq[pos:pos + chunk])
        pos = (pos + chunk) % seq_len
        n -= chunk
        if n > 0 and chunk == 60:
            out.append('\n')
    
    sys.stdout.write(''.join(out) + '\n')

def generate_random_fasta(table, n):
    """Generate DNA using weighted random selection"""
    # Create cumulative probabilities
    cumulative = make_cumulative(table)
    
    out = []
    while n > 0:
        chunk = min(n, 60)
        for i in range(chunk):
            out.append(select_random(cumulative))
        out.append('\n')
        n -= chunk
    
    sys.stdout.write(''.join(out))

def main():
    n = 1000
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    
    # Reset seed for each test
    global SEED
    SEED = 42
    
    # ALU sequence
    alu = (
        'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
        'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
        'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
        'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
        'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
        'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
        'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
    )
    
    # Probability tables
    iub = {
        'a': 0.27, 'c': 0.12, 'g': 0.12, 't': 0.27,
        'B': 0.02, 'D': 0.02, 'H': 0.02, 'K': 0.02,
        'M': 0.02, 'N': 0.02, 'R': 0.02, 'S': 0.02,
        'V': 0.02, 'W': 0.02, 'Y': 0.02
    }
    
    homosapiens = {
        'a': 0.3029549426680,
        'c': 0.1979883004921,
        'g': 0.1975473066391,
        't': 0.3015094502008
    }
    
    # Generate sequences
    sys.stdout.write(f'>ONE Homo sapiens alu\n')
    generate_repeat_fasta(alu, n * 2)
    
    sys.stdout.write(f'>TWO IUB ambiguity codes\n')
    SEED = 42  # Reset seed
    generate_random_fasta(iub, n * 3)
    
    sys.stdout.write(f'>THREE Homo sapiens frequency\n')
    SEED = 42  # Reset seed
    generate_random_fasta(homosapiens, n * 5)

if __name__ == '__main__':
    main()