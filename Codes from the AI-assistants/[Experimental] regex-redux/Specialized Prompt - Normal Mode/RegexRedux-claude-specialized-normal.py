#!/usr/bin/env python3
"""
Regex-Redux Algorithm Implementation
Optimized for Ubuntu 24.04.2 LTS with 16GB RAM and 30GB SSD
Uses native Python libraries for maximum performance
"""

import sys
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import gc
import mmap
import os

class RegexRedux:
    def __init__(self):
        # Precompile regex patterns for better performance
        self.variants = [
            ('agggtaaa|tttaccct', re.compile(r'agggtaaa|tttaccct')),
            ('[cgt]gggtaaa|tttaccc[acg]', re.compile(r'[cgt]gggtaaa|tttaccc[acg]')),
            ('a[act]ggtaaa|tttacc[agt]t', re.compile(r'a[act]ggtaaa|tttacc[agt]t')),
            ('ag[act]gtaaa|tttac[agt]ct', re.compile(r'ag[act]gtaaa|tttac[agt]ct')),
            ('agg[act]taaa|ttta[agt]cct', re.compile(r'agg[act]taaa|ttta[agt]cct')),
            ('aggg[acg]aaa|ttt[cgt]ccct', re.compile(r'aggg[acg]aaa|ttt[cgt]ccct')),
            ('agggt[cgt]aa|tt[acg]accct', re.compile(r'agggt[cgt]aa|tt[acg]accct')),
            ('agggta[cgt]a|t[acg]taccct', re.compile(r'agggta[cgt]a|t[acg]taccct')),
            ('agggtaa[cgt]|[acg]ttaccct', re.compile(r'agggtaa[cgt]|[acg]ttaccct'))
        ]
        
        # Substitution patterns - order matters for correctness
        self.substitutions = [
            ('tHa[Nt]', '<4>'),
            ('aND|caN|Ha[DS]|WaS', '<3>'),
            ('a[NSt]|BY', '<2>'),
            ('<[^>]*>', '|'),
            ('\\|[^|][^|]*\\|', '-')
        ]
        
        # Precompile substitution patterns
        self.sub_patterns = [(re.compile(pattern), replacement) 
                           for pattern, replacement in self.substitutions]
    
    def read_input_efficiently(self, file_path=None):
        """
        Read input efficiently using memory mapping for large files
        Falls back to stdin if no file provided
        """
        if file_path and os.path.exists(file_path):
            # Use memory mapping for large files to avoid loading everything into RAM
            with open(file_path, 'r') as f:
                # Check file size first
                f.seek(0, 2)  # Seek to end
                size = f.tell()
                f.seek(0)  # Seek back to beginning
                
                if size > 100 * 1024 * 1024:  # If > 100MB, use mmap
                    with open(file_path, 'rb') as bf:
                        with mmap.mmap(bf.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                            return mmapped_file.read().decode('utf-8')
                else:
                    return f.read()
        else:
            # Read from stdin
            return sys.stdin.read()
    
    def clean_sequence(self, sequence):
        """
        Remove FASTA headers and newlines efficiently
        """
        # Remove FASTA headers (lines starting with >)
        lines = []
        for line in sequence.splitlines():
            if not line.startswith('>'):
                lines.append(line)
        
        # Join without newlines and convert to uppercase for consistency
        return ''.join(lines).upper()
    
    def count_variant_parallel(self, args):
        """
        Count occurrences of a variant pattern (for parallel execution)
        """
        pattern_name, compiled_pattern, sequence = args
        count = len(compiled_pattern.findall(sequence))
        return pattern_name, count
    
    def count_variants(self, sequence):
        """
        Count all variant patterns using parallel processing
        """
        # Prepare arguments for parallel processing
        args_list = [(name, pattern, sequence) for name, pattern in self.variants]
        
        # Use ThreadPoolExecutor for I/O-bound regex operations
        max_workers = min(len(self.variants), os.cpu_count() or 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.count_variant_parallel, args_list))
        
        return results
    
    def apply_substitutions(self, sequence):
        """
        Apply substitution patterns sequentially (order matters)
        Memory-efficient approach using in-place operations where possible
        """
        current_seq = sequence
        
        for pattern, replacement in self.sub_patterns:
            # Use re.sub which is implemented in C and very efficient
            current_seq = pattern.sub(replacement, current_seq)
            
            # Force garbage collection after each major operation to manage memory
            if len(current_seq) > 50 * 1024 * 1024:  # If > 50MB
                gc.collect()
        
        return current_seq
    
    def run(self, input_file=None):
        """
        Main execution function
        """
        # Read input
        raw_input = self.read_input_efficiently(input_file)
        initial_length = len(raw_input)
        
        # Clean sequence (remove headers and newlines)
        sequence = self.clean_sequence(raw_input)
        cleaned_length = len(sequence)
        
        # Free memory from raw input
        del raw_input
        gc.collect()
        
        # Count variant patterns in parallel
        variant_counts = self.count_variants(sequence)
        
        # Apply substitutions
        final_sequence = self.apply_substitutions(sequence)
        final_length = len(final_sequence)
        
        # Free memory
        del sequence
        gc.collect()
        
        return {
            'initial_length': initial_length,
            'cleaned_length': cleaned_length,
            'final_length': final_length,
            'variant_counts': variant_counts
        }
    
    def print_results(self, results):
        """
        Print results in the expected format
        """
        # Print variant counts
        for pattern_name, count in results['variant_counts']:
            print(f"{pattern_name} {count}")
        
        print()
        print(f"{results['initial_length']}")
        print(f"{results['cleaned_length']}")
        print(f"{results['final_length']}")


def main():
    """
    Main function with memory and performance optimizations
    """
    # Set up memory-efficient settings
    gc.set_threshold(700, 10, 10)  # More aggressive garbage collection
    
    # Create regex redux instance
    regex_redux = RegexRedux()
    
    # Check if input file is provided as command line argument
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        # Run the algorithm
        results = regex_redux.run(input_file)
        
        # Print results
        regex_redux.print_results(results)
        
    except MemoryError:
        print("Error: Insufficient memory to process the input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Final cleanup
        gc.collect()


if __name__ == "__main__":
    main()