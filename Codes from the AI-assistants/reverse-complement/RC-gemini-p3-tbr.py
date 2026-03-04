import sys

def build_translation_table():
    """
    Creates a translation table for DNA/IUPAC codes using bytes.
    """
    # Define the mapping based on the prompt
    mapping = {
        'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A',
        'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S', 'Y': 'R',
        'K': 'M', 'V': 'B', 'H': 'D', 'D': 'H', 'B': 'V', 'N': 'N',
        # Lowercase support (standard practice for robustness)
        'a': 'T', 'c': 'G', 'g': 'C', 't': 'A', 'u': 'A',
        'm': 'K', 'r': 'Y', 'w': 'W', 's': 'S', 'y': 'R',
        'k': 'M', 'v': 'B', 'h': 'D', 'd': 'H', 'b': 'V', 'n': 'N'
    }
    
    # Initialize a table where every byte maps to itself
    tb = bytearray(range(256))
    
    # Update the table with the specific complements
    for k, v in mapping.items():
        tb[ord(k)] = ord(v)
        
    return bytes(tb)

def process_sequence(header, sequence_parts, translation_table):
    """
    Reverses, complements, and prints the sequence.
    """
    # 1. Join the parts (grow the data)
    full_seq = b''.join(sequence_parts)
    
    # 2. Reverse (slicing with step -1) and Translate
    # Python performs this very efficiently in C under the hood
    rev_comp = full_seq[::-1].translate(translation_table)
    
    # 3. Print Header
    sys.stdout.buffer.write(header)
    
    # 4. Print Data (Formatted: 60 characters per line is standard FASTA)
    # We write directly to the buffered stdout for speed
    for i in range(0, len(rev_comp), 60):
        sys.stdout.buffer.write(rev_comp[i:i+60] + b'\n')

def main():
    translation_table = build_translation_table()
    
    sequence_parts = []
    header = None
    
    # Read stdin line-by-line (buffered read)
    # sys.stdin.buffer reads raw bytes, avoiding encoding overhead
    for line in sys.stdin.buffer:
        # Check for FASTA header
        if line.startswith(b'>'):
            # If we have a previous sequence accumulated, process it
            if header:
                process_sequence(header, sequence_parts, translation_table)
                sequence_parts = [] # Reset buffer
            
            header = line
        else:
            # Accumulate sequence lines (stripping newline at the end)
            # strictly, we just strip the newline char (10)
            if line.endswith(b'\n'):
                sequence_parts.append(line[:-1])
            else:
                sequence_parts.append(line)

    # Process the final sequence after the loop ends
    if header and sequence_parts:
        process_sequence(header, sequence_parts, translation_table)

if __name__ == "__main__":
    main()