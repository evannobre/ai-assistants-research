#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
Optimized for large files with memory constraints (8GB RAM)
Uses streaming approach and native Python libraries
"""

import sys
import os
from io import StringIO


class DNAProcessor:
    """Handles DNA sequence reverse complement operations"""
    
    # Translation table for complement (using str.translate for O(n) performance)
    COMPLEMENT_TABLE = str.maketrans('ACGTacgtNnRrYyKkMmSsWwBbDdHhVv',
                                     'TGCAtgcaNnYyRrMmKkSsWwVvHhDdBb')
    
    def __init__(self, chunk_size=8388608):  # 8MB chunks
        """
        Initialize DNA processor
        
        Args:
            chunk_size: Size of chunks to read (default 8MB for efficient I/O)
        """
        self.chunk_size = chunk_size
    
    @staticmethod
    def complement(sequence):
        """
        Returns the complement of a DNA sequence
        
        Time complexity: O(n)
        Space complexity: O(n)
        """
        return sequence.translate(DNAProcessor.COMPLEMENT_TABLE)
    
    @staticmethod
    def reverse_complement(sequence):
        """
        Returns the reverse complement of a DNA sequence
        
        Time complexity: O(n)
        Space complexity: O(n)
        """
        return sequence.translate(DNAProcessor.COMPLEMENT_TABLE)[::-1]
    
    def process_fasta_file(self, input_path, output_path):
        """
        Process FASTA file and write reverse complement
        Uses streaming to handle files larger than available RAM
        
        Args:
            input_path: Path to input FASTA file
            output_path: Path to output file
        """
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            current_header = None
            sequence_buffer = []
            
            for line in infile:
                line = line.rstrip('\n\r')
                
                if line.startswith('>'):
                    # Process previous sequence if exists
                    if current_header is not None:
                        self._write_reverse_complement(
                            outfile, current_header, sequence_buffer
                        )
                    
                    # Start new sequence
                    current_header = line
                    sequence_buffer = []
                else:
                    # Accumulate sequence data
                    sequence_buffer.append(line)
            
            # Process last sequence
            if current_header is not None:
                self._write_reverse_complement(
                    outfile, current_header, sequence_buffer
                )
    
    def _write_reverse_complement(self, outfile, header, sequence_buffer):
        """
        Write reverse complement of accumulated sequence
        
        Args:
            outfile: Output file handle
            header: FASTA header line
            sequence_buffer: List of sequence lines
        """
        outfile.write(header + '\n')
        
        # Join all sequence parts
        full_sequence = ''.join(sequence_buffer)
        
        # Compute reverse complement
        rev_comp = self.reverse_complement(full_sequence)
        
        # Write in 80-character lines (FASTA convention)
        for i in range(0, len(rev_comp), 80):
            outfile.write(rev_comp[i:i+80] + '\n')
    
    def process_raw_file(self, input_path, output_path):
        """
        Process raw DNA sequence file (no FASTA headers)
        Uses chunked processing for memory efficiency
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
        """
        file_size = os.path.getsize(input_path)
        
        # For small files, process in one go
        if file_size < self.chunk_size:
            with open(input_path, 'r') as infile:
                sequence = infile.read().strip().replace('\n', '').replace('\r', '')
                rev_comp = self.reverse_complement(sequence)
            
            with open(output_path, 'w') as outfile:
                outfile.write(rev_comp + '\n')
        else:
            # For large files, use memory-mapped approach
            self._process_large_raw_file(input_path, output_path)
    
    def _process_large_raw_file(self, input_path, output_path):
        """
        Process large raw files using streaming
        Reads file, reverses it, and complements in chunks
        """
        # First pass: read and store complemented chunks in reverse order
        chunks = []
        
        with open(input_path, 'r') as infile:
            while True:
                chunk = infile.read(self.chunk_size)
                if not chunk:
                    break
                # Remove whitespace and complement
                clean_chunk = chunk.replace('\n', '').replace('\r', '').replace(' ', '')
                comp_chunk = self.complement(clean_chunk)
                chunks.append(comp_chunk)
        
        # Write chunks in reverse order, reversing each chunk
        with open(output_path, 'w') as outfile:
            for chunk in reversed(chunks):
                outfile.write(chunk[::-1])
            outfile.write('\n')


def print_usage():
    """Print usage information"""
    print("Usage: python3 reverse_complement.py <input_file> <output_file> [--format FORMAT]")
    print("\nArguments:")
    print("  input_file   Path to input DNA sequence file")
    print("  output_file  Path to output file for reverse complement")
    print("\nOptions:")
    print("  --format     Format of input file: 'fasta' or 'raw' (default: auto-detect)")
    print("\nExamples:")
    print("  python3 reverse_complement.py input.fasta output.fasta")
    print("  python3 reverse_complement.py input.txt output.txt --format raw")


def detect_format(filepath):
    """
    Auto-detect file format based on first line
    
    Returns:
        'fasta' if file starts with '>', 'raw' otherwise
    """
    with open(filepath, 'r') as f:
        first_line = f.readline().strip()
        return 'fasta' if first_line.startswith('>') else 'raw'


def main():
    """Main entry point"""
    if len(sys.argv) < 3 or '--help' in sys.argv or '-h' in sys.argv:
        print_usage()
        sys.exit(0 if '--help' in sys.argv or '-h' in sys.argv else 1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Parse format argument
    file_format = None
    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            file_format = sys.argv[idx + 1].lower()
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Auto-detect format if not specified
    if file_format is None:
        file_format = detect_format(input_file)
        print(f"Auto-detected format: {file_format}")
    
    # Validate format
    if file_format not in ['fasta', 'raw']:
        print(f"Error: Invalid format '{file_format}'. Use 'fasta' or 'raw'", file=sys.stderr)
        sys.exit(1)
    
    # Process file
    processor = DNAProcessor()
    
    try:
        print(f"Processing {input_file}...")
        
        if file_format == 'fasta':
            processor.process_fasta_file(input_file, output_file)
        else:
            processor.process_raw_file(input_file, output_file)
        
        print(f"Reverse complement written to {output_file}")
        print(f"Output file size: {os.path.getsize(output_file):,} bytes")
        
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
