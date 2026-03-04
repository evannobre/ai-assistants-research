import sys

COMPLEMENT_MAP = {
    'A': 'T', 'T': 'A', 'U': 'A', 'C': 'G', 'G': 'C',
    'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R', 'W': 'W',
    'S': 'S', 'B': 'V', 'V': 'B', 'H': 'D', 'D': 'H',
    'N': 'N'
}
# For real implementation, consider a direct array lookup for speed
# complement_array = [''] * 128
# for char, comp in COMPLEMENT_MAP.items():
#     complement_array[ord(char)] = comp
# etc.

BUFFER_SIZE = 4096 # bytes
FASTA_LINE_WRAP_LENGTH = 60

def reverse_complement_simulation():
    current_header = ""
    current_sequence_chars = [] # Using a list for efficient appends

    # Use sys.stdin.buffer and sys.stdout.buffer for binary I/O
    # and manual decoding/encoding for max control over buffering.
    # For simplicity, using text-based sys.stdin/stdout here, but
    # performance critical code would go lower-level.

    for line in sys.stdin:
        line = line.strip() # Remove newline and leading/trailing whitespace

        if line.startswith('>'):
            if current_sequence_chars:
                # Process the previous sequence
                process_and_write_sequence(current_header, current_sequence_chars)
                current_sequence_chars = [] # Reset for next sequence
            current_header = line
        else:
            # Accumulate sequence characters (convert to uppercase for robustness)
            current_sequence_chars.extend(char.upper() for char in line)

    # Process the last sequence after the loop finishes
    if current_sequence_chars:
        process_and_write_sequence(current_header, current_sequence_chars)

def process_and_write_sequence(header, sequence_chars):
    sys.stdout.write(header + '\n')

    # 1. Reverse the sequence
    reversed_sequence_chars = sequence_chars[::-1] # Pythonic reverse

    # 2. Complement the reversed sequence
    #    Use a pre-allocated list for efficiency
    reverse_complement_chars = [None] * len(reversed_sequence_chars)
    for i, char in enumerate(reversed_sequence_chars):
        reverse_complement_chars[i] = COMPLEMENT_MAP.get(char, char) # Handle unknown chars gracefully

    # 3. Format and write to stdout
    chars_written = 0
    for char in reverse_complement_chars:
        sys.stdout.write(char)
        chars_written += 1
        if chars_written % FASTA_LINE_WRAP_LENGTH == 0:
            sys.stdout.write('\n')
    if chars_written % FASTA_LINE_WRAP_LENGTH != 0: # Ensure newline at the end if not perfectly wrapped
        sys.stdout.write('\n')

# To run this:
# python your_script.py < input25000000.txt > output25000000.fasta