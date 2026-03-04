#!/usr/bin/env python3
"""
regex-redux solution using native Python libraries and best practices.
Optimized for Ubuntu 24.04.4 with 8GB RAM and SSD storage.
"""
import sys
import re
import concurrent.futures
from typing import Tuple, List, Dict
import multiprocessing as mp
from collections import defaultdict
from io import StringIO
import gzip
from functools import lru_cache

class DNASequenceProcessor:
    """
    Processor for DNA sequence operations with memory and performance optimizations.
    """
    
    def __init__(self, max_workers: int = None):
        """
        Initialize processor with optimal worker count.
        """
        self.max_workers = max_workers or max(1, mp.cpu_count() - 1)
        # Pre-compile regex patterns for better performance
        self.patterns = {
            'variant_1': re.compile(r'gt[ac]|ac[gt]'),
            'variant_2': re.compile(r'a[act]|c[acg]|g[act]|t[acg]'),
            'variant_3': re.compile(r'[actg]gt|[acg]ac|[act]gt|[acg]tt'),
            'buo': re.compile(r'buo'),
            'bub': re.compile(r'bub'),
            'replace_1': re.compile(r'tHa[Nt]'),
            'replace_2': re.compile(r'<.*>'),
            'replace_3': re.compile(r'\\|[^|][^|]*\\|'),
            'dna_bases': re.compile(r'[actgACTG]'),
            'non_dna': re.compile(r'[^actgACTG\n]')
        }
        
    def read_input(self) -> str:
        """
        Read input efficiently, handling both stdin and files.
        Uses memory-efficient streaming for large inputs.
        """
        buffer = StringIO()
        
        # For large inputs, read in chunks
        chunk_size = 1024 * 1024  # 1MB chunks
        
        if sys.stdin.isatty():
            # Read from file if stdin is empty
            try:
                with open('/dev/stdin', 'r') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        buffer.write(chunk)
            except Exception:
                raise ValueError("No input provided")
        else:
            # Read from stdin
            while True:
                chunk = sys.stdin.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
        
        return buffer.getvalue()
    
    def clean_sequence(self, sequence: str) -> Tuple[str, int]:
        """
        Extract and clean DNA sequence from input.
        Returns cleaned sequence and original length.
        """
        # Find DNA sequence start
        lines = sequence.split('\n')
        seq_lines = []
        
        in_sequence = False
        for line in lines:
            if line.startswith('>'):
                if not in_sequence:
                    in_sequence = True
                    continue
                else:
                    break
            if in_sequence:
                seq_lines.append(line.strip())
        
        dna_seq = ''.join(seq_lines).upper()
        original_len = len(dna_seq)
        
        # Remove non-DNA characters efficiently
        dna_seq = self.patterns['dna_bases'].findall(dna_seq)
        return ''.join(dna_seq), original_len
    
    @lru_cache(maxsize=128)
    def count_pattern(self, pattern: str, sequence: str) -> int:
        """
        Count pattern occurrences with LRU caching for repeated patterns.
        """
        return len(re.findall(pattern, sequence))
    
    def find_variants(self, sequence: str) -> Dict[str, int]:
        """
        Find and count DNA variants using pre-compiled patterns.
        """
        results = {}
        
        for name, pattern in self.patterns.items():
            if name.startswith('variant'):
                # Use finditer for memory efficiency with large sequences
                count = sum(1 for _ in pattern.finditer(sequence))
                results[name] = count
        
        return results
    
    def perform_replacements(self, sequence: str) -> str:
        """
        Perform required replacements on the sequence.
        """
        # Apply replacements in specified order
        modified = self.patterns['replace_1'].sub('~~~', sequence)
        modified = self.patterns['replace_2'].sub('---', modified)
        modified = self.patterns['replace_3'].sub('***', modified)
        
        return modified
    
    def process_chunk(self, chunk: str, chunk_id: int) -> Dict:
        """
        Process a chunk of DNA sequence in parallel.
        """
        results = {
            'chunk_id': chunk_id,
            'length': len(chunk),
            'variants': defaultdict(int),
            'buo_count': 0,
            'bub_count': 0
        }
        
        # Count variants in this chunk
        for name, pattern in self.patterns.items():
            if name.startswith('variant'):
                results['variants'][name] = sum(1 for _ in pattern.finditer(chunk))
        
        # Count specific patterns
        results['buo_count'] = sum(1 for _ in self.patterns['buo'].finditer(chunk))
        results['bub_count'] = sum(1 for _ in self.patterns['bub'].finditer(chunk))
        
        return results
    
    def parallel_process(self, sequence: str) -> Dict:
        """
        Process DNA sequence in parallel chunks for better performance.
        """
        # Determine optimal chunk size based on sequence length and available workers
        chunk_size = max(10000, len(sequence) // (self.max_workers * 4))
        chunks = [sequence[i:i + chunk_size] 
                 for i in range(0, len(sequence), chunk_size)]
        
        results = {
            'total_length': len(sequence),
            'variants': defaultdict(int),
            'total_buo': 0,
            'total_bub': 0
        }
        
        # Use ThreadPoolExecutor for I/O bound operations (regex matching)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunks for processing
            future_to_chunk = {
                executor.submit(self.process_chunk, chunk, i): i
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk_result = future.result()
                
                # Aggregate results
                for variant, count in chunk_result['variants'].items():
                    results['variants'][variant] += count
                
                results['total_buo'] += chunk_result['buo_count']
                results['total_bub'] += chunk_result['bub_count']
        
        return results
    
    def run(self) -> None:
        """
        Main processing pipeline.
        """
        try:
            # 1. Read and clean input
            raw_input = self.read_input()
            sequence, original_len = self.clean_sequence(raw_input)
            
            print(f"Original length: {original_len}")
            print(f"Cleaned DNA length: {len(sequence)}")
            
            # 2. Parallel processing of variants
            parallel_results = self.parallel_process(sequence)
            
            print(f"\nVariant counts:")
            for variant, count in sorted(parallel_results['variants'].items()):
                print(f"{variant}: {count}")
            
            print(f"\nPattern counts:")
            print(f"buo: {parallel_results['total_buo']}")
            print(f"bub: {parallel_results['total_bub']}")
            
            # 3. Perform replacements
            modified_sequence = self.perform_replacements(sequence)
            
            print(f"\nAfter replacements:")
            print(f"Original ATGC count: {self.count_pattern('[ATGC]', sequence)}")
            print(f"Modified length: {len(modified_sequence)}")
            
            # 4. Final statistics
            gc_content = (sequence.count('G') + sequence.count('C')) / len(sequence) * 100
            print(f"\nGC content: {gc_content:.2f}%")
            
            # Memory usage feedback
            import os
            import psutil
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            print(f"\nMemory usage: {mem_mb:.2f} MB")
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)


def main():
    """
    Entry point with resource optimization for the given hardware.
    """
    # Configure for 8GB RAM system
    # Leave 2GB for system, use up to 6GB for processing
    MAX_MEMORY_MB = 6000
    
    # Calculate optimal worker count
    cpu_count = mp.cpu_count()
    # On 8GB system, limit workers to prevent memory exhaustion
    optimal_workers = max(1, min(cpu_count - 1, 4))
    
    processor = DNASequenceProcessor(max_workers=optimal_workers)
    processor.run()


if __name__ == "__main__":
    main()