#!/usr/bin/env python3
"""
FASTA Reverse Complement Algorithm
Optimized for memory efficiency and speed using native Python libraries
"""

import sys
from typing import Dict, Generator

# DNA/RNA complement mapping including ambiguous nucleotides
# Using a translation table for maximum performance
_COMPLEMENT_TABLE = str.maketrans({
    'A': 'T', 'T': 'A', 'U': 'A',  # Handle both DNA and RNA
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
})

def reverse_complement(sequence: str) -> str:
    """
    Generate reverse complement of a DNA/RNA sequence.
    
    Args:
        sequence: Input nucleotide sequence
        
    Returns:
        Reverse complement string
    """
    # Translate using complement table and reverse in one operation
    # Reverse first, then translate for better cache locality
    return sequence[::-1].translate(_COMPLEMENT_TABLE)

def read_fasta_chunks(file_obj, buffer_size: int = 8192) -> Generator[str, None, None]:
    """
    Generator to read FASTA data in buffered chunks.
    
    Args:
        file_obj: Input file object
        buffer_size: Size of read buffer in bytes
        
    Yields:
        Chunks of FASTA data as strings
    """
    while True:
        chunk = file_obj.read(buffer_size)
        if not chunk:
            break
        yield chunk

def process_fasta_stream() -> None:
    """
    Main processing function that reads FASTA from stdin line by line,
    processes sequences, and writes reverse complements to stdout.
    
    Memory efficient: Processes sequences chunk by chunk without loading
    entire file into memory.
    """
    # Use sys.stdin.buffer for binary reading (more efficient)
    # and sys.stdout for text writing
    import io
    
    current_id = ""
    current_desc = ""
    sequence_buffer = []
    
    # Buffer for building sequence lines
    line_buffer = []
    
    for line in sys.stdin:
        line = line.rstrip('\n\r')
        
        if not line:
            continue
            
        if line.startswith('>'):
            # Process previous sequence if exists
            if sequence_buffer or current_id:
                if sequence_buffer:
                    # Join all sequence parts, reverse complement, and write
                    full_sequence = ''.join(sequence_buffer)
                    revcomp = reverse_complement(full_sequence)
                    
                    # Write in FASTA format (60 chars per line)
                    sys.stdout.write(f">{current_id} {current_desc}\n")
                    for i in range(0, len(revcomp), 60):
                        sys.stdout.write(revcomp[i:i+60] + "\n")
                
                # Reset for new sequence
                sequence_buffer = []
            
            # Parse new header
            header = line[1:].strip()
            parts = header.split(maxsplit=1)
            current_id = parts[0]
            current_desc = parts[1] if len(parts) > 1 else ""
        else:
            # Accumulate sequence data
            sequence_buffer.append(line.upper())
    
    # Process the last sequence
    if sequence_buffer and current_id:
        full_sequence = ''.join(sequence_buffer)
        revcomp = reverse_complement(full_sequence)
        
        sys.stdout.write(f">{current_id} {current_desc}\n")
        for i in range(0, len(revcomp), 60):
            sys.stdout.write(revcomp[i:i+60] + "\n")

def main():
    """Main entry point."""
    try:
        process_fasta_stream()
    except BrokenPipeError:
        # Handle pipe closure gracefully (e.g., when piped to head)
        sys.stderr.close()
    except KeyboardInterrupt:
        sys.stderr.write("\nProcess interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()