import sys

IM = 139968
IA = 3877
IC = 29573
SEED = 42

def random_next(max_val=1.0):
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

alu = (
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
)

iub_table = {
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

homosapiens_table = {
    'a': 0.3029549426680,
    'c': 0.1979883004921,
    'g': 0.1975473066391,
    't': 0.3015094502008
}

def make_cumulative(table):
    cumulative = []
    current = 0.0
    for char, prob in table.items():
        current += prob
        cumulative.append((current, char))
    return cumulative

iub_cumulative = make_cumulative(iub_table)
homosapiens_cumulative = make_cumulative(homosapiens_table)

def repeat_fasta(seq, size):
    seq_len = len(seq)
    n = size
    pos = 0
    while n > 0:
        line_length = min(60, n)
        line = []
        for j in range(line_length):
            line.append(seq[pos % seq_len])
            pos += 1
        print(''.join(line))
        n -= line_length

def random_fasta(cumulative_table, size):
    n = size
    while n > 0:
        line_length = min(60, n)
        line = []
        for j in range(line_length):
            r = random_next(1.0)
            for cum, char in cumulative_table:
                if r <= cum:
                    line.append(char)
                    break
        print(''.join(line))
        n -= line_length

def main():
    global SEED
    if len(sys.argv) < 2:
        n = 25000000
    else:
        n = int(sys.argv[1])
    
    total = n
    alu_size = (2 * total) // 10
    iub_size = (3 * total) // 10
    homosapiens_size = total - alu_size - iub_size
    
    SEED = 42
    
    print(">ONE Homo sapiens alu")
    repeat_fasta(alu, alu_size)
    
    print(">TWO IUB ambiguity codes")
    random_fasta(iub_cumulative, iub_size)
    
    print(">THREE Homo sapiens frequency")
    random_fasta(homosapiens_cumulative, homosapiens_size)

if __name__ == "__main__":
    main()