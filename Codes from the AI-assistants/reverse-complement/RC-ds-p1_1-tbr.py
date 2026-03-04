#!/usr/bin/env python3
"""
Reverse Complement Simulator
Usage: python reverse_complement.py <input_file.fasta>
"""

import sys
import argparse
from pathlib import Path
import gzip
from typing import Generator, Tuple
import time

class ReverseComplement:
    def __init__(self):
        # DNA complement mapping (including ambiguity codes)
        self.complement_table = str.maketrans({
            'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
            'a': 't', 't': 'a', 'c': 'g', 'g': 'c',
            'N': 'N', 'n': 'n',  # Unknown bases
            'R': 'Y', 'Y': 'R',  # Purine (A/G) ↔ Pyrimidine (T/C)
            'S': 'S', 'W': 'W',  # S=G/C strong, W=A/T weak
            'K': 'M', 'M': 'K',  # K=G/T keto, M=A/C amino
            'B': 'V', 'V': 'B',  # B=not A, V=not T
            'D': 'H', 'H': 'D'   # D=not C, H=not G
        })
    
    def complement_base(self, base: str) -> str:
        """Get complement of a single base using translation table."""
        return base.translate(self.complement_table)
    
    def reverse_complement_sequence(self, sequence: str) -> str:
        """Compute reverse complement of a DNA sequence."""
        # Reverse the string and translate complements
        return sequence[::-1].translate(self.complement_table)
    
    def process_fasta(self, filepath: Path) -> Generator[Tuple[str, str], None, None]:
        """Parse FASTA file and yield (header, sequence) pairs."""
        header = None
        sequence_lines = []
        
        # Handle gzipped files
        open_func = gzip.open if filepath.suffix == '.gz' else open
        mode = 'rt' if filepath.suffix == '.gz' else 'r'
        
        with open_func(filepath, mode) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('>'):
                    # Yield previous sequence if exists
                    if header is not None and sequence_lines:
                        yield header, ''.join(sequence_lines)
                    
                    # Start new sequence
                    header = line
                    sequence_lines = []
                else:
                    sequence_lines.append(line.upper())
            
            # Yield the last sequence
            if header is not None and sequence_lines:
                yield header, ''.join(sequence_lines)
    
    def validate_dna(self, sequence: str) -> bool:
        """Check if sequence contains valid DNA characters."""
        valid_bases = set('ACGTNacgtnRYSMKBDHVrysmkbdhv-')
        return all(base in valid_bases for base in sequence)
    
    def run(self, input_file: str, output_file: str = None, 
            validate: bool = False, stats: bool = False) -> None:
        """Main execution method."""
        filepath = Path(input_file)
        
        if not filepath.exists():
            print(f"Error: File '{input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        
        # Statistics tracking
        total_seqs = 0
        total_bases = 0
        invalid_seqs = 0
        
        # Determine output destination
        output_stream = sys.stdout
        if output_file:
            output_path = Path(output_file)
            output_stream = open(output_path, 'w')
        
        try:
            start_time = time.time()
            
            for header, sequence in self.process_fasta(filepath):
                total_seqs += 1
                
                # Validate if requested
                if validate and not self.validate_dna(sequence):
                    print(f"Warning: Sequence {header[:50]}... contains invalid characters", 
                          file=sys.stderr)
                    invalid_seqs += 1
                    if stats:
                        continue  # Skip invalid sequences
                
                # Compute reverse complement
                rc_sequence = self.reverse_complement_sequence(sequence)
                total_bases += len(sequence)
                
                # Output in FASTA format
                output_stream.write(f"{header}_reverse_complement\n")
                
                # Format with 80 bases per line (standard FASTA)
                for i in range(0, len(rc_sequence), 80):
                    output_stream.write(rc_sequence[i:i+80] + '\n')
            
            end_time = time.time()
            
            # Print statistics if requested
            if stats:
                print(f"\nStatistics:", file=sys.stderr)
                print(f"  Total sequences: {total_seqs}", file=sys.stderr)
                print(f"  Total bases: {total_bases:,}", file=sys.stderr)
                print(f"  Invalid sequences: {invalid_seqs}", file=sys.stderr)
                print(f"  Time elapsed: {end_time - start_time:.3f} seconds", file=sys.stderr)
                
        except Exception as e:
            print(f"Error processing file: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            if output_file and output_stream != sys.stdout:
                output_stream.close()

def main():
    parser = argparse.ArgumentParser(
        description='Compute reverse complement of DNA sequences in FASTA format'
    )
    parser.add_argument('input_file', help='Input FASTA file (can be .gz compressed)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('-v', '--validate', action='store_true',
                       help='Validate DNA sequences')
    parser.add_argument('-s', '--stats', action='store_true',
                       help='Print statistics after processing')
    
    args = parser.parse_args()
    
    rc = ReverseComplement()
    rc.run(args.input_file, args.output, args.validate, args.stats)

if __name__ == '__main__':
    main()