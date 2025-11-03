import sys

def create_complement_map():
    return {
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

def reverse_complement(sequence, complement_map):
    # Reverse the sequence and complement each base
    return ''.join([complement_map.get(base, base) for base in reversed(sequence)])

def process_fasta(input_stream, output_stream):
    complement_map = create_complement_map()
    current_header = None
    current_sequence = []
    
    for line in input_stream:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('>'):
            # Output previous sequence if exists
            if current_header is not None:
                rev_comp = reverse_complement(''.join(current_sequence), complement_map)
                output_stream.write(current_header + '\n')
                output_stream.write(rev_comp + '\n')
            
            # Start new sequence
            current_header = line
            current_sequence = []
        else:
            current_sequence.append(line)
    
    # Output the last sequence
    if current_header is not None:
        rev_comp = reverse_complement(''.join(current_sequence), complement_map)
        output_stream.write(current_header + '\n')
        output_stream.write(rev_comp + '\n')

if __name__ == "__main__":
    process_fasta(sys.stdin, sys.stdout)