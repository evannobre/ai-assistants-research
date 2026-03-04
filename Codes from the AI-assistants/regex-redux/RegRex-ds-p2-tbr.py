#!/usr/bin/env python3
"""
regex-redux solution optimized for Ubuntu 24.04.4 with 8GB RAM
Uses native Python libraries with minimal memory overhead
"""

import sys
import re
import mmap
import io
from collections import defaultdict
from typing import Dict, List, Tuple
from functools import lru_cache

class RegexReduxSolver:
    def __init__(self):
        # Pre-compile all regex patterns for maximum performance
        self.patterns = {
            'bgi': re.compile(rb'>[^\n]*\n|\n'),  # Remove headers and newlines
            'agggtaaa': re.compile(rb'agggtaaa|tttaccct'),
            'cgggtaaa': re.compile(rb'[cgt]gggtaaa|tttaccc[acg]'),
            'agggtaa': re.compile(rb'a[act]ggtaaa|tttacc[agt]t'),
            'agggta': re.compile(rb'ag[act]gtaaa|tttac[agt]ct'),
            'agggt': re.compile(rb'agg[act]taaa|ttta[agt]cct'),
            'aggg': re.compile(rb'aggg[acg]aaa|ttt[cgt]ccct'),
            'agggt_cgt': re.compile(rb'agggt[cgt]aa|tt[acg]accct'),
            'agggta_cgt': re.compile(rb'agggta[cgt]a|t[acg]taccct'),
            'agggtaa_cgt': re.compile(rb'agggtaa[cgt]|[acg]ttaccct'),
        }
        
        # IUB code replacements (optimized as bytes)
        self.iub_codes = [
            (b'B', b'(c|g|t)'),
            (b'D', b'(a|g|t)'),
            (b'H', b'(a|c|t)'),
            (b'K', b'(g|t)'),
            (b'M', b'(a|c)'),
            (b'N', b'(a|c|g|t)'),
            (b'R', b'(a|g)'),
            (b'S', b'(c|g)'),
            (b'V', b'(a|c|g)'),
            (b'W', b'(a|t)'),
            (b'Y', b'(c|t)'),
        ]
    
    def read_input_mmap(self) -> bytes:
        """Read input using memory-mapped file for efficiency"""
        if sys.stdin.isatty():
            # For testing with file
            with open('/dev/stdin', 'rb') as f:
                return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        else:
            # For pipe input
            return mmap.mmap(sys.stdin.fileno(), 0, access=mmap.ACCESS_READ)
    
    def clean_sequence(self, data: mmap.mmap) -> bytes:
        """Remove FASTA headers and newlines in one pass"""
        # Use regex substitution on bytes directly
        return self.patterns['bgi'].sub(b'', data)
    
    def count_patterns(self, sequence: bytes) -> Dict[str, int]:
        """Count pattern occurrences using pre-compiled regex"""
        results = {}
        for name, pattern in self.patterns.items():
            if name != 'bgi':  # Skip the cleaning pattern
                # Use finditer to avoid creating large match objects
                count = sum(1 for _ in pattern.finditer(sequence))
                results[name] = count
        return results
    
    def apply_iub_replacements(self, sequence: bytes) -> bytes:
        """Apply IUB code replacements using iterative replacement"""
        # Convert to bytearray for in-place modifications
        result = bytearray(sequence)
        
        # Apply replacements in reverse order to avoid interference
        for code, replacement in reversed(self.iub_codes):
            # Use manual replacement for better performance
            pos = 0
            while pos < len(result):
                found = result.find(code, pos)
                if found == -1:
                    break
                # Replace single byte with replacement pattern
                result[found:found+1] = replacement
                pos = found + len(replacement)
        
        return bytes(result)
    
    def optimized_iub_replacements(self, sequence: bytes) -> bytes:
        """Alternative implementation using regex for IUB replacements"""
        # Build a single regex pattern for all replacements
        pattern_parts = []
        replacements = {}
        
        for code, replacement in self.iub_codes:
            pattern_parts.append(re.escape(code))
            replacements[code.decode()] = replacement
        
        # Compile pattern once
        pattern = re.compile(b'|'.join(pattern_parts))
        
        def replacer(match):
            return replacements[match.group(0).decode()]
        
        return pattern.sub(replacer, sequence)
    
    def process(self) -> None:
        """Main processing pipeline"""
        try:
            # 1. Read input with memory mapping
            mmapped_data = self.read_input_mmap()
            
            # 2. Clean sequence (remove headers and newlines)
            sequence = self.clean_sequence(mmapped_data)
            initial_len = len(sequence)
            
            # 3. Count patterns
            counts = self.count_patterns(sequence)
            
            # 4. Print pattern counts
            for name in sorted(counts.keys()):
                if name != 'bgi':
                    print(f"{name} {counts[name]}")
            
            # 5. Apply IUB replacements
            modified = self.optimized_iub_replacements(sequence)
            
            # 6. Print lengths
            print(f"\n{initial_len}")
            print(len(modified))
            
            # Clean up memory map
            mmapped_data.close()
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Entry point with memory usage optimization"""
    # Set up environment for optimal performance
    import os
    os.environ['PYTHONHASHSEED'] = '0'
    
    # Create solver and process
    solver = RegexReduxSolver()
    solver.process()

if __name__ == "__main__":
    main()