import sys

def main():
    n = int(sys.argv[1])
    
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )
    
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
        ('Y', 0.02)
    ]
    
    homo_sapiens = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]
    
    def make_cumulative(prob_list):
        cumulative = []
        total = 0.0
        for char, prob in prob_list:
            total += prob
            cumulative.append((char, total))
        return cumulative
    
    iub_cumulative = make_cumulative(iub)
    hs_cumulative = make_cumulative(homo_sapiens)
    
    def make_random():
        seed = 42
        IM = 139968
        IA = 3877
        IC = 29573
        def random_next(max_val):
            nonlocal seed
            seed = (seed * IA + IC) % IM
            return max_val * seed / IM
        return random_next
    
    random_next = make_random()
    
    sys.stdout.write(">ONE\n")
    for i in range(0, len(alu), 60):
        sys.stdout.write(alu[i:i+60] + "\n")
    
    sys.stdout.write(">TWO\n")
    output_lines = []
    line = []
    for char in alu:
        r = random_next(1.0)
        if r < 0.01:
            r2 = random_next(1.0)
            for symbol, cum_prob in iub_cumulative:
                if r2 < cum_prob:
                    line.append(symbol)
                    break
        else:
            line.append(char)
        if len(line) == 60:
            output_lines.append(''.join(line))
            line = []
    if line:
        output_lines.append(''.join(line))
    for l in output_lines:
        sys.stdout.write(l + "\n")
    
    sys.stdout.write(">THREE\n")
    line = []
    for i in range(n):
        r = random_next(1.0)
        for symbol, cum_prob in hs_cumulative:
            if r < cum_prob:
                line.append(symbol)
                break
        if len(line) == 60:
            sys.stdout.write(''.join(line) + "\n")
            line = []
    if line:
        sys.stdout.write(''.join(line) + "\n")

if __name__ == "__main__":
    main()