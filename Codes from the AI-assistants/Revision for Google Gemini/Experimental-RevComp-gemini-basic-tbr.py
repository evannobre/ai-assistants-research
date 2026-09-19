#!/usr/bin/env python3
import sys
import argparse

def get_reverse_complement(seq):
    """
    Translates a DNA sequence to its complement and reverses it.
    Includes extended IUPAC nucleotide codes for comprehensive support.
    """
    # Map each base to its complement (supports both upper and lower case)
    complement_map = str.maketrans(
        'ACGUTMRWSYKVHDBNacgutmrwsykvhdbn',
        'TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn'
    )
    
    # Translate the sequence and reverse it using slice notation [::-1]
    return seq.translate(complement_map)[::-1]

def process_fasta(file_path):
    """
    Reads a FASTA file, processes sequences, and outputs the reverse complement.
    """
    header = ""
    seq_chunks = []

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a FASTA header line
                if line.startswith('>'):
                    # If we already have a sequence queued, process and print it
                    if header:
                        full_seq = "".join(seq_chunks)
                        print(header)
                        rev_comp = get_reverse_complement(full_seq)
                        
                        # Print sequence wrapped to 80 characters per line
                        for i in range(0, len(rev_comp), 80):
                            print(rev_comp[i:i+80])
                    
                    # Reset for the new sequence
                    header = line
                    seq_chunks = []
                else:
                    seq_chunks.append(line)

            # Don't forget to process the final sequence in the file
            if header:
                full_seq = "".join(seq_chunks)
                print(header)
                rev_comp = get_reverse_complement(full_seq)
                for i in range(0, len(rev_comp), 80):
                    print(rev_comp[i:i+80])

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate the reverse complement of a DNA sequence in a FASTA file.")
    parser.add_argument("input_file", help="Path to the input DNA file (FASTA format)")
    args = parser.parse_args()

    process_fasta(args.input_file)