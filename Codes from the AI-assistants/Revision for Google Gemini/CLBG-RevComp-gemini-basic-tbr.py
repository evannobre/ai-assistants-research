import sys

def reverse_complement():
    # 1. Map IUPAC codes (both uppercase and lowercase) to uppercase complements
    frm = b'ACGTUMRWSYKVHDBNacgtumrwsykvhdbn'
    to  = b'TGCAAKYWSRMBDHVNTGCAAKYWSRMBDHVN'
    
    # Create a 256-character C-optimized translation table
    trans_table = bytes.maketrans(frm, to)
    
    # 2. Use a bytearray to dynamically "grow the data" without pre-allocating size
    seq = bytearray()
    
    # 3. Read line-by-line via buffered binary I/O for maximum performance
    for line in sys.stdin.buffer:
        if line.startswith(b'>'):
            # If sequence data is queued up, process and flush it
            if seq:
                # Reverse in-place (highly memory efficient)
                seq.reverse()
                # Translate entire block in one C-level operation
                seq_trans = seq.translate(trans_table)
                
                # Write out in standard 60-character FASTA line width
                for i in range(0, len(seq_trans), 60):
                    sys.stdout.buffer.write(seq_trans[i:i+60] + b'\n')
                
                # Clear buffer for the next sequence
                seq.clear()
            
            # Print the header line (ID and description) immediately
            sys.stdout.buffer.write(line)
        else:
            # Strip newline/carriage returns and grow the sequence buffer
            seq.extend(line.rstrip(b'\n\r'))
            
    # 4. Don't forget to process the final sequence after EOF
    if seq:
        seq.reverse()
        seq_trans = seq.translate(trans_table)
        for i in range(0, len(seq_trans), 60):
            sys.stdout.buffer.write(seq_trans[i:i+60] + b'\n')

if __name__ == '__main__':
    reverse_complement()