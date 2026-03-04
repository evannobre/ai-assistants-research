import sys

def main():
    complement_map = {
        'A': 'T', 
        'T': 'A', 
        'U': 'A',   
        'C': 'G', 
        'G': 'C', 
        'M': 'K', 
        'K': 'M', 
        'R': 'Y', 
        'Y': 'R', 
        'W': 'W', 
        'S': 'S', 
        'V': 'B', 
        'B': 'V', 
        'H': 'D', 
        'D': 'H', 
        'N': 'N'
    }
    
    current_header = None
    current_sequence_lines = []
    
    for line in sys.stdin:
        line = line.strip()
        if line.startswith('>'):
            if current_header is not None:
                seq_str = ''.join(current_sequence_lines)
                rev_seq = seq_str[::-1]
                rev_comp_list = [complement_map.get(base, base) for base in rev_seq]
                rev_comp = ''.join(rev_comp_list)
                print('>' + current_header)
                for i in range(0, len(rev_comp), 60):
                    print(rev_comp[i:i+60])
            current_header = line[1:]
            current_sequence_lines = []
        else:
            clean_line = ''.join(filter(str.isalpha, line)).upper()
            if clean_line:
                current_sequence_lines.append(clean_line)
                
    if current_header is not None:
        seq_str = ''.join(current_sequence_lines)
        rev_seq = seq_str[::-1]
        rev_comp_list = [complement_map.get(base, base) for base in rev_seq]
        rev_comp = ''.join(rev_comp_list)
        print('>' + current_header)
        for i in range(0, len(rev_comp), 60):
            print(rev_comp[i:i+60])

if __name__ == "__main__":
    main()