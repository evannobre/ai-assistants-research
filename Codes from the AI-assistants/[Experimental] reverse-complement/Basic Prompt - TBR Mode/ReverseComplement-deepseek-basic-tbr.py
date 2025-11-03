import sys

def reverse_complement(dna):
    mapping = str.maketrans({
        'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
        'a': 't', 't': 'a', 'g': 'c', 'c': 'g'
    })
    reversed_dna = dna[::-1]
    return reversed_dna.translate(mapping)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reverse_complement.py <DNA_SEQUENCE>")
        sys.exit(1)
    dna_input = sys.argv[1]
    result = reverse_complement(dna_input)
    print(result)