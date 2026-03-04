import sys
from itertools import islice

# Constants for the LCG
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def random(max_val):
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

def make_cumulative(table):
    # Convert probability table to cumulative table without optimization
    cumulative = []
    total = 0.0
    for char, prob in table:
        total += prob
        cumulative.append((char, total))
    return cumulative

def random_char(cumulative):
    # Select random character using linear search
    r = random(1.0)
    for char, prob in cumulative:
        if r < prob:
            return char
    return cumulative[-1][0]  # fallback

def repeat_fasta(src, n):
    width = 60
    r = len(src)
    s = src + src + src[:n % r]
    for i in range(0, n, width):
        j = i + width
        print(s[i%r:j%r] if j%r else s[i%r:j%r] + '\n')

def random_fasta(table, n):
    width = 60
    cumulative = make_cumulative(table)
    buf = []
    for i in range(n):
        if i % width == 0 and i > 0:
            print(''.join(buf))
            buf = []
        buf.append(random_char(cumulative))
    if buf:
        print(''.join(buf))

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    # IUB ambiguity codes with probabilities
    iub = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]

    # Homo sapiens frequency
    homosapiens = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]

    # Reset seed for each sequence
    global SEED
    SEED = 42
    
    print(f'>ONE Homo sapiens alu')
    repeat_fasta(
        'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
        'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
        'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
        'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
        'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
        'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
        'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA',
        n*2
    )

    SEED = 42
    print(f'>TWO IUB ambiguity codes')
    random_fasta(iub, n*3)

    SEED = 42
    print(f'>THREE Homo sapiens frequency')
    random_fasta(homosapiens, n*5)

if __name__ == '__main__':
    main()