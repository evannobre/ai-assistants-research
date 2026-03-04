import sys  

def reverse_complement(dna_sequence: str) -> str:  
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}  
    return "".join(complement[base] for base in reversed(dna_sequence))  

if __name__ == "__main__":  
    if len(sys.argv) != 2:  
        print("Usage: python3 reverse_complement.py <DNA_sequence>")  
        sys.exit(1)  

    dna_seq = sys.argv[1].upper()  
    if not set(dna_seq).issubset({'A', 'T', 'C', 'G'}):  
        print("Invalid DNA sequence: Use only A, T, C, and G")  
        sys.exit(1)  

    print(reverse_complement(dna_seq))  
