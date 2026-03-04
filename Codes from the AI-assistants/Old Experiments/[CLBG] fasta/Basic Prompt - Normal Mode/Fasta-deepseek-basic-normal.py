import sys
from bisect import bisect

IM = 139968
IA = 3877
IC = 29573
Seed = 42

def random_max(max_val):
    global Seed
    Seed = (Seed * IA + IC) % IM
    return max_val * Seed / IM

def make_cumulative(table):
    cumulative = []
    cumul = 0.0
    for char, prob in table:
        cumul += prob
        cumulative.append((cumul, char))
    return cumulative

def random_to_char(random_val, cumulative):
    i = bisect(cumulative, (random_val,))
    return cumulative[i][1]

def repeat_fasta(src, n):
    width = 60
    r = len(src)
    s = src + src + src[:n % r]
    for j in range(n // width):
        i = j * width % r
        print(s[i:i+width])
    if n % width:
        print(s[-(n % width):])

def random_fasta(table, n):
    width = 60
    cumulative = make_cumulative(table)
    for j in range(n // width):
        line = []
        for _ in range(width):
            r = random_max(1.0)
            line.append(random_to_char(r, cumulative))
        print(''.join(line))
    remaining = n % width
    if remaining:
        line = []
        for _ in range(remaining):
            r = random_max(1.0)
            line.append(random_to_char(r, cumulative))
        print(''.join(line))

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    IUB = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]
    
    HomoSap = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]
    
    alu = (
        'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
        'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
        'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
        'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
        'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
        'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
        'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
    )
    
    print(f'>ONE Homo sapiens alu')
    repeat_fasta(alu, n*2)
    
    print(f'>TWO IUB ambiguity codes')
    random_fasta(IUB, n*3)
    
    print(f'>THREE Homo sapiens frequency')
    random_fasta(HomoSap, n*5)

if __name__ == '__main__':
    main()