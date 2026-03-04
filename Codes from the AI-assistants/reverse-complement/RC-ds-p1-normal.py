#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
Usage: python reverse_complement.py <input_file.fasta> [output_file.fasta]
"""

import sys
import argparse
import gzip
from pathlib import Path
from typing import Dict, Tuple, Iterator
import time

class ReverseComplement:
    """Main class for reverse complement operations."""
    
    # DNA complement mapping using native dict
    DNA_COMPLEMENT = str.maketrans({
        'A': 'T', 'T': 'A', 
        'G': 'C', 'C': 'G',
        'a': 't', 't': 'a',
        'g': 'c', 'c': 'g',
        'N': 'N', 'n': 'n',
        'R': 'Y', 'Y': 'R',  # Purines (A,G) ↔ Pyrimidines (C,T)
        'r': 'y', 'y': 'r',
        'M': 'K', 'K': 'M',  # Amino (A,C) ↔ Keto (G,T)
        'm': 'k', 'k': 'm',
        'S': 'S', 's': 's',  # Strong (G,C)
        'W': 'W', 'w': 'w',  # Weak (A,T)
        'B': 'V', 'V': 'B',  # Not A ↔ Not T
        'D': 'H', 'H': 'D'   # Not C ↔ Not G
    })
    
    @staticmethod
    def reverse_complement_sequence(sequence: str) -> str:
        """
        Compute reverse complement of a DNA sequence.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Reverse complemented sequence
        """
        # Reverse the sequence and translate using complement mapping
        return sequence[::-1].translate(ReverseComplement.DNA_COMPLEMENT)
    
    @staticmethod
    def read_fasta(file_path: Path) -> Iterator[Tuple[str, str]]:
        """
        Read FASTA file yielding (header, sequence) pairs.
        Supports both plain text and gzipped files.
        
        Args:
            file_path: Path to FASTA file
            
        Yields:
            Tuples of (header, sequence)
        """
        # Detect if file is gzipped
        opener = gzip.open if file_path.suffix == '.gz' else open
        
        with opener(file_path, 'rt', encoding='utf-8') as f:
            header = None
            sequence_lines = []
            
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('>'):
                    # Yield previous sequence if exists
                    if header is not None:
                        yield header, ''.join(sequence_lines)
                    
                    # Start new sequence
                    header = line[1:]  # Remove '>'
                    sequence_lines = []
                else:
                    sequence_lines.append(line.upper())
            
            # Yield the last sequence
            if header is not None and sequence_lines:
                yield header, ''.join(sequence_lines)
    
    @staticmethod
    def write_fasta(file_path: Path, sequences: Iterator[Tuple[str, str]]) -> None:
        """
        Write sequences to FASTA file.
        
        Args:
            file_path: Output file path
            sequences: Iterator of (header, sequence) tuples
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            for header, sequence in sequences:
                f.write(f">{header}\n")
                
                # Write sequence in lines of 60 characters (standard FASTA format)
                for i in range(0, len(sequence), 60):
                    f.write(f"{sequence[i:i+60]}\n")
    
    def process_file(self, input_file: Path, output_file: Path = None) -> Dict[str, any]:
        """
        Process input FASTA file and generate reverse complement.
        
        Args:
            input_file: Input FASTA file path
            output_file: Output file path (optional)
            
        Returns:
            Dictionary with processing statistics
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        start_time = time.time()
        stats = {
            'sequences_processed': 0,
            'total_bases': 0,
            'processing_time': 0
        }
        
        # Generate reverse complemented sequences
        revcomp_sequences = []
        
        for header, sequence in self.read_fasta(input_file):
            revcomp_seq = self.reverse_complement_sequence(sequence)
            revcomp_sequences.append((f"{header}_reverse_complement", revcomp_seq))
            
            stats['sequences_processed'] += 1
            stats['total_bases'] += len(sequence)
        
        # Calculate processing time
        stats['processing_time'] = time.time() - start_time
        
        # Write output if requested
        if output_file:
            self.write_fasta(output_file, revcomp_sequences)
        
        return stats
    
    def print_stats(self, stats: Dict[str, any]) -> None:
        """Print processing statistics."""
        print("\n" + "="*50)
        print("PROCESSING STATISTICS")
        print("="*50)
        print(f"Sequences processed: {stats['sequences_processed']:,}")
        print(f"Total bases: {stats['total_bases']:,}")
        print(f"Processing time: {stats['processing_time']:.4f} seconds")
        
        if stats['sequences_processed'] > 0 and stats['processing_time'] > 0:
            print(f"Speed: {stats['total_bases']/stats['processing_time']:,.0f} bases/second")
        print("="*50)

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Compute reverse complement of DNA sequences in FASTA format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reverse_complement.py input.fasta
  python reverse_complement.py input.fasta output.fasta
  python reverse_complement.py input.fasta.gz -o output.fasta
  python reverse_complement.py -v input.fasta

Input format: Standard FASTA format (plain or gzipped)
Output: FASTA format with '_reverse_complement' appended to headers
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input FASTA file (can be .fasta, .fa, .fna, or .gz)'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Output FASTA file (optional, prints to console if not specified)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file_alt',
        help='Alternative way to specify output file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print processing statistics'
    )
    
    parser.add_argument(
        '-c', '--console',
        action='store_true',
        help='Print result to console instead of file'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = ReverseComplement()
        
        # Determine output file
        output_file = args.output_file_alt or args.output_file
        
        if args.console and output_file:
            print("Warning: --console flag overrides output file specification")
            output_file = None
        
        # Process the file
        input_path = Path(args.input_file)
        
        if output_file and not args.console:
            output_path = Path(output_file)
            print(f"Processing: {input_path.name} → {output_path.name}")
            stats = processor.process_file(input_path, output_path)
            print(f"Reverse complement written to: {output_path}")
        else:
            # Print to console
            print(f"Processing: {input_path.name}")
            stats = processor.process_file(input_path)
            
            # Print results to console
            print("\nReverse Complement Results:")
            print("-" * 50)
            
            for header, sequence in processor.read_fasta(input_path):
                revcomp = processor.reverse_complement_sequence(sequence)
                print(f">{header}_reverse_complement")
                
                # Print sequence in chunks
                for i in range(0, len(revcomp), 60):
                    print(revcomp[i:i+60])
                print()
        
        # Print statistics if verbose mode
        if args.verbose or args.console:
            processor.print_stats(stats)
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()