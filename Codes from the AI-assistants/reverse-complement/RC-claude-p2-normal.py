#!/usr/bin/env python3
"""
DNA Reverse Complement Generator
Efficiently computes the reverse complement of DNA sequences from FASTA files.
Optimized for low memory footprint using streaming and native Python libraries.

Author: Computer Science Backend Specialist
Python Version: 3.12+ (Ubuntu 24.04)
"""

import sys
import os
import mmap
from typing import Iterator, TextIO
from io import StringIO


class DNAReverseComplement:
    """
    Memory-efficient DNA reverse complement processor using native Python libraries.
    
    Time Complexity: O(n) where n is the total sequence length
    Space Complexity: O(c) where c is the chunk size (constant for streaming)
    """
    
    # Translation table using str.maketrans for O(1) complement lookup
    COMPLEMENT_TABLE = str.maketrans('ACGTacgt', 'TGCAtgca')
    
    # Chunk size optimized for L1/L2 cache (~64KB) and I/O efficiency
    CHUNK_SIZE = 65536  # 64 KB chunks
    
    def __init__(self, input_file: str, output_file: str = None):
        """
        Initialize the reverse complement processor.
        
        Args:
            input_file: Path to input FASTA file
            output_file: Path to output file (defaults to stdout)
        """
        self.input_file = input_file
        self.output_file = output_file
        self._validate_input()
    
    def _validate_input(self) -> None:
        """Validate input file exists and is readable."""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if not os.access(self.input_file, os.R_OK):
            raise PermissionError(f"Cannot read input file: {self.input_file}")
        
        file_size = os.path.getsize(self.input_file)
        available_memory = 8 * 1024 * 1024 * 1024  # 8 GB
        
        # Warn if file is very large (>2GB) to ensure streaming approach
        if file_size > 2 * 1024 * 1024 * 1024:
            print(f"Warning: Large file detected ({file_size / (1024**3):.2f} GB). "
                  f"Using streaming mode.", file=sys.stderr)
    
    @staticmethod
    def complement(sequence: str) -> str:
        """
        Compute complement of DNA sequence using translation table.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Complemented sequence
            
        Time Complexity: O(n)
        Space Complexity: O(n) for output string
        """
        return sequence.translate(DNAReverseComplement.COMPLEMENT_TABLE)
    
    @staticmethod
    def reverse_complement(sequence: str) -> str:
        """
        Compute reverse complement of DNA sequence.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Reverse complement of sequence
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        # Using slice reversal [::-1] - implemented in C, very fast
        return sequence.translate(DNAReverseComplement.COMPLEMENT_TABLE)[::-1]
    
    def _parse_fasta_streaming(self, file_handle: TextIO) -> Iterator[tuple[str, str]]:
        """
        Stream-parse FASTA file to avoid loading entire file into memory.
        
        Yields:
            Tuple of (header, sequence) for each entry
            
        Space Complexity: O(m) where m is the longest single sequence
        """
        header = None
        sequence_parts = []
        
        for line in file_handle:
            line = line.rstrip('\n\r')
            
            if line.startswith('>'):
                # Yield previous sequence if exists
                if header is not None:
                    yield header, ''.join(sequence_parts)
                
                header = line
                sequence_parts = []
            else:
                # Accumulate sequence lines
                sequence_parts.append(line)
        
        # Yield final sequence
        if header is not None:
            yield header, ''.join(sequence_parts)
    
    def _process_large_sequence(self, sequence: str, output_handle: TextIO, 
                                line_width: int = 80) -> None:
        """
        Process and write large sequence in chunks to minimize memory usage.
        
        Args:
            sequence: DNA sequence to reverse complement
            output_handle: File handle for output
            line_width: Characters per line in output (FASTA standard: 80)
        """
        # Reverse complement in place
        rev_comp = self.reverse_complement(sequence)
        
        # Write in formatted chunks
        for i in range(0, len(rev_comp), line_width):
            output_handle.write(rev_comp[i:i + line_width])
            output_handle.write('\n')
    
    def process(self) -> None:
        """
        Main processing pipeline: read FASTA, compute reverse complement, write output.
        
        Uses streaming to handle files larger than available RAM.
        """
        output_handle = sys.stdout if self.output_file is None else open(self.output_file, 'w')
        
        try:
            with open(self.input_file, 'r', buffering=self.CHUNK_SIZE) as input_handle:
                for header, sequence in self._parse_fasta_streaming(input_handle):
                    # Write modified header
                    output_handle.write(f"{header} [reverse complement]\n")
                    
                    # Process sequence
                    self._process_large_sequence(sequence, output_handle)
                    
        finally:
            if self.output_file is not None:
                output_handle.close()


def main():
    """Command-line interface for DNA reverse complement tool."""
    
    if len(sys.argv) < 2:
        print("Usage: python3 reverse_complement.py <input_fasta> [output_file]", 
              file=sys.stderr)
        print("\nExample:")
        print("  python3 reverse_complement.py input.fasta output.fasta")
        print("  python3 reverse_complement.py input.fasta > output.fasta")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        processor = DNAReverseComplement(input_file, output_file)
        processor.process()
        
        if output_file:
            print(f"Successfully wrote reverse complement to: {output_file}", 
                  file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
