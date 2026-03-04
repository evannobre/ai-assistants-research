import sys
from collections import defaultdict
import io

class ReverseComplement:
    def __init__(self):
        # Dictionary for complement lookup (including ambiguous bases)
        self.complement_map = {
            'A': 'T', 'T': 'A', 'U': 'A',
            'C': 'G', 'G': 'C',
            'M': 'K', 'K': 'M',
            'R': 'Y', 'Y': 'R',
            'W': 'W', 'S': 'S',
            'V': 'B', 'B': 'V',
            'H': 'D', 'D': 'H',
            'N': 'N',
            # Handle lowercase bases too
            'a': 't', 't': 'a', 'u': 'a',
            'c': 'g', 'g': 'c',
            'm': 'k', 'k': 'm',
            'r': 'y', 'y': 'r',
            'w': 'w', 's': 's',
            'v': 'b', 'b': 'v',
            'h': 'd', 'd': 'h',
            'n': 'n'
        }
        
        # Create translation table for str.translate() - faster than dict lookup
        # First build ASCII table for all 256 characters
        self.trans_table = bytearray(256)
        for i in range(256):
            self.trans_table[i] = i
        
        # Update with complement mappings
        for key, value in self.complement_map.items():
            self.trans_table[ord(key)] = ord(value)
            self.trans_table[ord(key.lower())] = ord(value.lower())
        
        self.trans_table = bytes(self.trans_table)
    
    def reverse_complement(self, sequence: str) -> str:
        """Return reverse complement of DNA sequence."""
        # Translate complements, then reverse
        complemented = sequence.translate(self.trans_table)
        return complemented[::-1]
    
    def process_fasta(self):
        """Process FASTA from stdin line by line."""
        buffer = []
        current_header = None
        writer = io.StringIO()
        
        for line in sys.stdin:
            line = line.rstrip('\n')
            
            if line.startswith('>'):
                # Process previous sequence if exists
                if current_header is not None and buffer:
                    sequence = ''.join(buffer)
                    rev_comp = self.reverse_complement(sequence)
                    
                    # Write to output
                    writer.write(current_header + '\n')
                    
                    # Write in FASTA format (max 60 chars per line)
                    for i in range(0, len(rev_comp), 60):
                        writer.write(rev_comp[i:i+60] + '\n')
                
                # Start new sequence
                current_header = line
                buffer = []
            else:
                # Accumulate sequence data
                if line:  # Skip empty lines
                    buffer.append(line)
        
        # Process last sequence
        if current_header is not None and buffer:
            sequence = ''.join(buffer)
            rev_comp = self.reverse_complement(sequence)
            
            writer.write(current_header + '\n')
            for i in range(0, len(rev_comp), 60):
                writer.write(rev_comp[i:i+60] + '\n')
        
        # Write all output at once
        sys.stdout.write(writer.getvalue())

def main():
    rc = ReverseComplement()
    rc.process_fasta()

if __name__ == "__main__":
    main()