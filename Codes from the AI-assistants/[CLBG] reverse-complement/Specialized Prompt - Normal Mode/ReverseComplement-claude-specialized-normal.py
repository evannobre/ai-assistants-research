#!/usr/bin/env python3
"""
DNA Reverse Complement Algorithm
Efficiently processes FASTA format files to generate reverse complement sequences.
Optimized for memory usage with buffered line-by-line reading.
"""

import sys
from typing import Dict, TextIO

class DNAReverseComplement:
    """
    High-performance DNA reverse complement processor with optimized memory usage.
    """
    
    def __init__(self):
        # Complement mapping table for O(1) lookup
        self.complement_map: Dict[str, str] = {
            'A': 'T', 'T': 'A', 'U': 'A', 'C': 'G', 'G': 'C',
            'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S', 'Y': 'R',
            'K': 'M', 'V': 'B', 'H': 'D', 'D': 'H', 'B': 'V',
            'N': 'N'
        }
        
        # Buffer size for efficient I/O operations
        self.buffer_size = 8192
    
    def get_complement(self, base: str) -> str:
        """
        Get complement of a single base with error handling.
        
        Args:
            base: Single nucleotide character
            
        Returns:
            Complement character
        """
        return self.complement_map.get(base.upper(), 'N')
    
    def reverse_complement(self, sequence: str) -> str:
        """
        Generate reverse complement of DNA sequence.
        Optimized using list comprehension and reverse indexing.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Reverse complement sequence
        """
        # Use list comprehension for efficiency - single pass with reverse
        return ''.join(self.get_complement(base) for base in reversed(sequence.strip()))
    
    def process_fasta_stream(self, input_stream: TextIO = None, output_stream: TextIO = None):
        """
        Process FASTA format stream with buffered line-by-line reading.
        Memory-efficient implementation that grows data incrementally.
        
        Args:
            input_stream: Input stream (default: stdin)
            output_stream: Output stream (default: stdout)
        """
        if input_stream is None:
            input_stream = sys.stdin
        if output_stream is None:
            output_stream = sys.stdout
        
        current_id = None
        current_description = ""
        sequence_lines = []
        
        try:
            # Buffered line-by-line reading
            for line in input_stream:
                line = line.rstrip('\n\r')
                
                if line.startswith('>'):
                    # Process previous sequence if exists
                    if current_id is not None:
                        self._write_reverse_complement(
                            current_id, current_description, 
                            sequence_lines, output_stream
                        )
                    
                    # Parse new header
                    header_parts = line[1:].split(' ', 1)
                    current_id = header_parts[0]
                    current_description = header_parts[1] if len(header_parts) > 1 else ""
                    sequence_lines = []  # Reset sequence buffer
                    
                elif current_id is not None:
                    # Accumulate sequence data
                    sequence_lines.append(line)
            
            # Process final sequence
            if current_id is not None:
                self._write_reverse_complement(
                    current_id, current_description, 
                    sequence_lines, output_stream
                )
                
        except KeyboardInterrupt:
            sys.stderr.write("\nProcessing interrupted by user.\n")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Error processing FASTA file: {e}\n")
            sys.exit(1)
    
    def _write_reverse_complement(self, seq_id: str, description: str, 
                                sequence_lines: list, output_stream: TextIO):
        """
        Write reverse complement sequence in FASTA format.
        
        Args:
            seq_id: Sequence identifier
            description: Sequence description
            sequence_lines: List of sequence line strings
            output_stream: Output stream
        """
        # Combine all sequence lines efficiently
        full_sequence = ''.join(sequence_lines)
        
        # Generate reverse complement
        rev_comp = self.reverse_complement(full_sequence)
        
        # Write header
        header = f">{seq_id}"
        if description:
            header += f" {description}"
        output_stream.write(header + '\n')
        
        # Write sequence in standard 80-character lines
        line_length = 80
        for i in range(0, len(rev_comp), line_length):
            output_stream.write(rev_comp[i:i + line_length] + '\n')


def main():
    """
    Main entry point for the reverse complement processor.
    """
    processor = DNAReverseComplement()
    processor.process_fasta_stream()


if __name__ == "__main__":
    main()