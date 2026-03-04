import sys

COMPLEMENT_MAP = {
    'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'U': 'A',
    'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R', 'W': 'W',
    'S': 'S', 'V': 'B', 'B': 'V', 'H': 'D', 'D': 'H',
    'N': 'N'
}

def process_and_print_sequence(header, sequence_lines_list):
    if header is None or not sequence_lines_list:
        return

    full_sequence = "".join(sequence_lines_list)
    # It's good practice to convert to uppercase if not already guaranteed
    uppercase_sequence = full_sequence.upper()
    
    reversed_sequence = uppercase_sequence[::-1]
    
    complemented_chars = [COMPLEMENT_MAP.get(base, base) for base in reversed_sequence]
    reverse_complement_sequence = "".join(complemented_chars)
    
    print(header)
    line_width = 60
    for i in range(0, len(reverse_complement_sequence), line_width):
        print(reverse_complement_sequence[i:i+line_width])

current_header = None
current_sequence_lines = []

for line in sys.stdin:
    line = line.strip()
    if not line:  # Skip empty lines
        continue

    if line.startswith(">"):
        # Process the previous sequence
        process_and_print_sequence(current_header, current_sequence_lines)
        
        # Start a new sequence
        current_header = line
        current_sequence_lines = []
    else:
        current_sequence_lines.append(line)

# Process the last sequence in the file
process_and_print_sequence(current_header, current_sequence_lines)