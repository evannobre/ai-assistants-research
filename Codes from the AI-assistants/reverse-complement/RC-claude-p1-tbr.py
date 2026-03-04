#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
Computes the reverse complement of DNA sequences from a file.
Uses native Python libraries for maximum efficiency.
"""

import sys
import argparse
from pathlib import Path


def reverse_complement(dna_sequence):
    """
    Compute the reverse complement of a DNA sequence.
    
    Uses Python's str.translate() with str.maketrans() for O(n) performance.
    This is faster than iterating character by character.
    
    Args:
        dna_sequence: String containing DNA sequence (A, T, G, C, N)
    
    Returns:
        Reverse complement of the input sequence
    """
    # Create translation table using native str.maketrans()
    # This creates a mapping for efficient character replacement
    complement_table = str.maketrans('ATGCNatgcn', 'TACGNtacgn')
    
    # Apply complement using translate(), then reverse using slice notation
    # Both operations are highly optimized in Python's C implementation
    return dna_sequence.translate(complement_table)[::-1]


def process_fasta_file(filepath):
    """
    Process a FASTA format file and compute reverse complements.
    
    Args:
        filepath: Path to the FASTA file
    
    Yields:
        Tuples of (header, original_sequence, reverse_complement)
    """
    with open(filepath, 'r') as f:
        header = None
        sequence = []
        
        for line in f:
            line = line.strip()
            
            if not line:
                continue
                
            if line.startswith('>'):
                # Process previous sequence if exists
                if header is not None:
                    seq = ''.join(sequence)
                    yield (header, seq, reverse_complement(seq))
                
                # Start new sequence
                header = line[1:]  # Remove '>'
                sequence = []
            else:
                sequence.append(line)
        
        # Process last sequence
        if header is not None:
            seq = ''.join(sequence)
            yield (header, seq, reverse_complement(seq))


def process_raw_file(filepath):
    """
    Process a raw DNA sequence file (one sequence per line or continuous).
    
    Args:
        filepath: Path to the file
    
    Returns:
        Tuple of (original_sequence, reverse_complement)
    """
    with open(filepath, 'r') as f:
        # Read entire file and join lines, removing whitespace
        sequence = ''.join(line.strip() for line in f)
    
    return (sequence, reverse_complement(sequence))


def validate_dna_sequence(sequence, allow_n=True):
    """
    Validate that a sequence contains only valid DNA characters.
    
    Args:
        sequence: DNA sequence string
        allow_n: Whether to allow 'N' (unknown nucleotide)
    
    Returns:
        True if valid, False otherwise
    """
    valid_chars = set('ATGCatgc')
    if allow_n:
        valid_chars.update('Nn')
    
    return all(c in valid_chars for c in sequence)


def main():
    parser = argparse.ArgumentParser(
        description='Compute reverse complement of DNA sequences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sequence.fasta
  %(prog)s sequence.txt --raw
  %(prog)s sequence.fasta --output result.txt
  %(prog)s sequence.txt --raw --validate
        """
    )
    
    parser.add_argument('input_file', 
                       help='Input DNA file (FASTA or raw format)')
    parser.add_argument('--raw', action='store_true',
                       help='Treat input as raw sequence (not FASTA)')
    parser.add_argument('--output', '-o', 
                       help='Output file (default: stdout)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate DNA sequences contain only A,T,G,C,N')
    parser.add_argument('--stats', action='store_true',
                       help='Show sequence statistics')
    
    args = parser.parse_args()
    
    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Determine output destination
    output_file = open(args.output, 'w') if args.output else sys.stdout
    
    try:
        if args.raw:
            # Process raw format
            original, rev_comp = process_raw_file(input_path)
            
            if args.validate and not validate_dna_sequence(original):
                print("Warning: Sequence contains invalid DNA characters", 
                      file=sys.stderr)
            
            print("Original sequence:", file=output_file)
            print(original, file=output_file)
            print("\nReverse complement:", file=output_file)
            print(rev_comp, file=output_file)
            
            if args.stats:
                print(f"\nStatistics:", file=output_file)
                print(f"Length: {len(original)} bp", file=output_file)
                print(f"A: {original.upper().count('A')}", file=output_file)
                print(f"T: {original.upper().count('T')}", file=output_file)
                print(f"G: {original.upper().count('G')}", file=output_file)
                print(f"C: {original.upper().count('C')}", file=output_file)
        else:
            # Process FASTA format
            for header, original, rev_comp in process_fasta_file(input_path):
                if args.validate and not validate_dna_sequence(original):
                    print(f"Warning: Sequence '{header}' contains invalid DNA characters", 
                          file=sys.stderr)
                
                print(f">{header}", file=output_file)
                print(f"Original: {original}", file=output_file)
                print(f"Rev Comp: {rev_comp}", file=output_file)
                
                if args.stats:
                    print(f"Length: {len(original)} bp", file=output_file)
                
                print(file=output_file)  # Blank line between sequences
    
    finally:
        if args.output:
            output_file.close()


if __name__ == '__main__':
    main()
