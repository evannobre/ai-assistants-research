import sys

trans = str.maketrans("ATCGatcg", "TAGCtagc")

def revcomp(seq):
    return seq.translate(trans)[::-1]

def process_fasta(path):
    with open(path) as f:
        header = None
        seq_parts = []
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header:
                    print(header)
                    print(revcomp("".join(seq_parts)))
                header = line
                seq_parts = []
            else:
                seq_parts.append(line)
        if header:
            print(header)
            print(revcomp("".join(seq_parts)))

if __name__ == "__main__":
    process_fasta(sys.argv[1])
