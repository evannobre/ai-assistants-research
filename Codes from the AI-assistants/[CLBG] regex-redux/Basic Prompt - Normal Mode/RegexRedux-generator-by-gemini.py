# generate_fasta.py
import sys
import random

def generate_fasta(length):
    bases = ['a', 't', 'c', 'g']
    sys.stdout.write(">simulated_sequence\n")
    line_length = 60
    for i in range(length):
        sys.stdout.write(random.choice(bases))
        if (i + 1) % line_length == 0:
            sys.stdout.write("\n")
    sys.stdout.write("\n") # Ensure a final newline

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            length = int(sys.argv[1])
            generate_fasta(length)
        except ValueError:
            print("Usage: python generate_fasta.py <sequence_length>")
    else:
        print("Usage: python generate_fasta.py <sequence_length>")