#!/usr/bin/env python3
"""
DNA Reverse Complement Simulator
Optimized for Ubuntu 24.04.4 with 8GB RAM and 256GB SSD
Uses native libraries for maximum efficiency
"""

import sys
import os
import mmap
import argparse
from pathlib import Path
from typing import Generator, Tuple, Optional
import time

class DNAReverseComplement:
    """Efficient DNA reverse complement processor using memory-mapped files."""
    
    # DNA complement mapping (including ambiguous bases)
    COMPLEMENT_TABLE = str.maketrans({
        'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
        'a': 't', 't': 'a', 'c': 'g', 'g': 'c',
        'N': 'N', 'n': 'n',
        'R': 'Y', 'Y': 'R', 'S': 'S', 'W': 'W',
        'K': 'M', 'M': 'K', 'B': 'V', 'V': 'B',
        'D': 'H', 'H': 'D', 'r': 'y', 'y': 'r',
        's': 's', 'w': 'w', 'k': 'm', 'm': 'k',
        'b': 'v', 'v': 'b', 'd': 'h', 'h': 'd'
    })
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        """
        Initialize processor with optimal chunk size.
        
        Args:
            chunk_size: Size of chunks to process (optimized for SSD)
        """
        self.chunk_size = chunk_size
        
    def reverse_complement_string(self, sequence: str) -> str:
        """
        Compute reverse complement for a string.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Reverse complemented sequence
        """
        # Optimized: translate and reverse in one step
        return sequence.translate(self.COMPLEMENT_TABLE)[::-1]
    
    def process_fasta_stream(self, input_path: Path) -> Generator[Tuple[str, str], None, None]:
        """
        Process FASTA file in streaming fashion.
        
        Args:
            input_path: Path to input FASTA file
            
        Yields:
            Tuples of (header, reverse_complemented_sequence)
        """
        with open(input_path, 'r') as f:
            # Memory-map the file for efficient reading
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                current_header = None
                current_sequence = []
                
                # Process by lines for FASTA format
                for line in iter(mmapped_file.readline, b''):
                    line = line.decode('utf-8').rstrip()
                    
                    if line.startswith('>'):  # Header line
                        if current_header is not None:
                            # Process accumulated sequence
                            sequence = ''.join(current_sequence)
                            rev_comp = self.reverse_complement_string(sequence)
                            yield current_header, rev_comp
                        
                        current_header = line
                        current_sequence = []
                    else:
                        # Accumulate sequence lines
                        current_sequence.append(line.upper())
                
                # Process last sequence
                if current_header is not None and current_sequence:
                    sequence = ''.join(current_sequence)
                    rev_comp = self.reverse_complement_string(sequence)
                    yield current_header, rev_comp
    
    def process_raw_dna(self, input_path: Path) -> Generator[str, None, None]:
        """
        Process raw DNA file (no headers).
        
        Args:
            input_path: Path to input DNA file
            
        Yields:
            Reverse complemented chunks
        """
        with open(input_path, 'r') as f:
            # Memory-map for efficient access
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                # Process in chunks for large files
                start = 0
                total_length = len(mmapped_file)
                
                while start < total_length:
                    end = min(start + self.chunk_size, total_length)
                    
                    # Find the next newline to avoid cutting in middle of sequence
                    if end < total_length:
                        # Look for newline boundary
                        while end < total_length and chr(mmapped_file[end]) not in ('\n', '\r'):
                            end += 1
                    
                    chunk = mmapped_file[start:end].decode('utf-8')
                    # Remove whitespace and newlines
                    chunk = chunk.replace('\n', '').replace('\r', '').replace(' ', '').upper()
                    
                    if chunk:  # Skip empty chunks
                        rev_comp = self.reverse_complement_string(chunk)
                        yield rev_comp
                    
                    start = end
    
    def validate_dna_sequence(self, sequence: str) -> bool:
        """
        Validate DNA sequence contains only valid nucleotides.
        
        Args:
            sequence: DNA sequence to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_chars = set('ATCGNMRWSYKVHDBatcgnmrwsykvhdb')
        return all(char in valid_chars for char in sequence)
    
    def process_file(self, input_path: Path, output_path: Optional[Path] = None, 
                     is_fasta: bool = True) -> Tuple[int, float]:
        """
        Main processing method.
        
        Args:
            input_path: Input file path
            output_path: Output file path (stdout if None)
            is_fasta: Whether file is in FASTA format
            
        Returns:
            Tuple of (processed_sequences, processing_time)
        """
        start_time = time.time()
        processed_count = 0
        
        try:
            if output_path:
                out_fd = open(output_path, 'w')
            else:
                out_fd = sys.stdout
            
            if is_fasta:
                for header, rev_comp in self.process_fasta_stream(input_path):
                    # Validate sequence
                    if not self.validate_dna_sequence(rev_comp):
                        sys.stderr.write(f"Warning: Invalid characters in sequence after {header}\n")
                    
                    # Write output
                    out_fd.write(f"{header}_reverse_complement\n")
                    
                    # Write in 80-character lines (standard FASTA format)
                    for i in range(0, len(rev_comp), 80):
                        out_fd.write(rev_comp[i:i+80] + '\n')
                    
                    processed_count += 1
            else:
                # Raw DNA format
                for rev_comp_chunk in self.process_raw_dna(input_path):
                    if not self.validate_dna_sequence(rev_comp_chunk):
                        sys.stderr.write("Warning: Invalid characters in DNA sequence\n")
                    
                    # Write in 80-character lines
                    for i in range(0, len(rev_comp_chunk), 80):
                        out_fd.write(rev_comp_chunk[i:i+80] + '\n')
                    
                    processed_count += 1
            
            if output_path:
                out_fd.close()
                
        except Exception as e:
            sys.stderr.write(f"Error processing file: {str(e)}\n")
            raise
        
        processing_time = time.time() - start_time
        return processed_count, processing_time


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Compute reverse complement of DNA sequences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.fasta -o output.fasta
  %(prog)s dna.txt --raw
  cat input.fasta | %(prog)s --stdin
  
Memory Usage:
  This tool uses memory-mapped files and chunked processing
  to handle files up to several GB within 8GB RAM.
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input DNA file (FASTA or raw)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--raw', action='store_true', 
                       help='Treat input as raw DNA (no FASTA headers)')
    parser.add_argument('--stdin', action='store_true',
                       help='Read from stdin instead of file')
    parser.add_argument('--chunk-size', type=int, default=1024*1024,
                       help='Processing chunk size in bytes (default: 1MB)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output with timing information')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.stdin and not args.input:
        parser.error("Either provide input file or use --stdin")
    
    try:
        processor = DNAReverseComplement(chunk_size=args.chunk_size)
        
        if args.stdin:
            # Read from stdin to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                tmp.write(sys.stdin.read())
                tmp_path = Path(tmp.name)
            
            try:
                count, time_taken = processor.process_file(
                    tmp_path, 
                    Path(args.output) if args.output else None,
                    is_fasta=not args.raw
                )
            finally:
                tmp_path.unlink()  # Cleanup temp file
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                sys.stderr.write(f"Error: Input file '{args.input}' not found\n")
                sys.exit(1)
            
            output_path = Path(args.output) if args.output else None
            count, time_taken = processor.process_file(
                input_path, 
                output_path,
                is_fasta=not args.raw
            )
        
        if args.verbose:
            sys.stderr.write(f"Processed {count} sequence(s) in {time_taken:.2f} seconds\n")
            if count > 0:
                sys.stderr.write(f"Average: {time_taken/count:.3f} seconds per sequence\n")
        
    except Exception as e:
        sys.stderr.write(f"Fatal error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()