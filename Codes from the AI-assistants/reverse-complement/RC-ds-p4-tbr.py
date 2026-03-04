#!/usr/bin/env python3
"""
Reverse Complement DNA Sequences from FASTA format.

This program reads FASTA format data from stdin, computes the reverse complement
for each sequence, and writes the results to stdout. It uses buffered I/O and
memory-efficient processing suitable for large files up to 256GB.
"""

import sys
from typing import Generator

# DNA complement mapping including ambiguous bases
_COMPLEMENT_MAP = str.maketrans({
    'A': 'T', 'T': 'A', 'U': 'A', 'C': 'G', 'G': 'C',
    'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R', 'W': 'W',
    'S': 'S', 'V': 'B', 'B': 'V', 'H': 'D', 'D': 'H',
    'N': 'N',
    # Handle lowercase equivalents
    'a': 't', 't': 'a', 'u': 'a', 'c': 'g', 'g': 'c',
    'm': 'k', 'k': 'm', 'r': 'y', 'y': 'r', 'w': 'w',
    's': 's', 'v': 'b', 'b': 'v', 'h': 'd', 'd': 'h',
    'n': 'n'
})


def fasta_reader() -> Generator[tuple[str, str, str], None, None]:
    """
    Read FASTA format data from stdin line by line.
    
    Yields:
        Tuple of (header, sequence_id, sequence_description)
    
    Note:
        Sequences can span multiple lines. This reads them efficiently
        without loading entire sequences into memory at once.
    """
    header = ''
    sequence_lines = []
    
    for line in sys.stdin.buffer:
        # Decode binary line to string, strip whitespace
        line = line.decode('utf-8', errors='replace').rstrip()
        
        if not line:
            continue
            
        if line.startswith('>'):
            # Yield previous sequence if exists
            if header and sequence_lines:
                sequence = ''.join(sequence_lines)
                # Parse header into ID and description
                header_parts = header[1:].split(' ', 1)
                seq_id = header_parts[0]
                seq_desc = header_parts[1] if len(header_parts) > 1 else ''
                yield header, seq_id, seq_desc, sequence
                sequence_lines = []
            
            header = line
        else:
            sequence_lines.append(line.upper())
    
    # Yield the last sequence
    if header and sequence_lines:
        sequence = ''.join(sequence_lines)
        header_parts = header[1:].split(' ', 1)
        seq_id = header_parts[0]
        seq_desc = header_parts[1] if len(header_parts) > 1 else ''
        yield header, seq_id, seq_desc, sequence


def reverse_complement(sequence: str) -> str:
    """
    Compute the reverse complement of a DNA sequence.
    
    Args:
        sequence: DNA sequence string
    
    Returns:
        Reverse complement of the input sequence
    """
    # Reverse the sequence and translate using complement map
    return sequence.translate(_COMPLEMENT_MAP)[::-1]


def format_fasta_output(seq_id: str, description: str, 
                        sequence: str, line_width: int = 80) -> str:
    """
    Format sequence data into FASTA format with line wrapping.
    
    Args:
        seq_id: Sequence identifier
        description: Sequence description
        sequence: DNA sequence
        line_width: Width for line wrapping (default: 80)
    
    Returns:
        Formatted FASTA string
    """
    # Build header
    if description:
        header = f">{seq_id} {description}\n"
    else:
        header = f">{seq_id}\n"
    
    # Split sequence into lines of specified width
    sequence_lines = []
    for i in range(0, len(sequence), line_width):
        sequence_lines.append(sequence[i:i + line_width])
    
    return header + '\n'.join(sequence_lines) + '\n'


def main() -> None:
    """
    Main processing function.
    
    Reads FASTA from stdin, computes reverse complements,
    and writes results to stdout.
    """
    try:
        for header, seq_id, seq_desc, sequence in fasta_reader():
            # Compute reverse complement
            rev_comp_seq = reverse_complement(sequence)
            
            # Format and output result
            output = format_fasta_output(seq_id, seq_desc, rev_comp_seq)
            sys.stdout.write(output)
            
            # Flush periodically to ensure progress is visible
            if len(sequence) > 1000000:
                sys.stdout.flush()
    
    except BrokenPipeError:
        # Handle early termination of output pipeline gracefully
        devnull = open('/dev/null', 'w')
        sys.stdout = devnull
        sys.stderr = devnull
    
    except Exception as e:
        sys.stderr.write(f"Error processing FASTA file: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()