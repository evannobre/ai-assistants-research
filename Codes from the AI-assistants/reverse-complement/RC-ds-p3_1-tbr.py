import sys
import io

def build_complement_table():
    """Build a translation table for complement conversion"""
    # Create translation table for standard bases
    complements = {
        'A': 'T', 'T': 'A', 'U': 'A',
        'C': 'G', 'G': 'C',
        'M': 'K', 'K': 'M',
        'R': 'Y', 'Y': 'R',
        'W': 'W', 'S': 'S',
        'V': 'B', 'B': 'V',
        'H': 'D', 'D': 'H',
        'N': 'N',
        'a': 't', 't': 'a', 'u': 'a',
        'c': 'g', 'g': 'c',
        'm': 'k', 'k': 'm',
        'r': 'y', 'y': 'r',
        'w': 'w', 's': 's',
        'v': 'b', 'b': 'v',
        'h': 'd', 'd': 'h',
        'n': 'n'
    }
    return complements

def reverse_complement(sequence, complement_table):
    """Generate reverse complement of a sequence"""
    # Using list comprehension for efficiency
    return ''.join(complement_table.get(base, base) for base in reversed(sequence))

def process_fasta_stream():
    """Process FASTA from stdin line by line, write to stdout"""
    complement_table = build_complement_table()
    buffer_size = 64 * 1024  # 64KB buffer
    
    # Use sys.stdin.buffer for binary reading (more efficient)
    with io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8') as infile:
        current_id = None
        current_desc = None
        sequence_parts = []
        line_buffer = []
        
        for line in infile:
            line = line.rstrip('\n')
            
            if line.startswith('>'):
                # Process previous sequence if exists
                if sequence_parts:
                    # Join all sequence parts and get reverse complement
                    full_sequence = ''.join(sequence_parts)
                    rev_comp = reverse_complement(full_sequence, complement_table)
                    
                    # Write in FASTA format (typically 60 chars per line)
                    sys.stdout.write(f'>{current_id} {current_desc}\n')
                    for i in range(0, len(rev_comp), 60):
                        sys.stdout.write(rev_comp[i:i+60] + '\n')
                    
                    sequence_parts = []
                    line_buffer = []
                
                # Parse new header
                header = line[1:].strip()
                if ' ' in header:
                    current_id, current_desc = header.split(' ', 1)
                else:
                    current_id = header
                    current_desc = ''
            else:
                # Add sequence line
                sequence_parts.append(line)
        
        # Process the last sequence
        if sequence_parts:
            full_sequence = ''.join(sequence_parts)
            rev_comp = reverse_complement(full_sequence, complement_table)
            
            sys.stdout.write(f'>{current_id} {current_desc}\n')
            for i in range(0, len(rev_comp), 60):
                sys.stdout.write(rev_comp[i:i+60] + '\n')

def main():
    """Main entry point"""
    process_fasta_stream()

if __name__ == "__main__":
    main()