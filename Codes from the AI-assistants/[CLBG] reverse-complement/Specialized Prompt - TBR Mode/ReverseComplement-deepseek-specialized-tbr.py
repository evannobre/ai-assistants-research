import sys

complement_map = {
    'A': 'T',
    'C': 'G',
    'G': 'C',
    'T': 'A',
    'U': 'A',
    'M': 'K',
    'R': 'Y',
    'W': 'W',
    'S': 'S',
    'Y': 'R',
    'K': 'M',
    'V': 'B',
    'H': 'D',
    'D': 'H',
    'B': 'V',
    'N': 'N'
}

OUTPUT_LINE_LENGTH = 60

def main():
    current_header = None
    current_sequence_lines = []
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if current_header is not None:
                seq_str = ''.join(current_sequence_lines).upper()
                print(current_header)
                current_chunk = []
                for i in range(len(seq_str)-1, -1, -1):
                    base = seq_str[i]
                    comp_base = complement_map.get(base, 'N')
                    current_chunk.append(comp_base)
                    if len(current_chunk) == OUTPUT_LINE_LENGTH:
                        print(''.join(current_chunk))
                        current_chunk = []
                if current_chunk:
                    print(''.join(current_chunk))
            current_header = line
            current_sequence_lines = []
        else:
            current_sequence_lines.append(line)
    
    if current_header is not None:
        seq_str = ''.join(current_sequence_lines).upper()
        print(current_header)
        current_chunk = []
        for i in range(len(seq_str)-1, -1, -1):
            base = seq_str[i]
            comp_base = complement_map.get(base, 'N')
            current_chunk.append(comp_base)
            if len(current_chunk) == OUTPUT_LINE_LENGTH:
                print(''.join(current_chunk))
                current_chunk = []
        if current_chunk:
            print(''.join(current_chunk))

if __name__ == "__main__":
    main()