import sys
import argparse

def validate_dna_sequence(sequence):
    """Validate that the input contains only valid DNA nucleotides."""
    valid_chars = {'A', 'T', 'C', 'G', 'a', 't', 'c', 'g'}
    return all(c in valid_chars for c in sequence)

def reverse_complement(sequence):
    """
    Compute the reverse complement of a DNA sequence.
    
    Args:
        sequence (str): Input DNA sequence
        
    Returns:
        str: Reverse complement of the input sequence
    """
    # Create translation table for complementation
    complement_trans = str.maketrans('ATCGatcg', 'TAGCtagc')
    
    # Reverse the sequence and translate
    return sequence[::-1].translate(complement_trans)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Compute the reverse complement of a DNA sequence.'
    )
    parser.add_argument(
        'sequence', 
        nargs='?',
        help='DNA sequence to process (can also be provided via stdin)'
    )
    parser.add_argument(
        '-f', '--file',
        help='Input file containing DNA sequence'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file to save results'
    )
    
    args = parser.parse_args()
    
    # Get input sequence
    if args.file:
        try:
            with open(args.file, 'r') as f:
                sequence = f.read().strip()
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():  # Check if there's piped input
        sequence = sys.stdin.read().strip()
    elif args.sequence:
        sequence = args.sequence
    else:
        parser.print_help()
        sys.exit(1)
    
    # Remove any whitespace from sequence
    sequence = ''.join(sequence.split())
    
    # Validate sequence
    if not sequence:
        print("Error: Empty sequence provided", file=sys.stderr)
        sys.exit(1)
    
    if not validate_dna_sequence(sequence):
        print("Error: Sequence contains invalid characters. Only A, T, C, G are allowed.", file=sys.stderr)
        sys.exit(1)
    
    # Compute reverse complement
    try:
        result = reverse_complement(sequence)
    except Exception as e:
        print(f"Error computing reverse complement: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(result)
        except IOError as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(result)

if __name__ == '__main__':
    main()