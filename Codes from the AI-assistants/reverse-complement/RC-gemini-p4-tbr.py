import sys

def main():
    """
    Reads FASTA from stdin, calculates reverse complement, and writes to stdout.
    Optimized for buffered I/O and efficient string manipulation.
    """
    
    # 1. Setup Translation Table
    # We map the IUPAC nucleotide codes to their complements.
    # We handle both upper and lower case for robustness, though FASTA is usually upper.
    # ASCII codes: A=65, C=67, etc.
    
    # Base pairs
    pairs = {
        b'A': b'T', b'C': b'G', b'G': b'C', b'T': b'A', b'U': b'A',
        b'M': b'K', b'R': b'Y', b'W': b'W', b'S': b'S', b'Y': b'R',
        b'K': b'M', b'V': b'B', b'H': b'D', b'D': b'H', b'B': b'V',
        b'N': b'N',
        # Lowercase support
        b'a': b'T', b'c': b'G', b'g': b'C', b't': b'A', b'u': b'A',
        b'm': b'K', b'r': b'Y', b'w': b'W', b's': b'S', b'y': b'R',
        b'k': b'M', b'v': b'B', b'h': b'D', b'd': b'H', b'b': b'V',
        b'n': b'N'
    }

    # Create a translation table of 256 bytes.
    # Initialize with identity map (0->0, 1->1...)
    tb = bytearray(range(256))
    
    # Update the table with our specific mapping
    for k, v in pairs.items():
        tb[ord(k)] = ord(v)
        
    trans_table = bytes(tb)
    
    # 2. I/O Setup
    # Use binary stdin/stdout for performance (avoids encoding/decoding overhead)
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    
    # Buffer to hold sequence chunks (list of bytes is faster to append to than string concatenation)
    seq_buffer = []
    
    # 3. Processing Loop
    for line in stdin:
        # Check if line is a header (starts with '>')
        if line.startswith(b'>'):
            # If we have a previous sequence buffered, process it now
            if seq_buffer:
                process_sequence(seq_buffer, trans_table, stdout)
                seq_buffer.clear()
            
            # Write the current header immediately
            stdout.write(line)
        else:
            # It's sequence data: strip newline and add to buffer
            # rstrip() removes trailing newline characters (\n or \r\n)
            seq_buffer.append(line.strip())

    # 4. Handle the Final Sequence
    # After the loop finishes, the last sequence is still in the buffer
    if seq_buffer:
        process_sequence(seq_buffer, trans_table, stdout)

def process_sequence(buffer, table, out):
    """
    Joins the buffer, performs reverse complement, formats to 60-char lines, and writes.
    """
    # Join all chunks into one bytes object
    full_seq = b"".join(buffer)
    
    # ALGORITHM:
    # 1. Reverse the sequence (s[::-1])
    # 2. Translate characters (s.translate)
    # Note: Doing reverse first, then translate is functionally equivalent to 
    # translating then reversing, but Python's translate is very fast on bytes.
    rev_comp_seq = full_seq.translate(table)[::-1]
    
    # Output formatting: FASTA standard usually wraps lines at 60 characters.
    # Slicing is efficient in Python (doesn't copy data in memory for the slice view in some contexts, 
    # though writing does push bytes).
    width = 60
    length = len(rev_comp_seq)
    
    for i in range(0, length, width):
        out.write(rev_comp_seq[i:i+width] + b'\n')

if __name__ == "__main__":
    main()