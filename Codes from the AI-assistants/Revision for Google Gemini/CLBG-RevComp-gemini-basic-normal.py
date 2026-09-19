import sys

def reverse_complement():
    # 1. Create a native byte translation table for standard IUPAC codes.
    # We map both upper and lower case inputs to their uppercase complements.
    bases_in =  b'ACGTUMRWSYKVHDBNacgtumrwsykvhdbn'
    bases_out = b'TGCAAKYWSRMBDHVNTGCAAKYWSRMBDHVN'
    translation_table = bytes.maketrans(bases_in, bases_out)

    seq_parts = []
    
    def process_and_write():
        """Joins, reverses, translates, and writes the accumulated sequence."""
        if not seq_parts:
            return
            
        # Join all accumulated byte-lines into one byte string
        full_seq = b''.join(seq_parts)
        
        # Translate to complements, then reverse the entire sequence ([::-1])
        rev_comp = full_seq.translate(translation_table)[::-1]
        
        # Write sequence to stdout wrapped at 60 characters per line
        for i in range(0, len(rev_comp), 60):
            sys.stdout.buffer.write(rev_comp[i:i+60] + b'\n')
            
        # Clear the buffer for the next sequence
        seq_parts.clear()

    # 2. Buffered line-by-line read from standard input
    for line in sys.stdin.buffer:
        if line.startswith(b'>'):
            # If we hit a new FASTA header, process the previous sequence
            process_and_write()
            # Write the exact header (ID and description) to stdout
            sys.stdout.buffer.write(line)
        else:
            # Strip trailing whitespace/newlines (\r or \n) and accumulate
            seq_parts.append(line.rstrip())

    # 3. Process the final sequence after EOF
    process_and_write()

if __name__ == '__main__':
    # Ensure stdout handles buffering well for large data streams
    reverse_complement()