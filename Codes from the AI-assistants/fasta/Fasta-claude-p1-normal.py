import sys
import numpy as np

# LCG constants (same as used in benchmarks)
IM = 139968
IA = 3877
IC = 29573

# Global LCG seed
last = 42

def gen_random(max_val):
    """Generate random number using Linear Congruential Generator"""
    global last
    last = (last * IA + IC) % IM
    return max_val * last / IM

def make_cumulative(genelist):
    """Convert probability list to cumulative probabilities"""
    cp = 0.0
    cumulative = []
    for char, prob in genelist:
        cp += prob
        cumulative.append((char, cp))
    return cumulative

def select_random(cumulative):
    """Select character based on cumulative probability"""
    r = gen_random(1.0)
    for char, prob in cumulative:
        if r < prob:
            return char
    return cumulative[-1][0]

def make_repeat_fasta(id_str, desc, alu, n):
    """Generate repeating FASTA sequence"""
    print(f'>{id_str} {desc}')
    alu_len = len(alu)
    line_length = 60
    
    for i in range(0, n, line_length):
        chunk_size = min(line_length, n - i)
        start = i % alu_len
        
        if start + chunk_size <= alu_len:
            print(alu[start:start + chunk_size])
        else:
            # Wrap around
            first_part = alu[start:]
            remaining = chunk_size - len(first_part)
            second_part = alu[:remaining]
            print(first_part + second_part)

def make_random_fasta(id_str, desc, genelist, n):
    """Generate random FASTA sequence using LCG"""
    print(f'>{id_str} {desc}')
    cumulative = make_cumulative(genelist)
    line_length = 60
    
    # Generate in chunks for better performance
    lines = n // line_length
    remaining = n % line_length
    
    for _ in range(lines):
        line = ''.join(select_random(cumulative) for _ in range(line_length))
        print(line)
    
    if remaining > 0:
        line = ''.join(select_random(cumulative) for _ in range(remaining))
        print(line)

def make_random_fasta_numpy(id_str, desc, genelist, n):
    """Optimized version using NumPy for vectorized operations"""
    print(f'>{id_str} {desc}')
    cumulative = make_cumulative(genelist)
    chars = [c for c, _ in cumulative]
    probs = np.array([p for _, p in cumulative])
    
    line_length = 60
    lines = n // line_length
    remaining = n % line_length
    
    # Pre-generate random numbers in batches
    global last
    
    for _ in range(lines):
        # Generate line_length random numbers
        randoms = np.zeros(line_length)
        for i in range(line_length):
            last = (last * IA + IC) % IM
            randoms[i] = last / IM
        
        # Select characters based on cumulative probabilities
        line = []
        for r in randoms:
            for j, prob in enumerate(probs):
                if r < prob:
                    line.append(chars[j])
                    break
        print(''.join(line))
    
    if remaining > 0:
        randoms = np.zeros(remaining)
        for i in range(remaining):
            last = (last * IA + IC) % IM
            randoms[i] = last / IM
        
        line = []
        for r in randoms:
            for j, prob in enumerate(probs):
                if r < prob:
                    line.append(chars[j])
                    break
        print(''.join(line))

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
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
    
    # IUB ambiguity codes
    iub = [
        ('a', 0.27),
        ('c', 0.12),
        ('g', 0.12),
        ('t', 0.27),
        ('B', 0.02),
        ('D', 0.02),
        ('H', 0.02),
        ('K', 0.02),
        ('M', 0.02),
        ('N', 0.02),
        ('R', 0.02),
        ('S', 0.02),
        ('V', 0.02),
        ('W', 0.02),
        ('Y', 0.02),
    ]
    
    # Homo sapiens frequency
    homosapiens = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008),
    ]
    
    # Generate sequences
    make_repeat_fasta('ONE', 'Homo sapiens alu', alu, n * 2)
    make_random_fasta('TWO', 'IUB ambiguity codes', iub, n * 3)
    make_random_fasta_numpy('THREE', 'Homo sapiens frequency', homosapiens, n * 5)

if __name__ == '__main__':
    main()
