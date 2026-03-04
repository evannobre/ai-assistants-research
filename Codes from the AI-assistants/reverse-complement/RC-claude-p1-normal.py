#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
Reads a DNA sequence from a file and outputs its reverse complement.
Uses native Python libraries for maximum efficiency.
"""

import sys
import argparse
from pathlib import Path


def reverse_complement(dna_sequence):
    """
    Calculate the reverse complement of a DNA sequence.
    
    Uses str.translate() with str.maketrans() for O(n) performance.
    This is the fastest native Python approach.
    
    Args:
        dna_sequence: String containing DNA sequence (A, T, G, C, N)
    
    Returns:
        Reverse complement of the input sequence
    """
    # Define complement mapping (supports both upper and lowercase)
    complement_map = str.maketrans(
        'ATGCNatgcn',
        'TACGNtacgn'
    )
    
    # Translate to complement, then reverse using slice notation
    return dna_sequence.translate(complement_map)[::-1]


def read_fasta(file_path):
    """
    Read DNA sequences from a FASTA file.
    
    Args:
        file_path: Path to FASTA file
    
    Yields:
        Tuples of (header, sequence)
    """
    with open(file_path, 'r') as f:
        header = None
        sequence_parts = []
        
        for line in f:
            line = line.rstrip()
            
            if line.startswith('>'):
                # If we have a previous sequence, yield it
                if header is not None:
                    yield header, ''.join(sequence_parts)
                
                # Start new sequence
                header = line[1:]  # Remove '>' character
                sequence_parts = []
            else:
                # Accumulate sequence lines
                sequence_parts.append(line)
        
        # Yield the last sequence
        if header is not None:
            yield header, ''.join(sequence_parts)


def read_raw_sequence(file_path):
    """
    Read a raw DNA sequence from a file (non-FASTA format).
    Removes whitespace and newlines.
    
    Args:
        file_path: Path to sequence file
    
    Returns:
        DNA sequence as a string
    """
    with open(file_path, 'r') as f:
        # Read all lines and join, removing whitespace
        return ''.join(line.strip() for line in f if not line.startswith('>'))


def validate_dna_sequence(sequence):
    """
    Validate that a sequence contains only valid DNA characters.
    
    Args:
        sequence: DNA sequence string
    
    Returns:
        True if valid, False otherwise
    """
    valid_chars = set('ATGCNatgcn')
    return all(char in valid_chars for char in sequence)


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='Calculate reverse complement of DNA sequences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sequence.txt
  %(prog)s sequence.fasta --fasta
  %(prog)s sequence.txt --output result.txt
  %(prog)s sequence.txt --validate
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Input DNA sequence file'
    )
    
    parser.add_argument(
        '-f', '--fasta',
        action='store_true',
        help='Input file is in FASTA format'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '-v', '--validate',
        action='store_true',
        help='Validate DNA sequence before processing'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show sequence statistics'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Determine output stream
    output_file = open(args.output, 'w') if args.output else sys.stdout
    
    try:
        if args.fasta:
            # Process FASTA file
            for header, sequence in read_fasta(input_path):
                if args.validate and not validate_dna_sequence(sequence):
                    print(f"Warning: Invalid characters in sequence '{header}'", 
                          file=sys.stderr)
                    continue
                
                rev_comp = reverse_complement(sequence)
                
                # Output in FASTA format
                print(f">{header} (reverse complement)", file=output_file)
                
                # Format sequence in 80-character lines (standard FASTA)
                for i in range(0, len(rev_comp), 80):
                    print(rev_comp[i:i+80], file=output_file)
                
                if args.stats:
                    print(f"Length: {len(sequence)} bp", file=sys.stderr)
        else:
            # Process raw sequence file
            sequence = read_raw_sequence(input_path)
            
            if args.validate and not validate_dna_sequence(sequence):
                print("Error: Invalid characters in DNA sequence.", file=sys.stderr)
                print("Valid characters: A, T, G, C, N (case insensitive)", file=sys.stderr)
                sys.exit(1)
            
            rev_comp = reverse_complement(sequence)
            print(rev_comp, file=output_file)
            
            if args.stats:
                from collections import Counter
                counts = Counter(sequence.upper())
                print(f"\nSequence Statistics:", file=sys.stderr)
                print(f"Length: {len(sequence)} bp", file=sys.stderr)
                print(f"A: {counts.get('A', 0)}, T: {counts.get('T', 0)}, "
                      f"G: {counts.get('G', 0)}, C: {counts.get('C', 0)}", 
                      file=sys.stderr)
                
                gc_content = (counts.get('G', 0) + counts.get('C', 0)) / len(sequence) * 100
                print(f"GC Content: {gc_content:.2f}%", file=sys.stderr)
    
    finally:
        if args.output:
            output_file.close()


if __name__ == '__main__':
    main()
