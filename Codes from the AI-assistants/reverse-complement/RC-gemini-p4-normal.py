import sys

def solve_reverse_complement():
    # Native translation table for all IUPAC ambiguity codes
    # Mapping follows: A->T, C->G, G->C, T/U->A, M->K, R->Y, W->W, etc.
    trans_table = bytes.maketrans(
        b"ACGTUMRWSYKVHDBNacgtumrwsykvhdbn",
        b"TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn"
    )

    def process_sequence(header, sequence_data):
        if not header:
            return
        
        # 1. Output the header exactly as received
        sys.stdout.buffer.write(header + b"\n")
        
        # 2. Join the byte fragments and compute reverse complement
        # We use bytearray for efficient in-place reversal
        full_seq = bytearray(b"".join(sequence_data))
        full_seq = full_seq.translate(trans_table)[::-1]
        
        # 3. Write out in FASTA format (60 chars per line)
        for i in range(0, len(full_seq), 60):
            sys.stdout.buffer.write(full_seq[i:i+60] + b"\n")

    current_header = None
    current_sequence = []

    # Read from stdin line by line (Buffered)
    for line in sys.stdin.buffer:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith(b">"):
            # New sequence found: process the previous one first
            process_sequence(current_header, current_sequence)
            current_header = line
            current_sequence = []
        else:
            current_sequence.append(line)

    # Process the final sequence in the file
    process_sequence(current_header, current_sequence)

if __name__ == "__main__":
    solve_reverse_complement()