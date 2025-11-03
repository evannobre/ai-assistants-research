import sys

def main(output_file, header, length, seed=42):
    a = 1103515245
    c = 12345
    m = 2**31
    
    with open(output_file, 'w') as f:
        f.write(f">{header}\n")
        nucleotides = []
        for _ in range(length):
            seed = (a * seed + c) % m
            base = seed & 0b11  # Efficient modulo 4 using bitmask
            nucleotide = 'ACGT'[base]
            nucleotides.append(nucleotide)
            if len(nucleotides) == 60:
                f.write(''.join(nucleotides) + '\n')
                nucleotides = []
        
        if nucleotides:
            f.write(''.join(nucleotides) + '\n')

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python fasta_sim.py <output_file> <header> <length> [seed]")
        sys.exit(1)
    
    output_file = sys.argv[1]
    header = sys.argv[2]
    length = int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 42
    
    main(output_file, header, length, seed)