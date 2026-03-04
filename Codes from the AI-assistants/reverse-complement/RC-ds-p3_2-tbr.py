import sys
import io

class ReverseComplementProcessor:
    def __init__(self):
        # Pre-compute translation tables for maximum speed
        self.complement_map = str.maketrans({
            'A': 'T', 'T': 'A', 'U': 'A', 'C': 'G', 'G': 'C',
            'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R', 'W': 'W',
            'S': 'S', 'V': 'B', 'B': 'V', 'H': 'D', 'D': 'H',
            'N': 'N',
            'a': 't', 't': 'a', 'u': 'a', 'c': 'g', 'g': 'c',
            'm': 'k', 'k': 'm', 'r': 'y', 'y': 'r', 'w': 'w',
            's': 's', 'v': 'b', 'b': 'v', 'h': 'd', 'd': 'h',
            'n': 'n'
        })
        
    def reverse_complement_fast(self, sequence):
        """Ultra-fast reverse complement using translation and slicing"""
        # Reverse and translate in one operation
        return sequence[::-1].translate(self.complement_map)
    
    def process(self):
        """Process input with minimal memory usage"""
        buffer_size = 128 * 1024  # 128KB buffer
        current_header = None
        sequence_chunks = []
        
        # Use binary reading for efficiency
        stdin_buffer = sys.stdin.buffer
        
        while True:
            # Read chunk
            chunk = stdin_buffer.read1(buffer_size)
            if not chunk:
                break
                
            # Decode chunk to text
            text_chunk = chunk.decode('utf-8', errors='replace')
            lines = text_chunk.split('\n')
            
            for i, line in enumerate(lines):
                if not line:
                    continue
                    
                if line.startswith('>'):
                    # Process previous sequence
                    if sequence_chunks:
                        full_seq = ''.join(sequence_chunks)
                        rev_comp = self.reverse_complement_fast(full_seq)
                        
                        # Output with 60 chars per line
                        sys.stdout.write(current_header + '\n')
                        for j in range(0, len(rev_comp), 60):
                            sys.stdout.write(rev_comp[j:j+60] + '\n')
                        
                        sequence_chunks = []
                    
                    current_header = line.rstrip('\r')
                else:
                    sequence_chunks.append(line.strip().upper())
        
        # Process final sequence
        if sequence_chunks:
            full_seq = ''.join(sequence_chunks)
            rev_comp = self.reverse_complement_fast(full_seq)
            
            sys.stdout.write(current_header + '\n')
            for j in range(0, len(rev_comp), 60):
                sys.stdout.write(rev_comp[j:j+60] + '\n')

def main():
    processor = ReverseComplementProcessor()
    processor.process()

if __name__ == "__main__":
    main()