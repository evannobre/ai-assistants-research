#!/usr/bin/env python3
"""
Regex-Redux FASTA Format Processor
A Computer Science implementation specialized in back-end development
using native Python libraries for DNA sequence analysis.

This implementation follows the exact algorithm specification:
1. Read FASTA format from stdin
2. Remove descriptions and linefeeds with regex
3. Count DNA 8-mer patterns and their reverse complements
4. Apply magic regex transformations
5. Report all sequence lengths
"""

import sys
import re
from typing import List, Tuple


class RegexReduxProcessor:
    """
    FASTA sequence processor implementing regex-redux algorithm
    using Python's native re module for maximum compatibility.
    """
    
    def __init__(self):
        # DNA 8-mer patterns and their reverse complements with wildcards
        self.dna_patterns = [
            r'agggtaaa|tttaccct',
            r'[cgt]gggtaaa|tttaccc[acg]',
            r'a[act]ggtaaa|tttacc[agt]t',
            r'ag[act]gtaaa|tttac[agt]ct',
            r'agg[act]taaa|ttta[agt]cct',
            r'aggg[acg]aaa|ttt[cgt]ccct',
            r'agggt[cgt]aa|tt[acg]accct',
            r'agggta[cgt]a|t[acg]taccct',
            r'agggtaa[cgt]|[acg]ttaccct'
        ]
        
        # Magic transformation patterns and their replacements
        self.magic_patterns = [
            (r'tHa[Nt]', r'<4>'),
            (r'aND|caN|Ha[DS]|WaS', r'<3>'),
            (r'a[NSt]|BY', r'<2>'),
            (r'<[^>]*>', r'|'),
            (r'\\|[^|][^|]*\\|', r'-')
        ]
        
        # Compiled regex patterns for performance
        self.compiled_dna_patterns = [re.compile(pattern, re.IGNORECASE) 
                                     for pattern in self.dna_patterns]
        self.compiled_magic_patterns = [(re.compile(pattern, re.IGNORECASE), replacement) 
                                       for pattern, replacement in self.magic_patterns]
    
    def read_fasta_from_stdin(self) -> str:
        """
        Read entire FASTA format file from standard input.
        
        Returns:
            str: Complete FASTA file content as string
        """
        try:
            content = sys.stdin.read()
            return content
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_original_length(self, content: str) -> int:
        """
        Calculate original sequence length including all characters.
        
        Args:
            content: Raw FASTA content
            
        Returns:
            int: Length of original content
        """
        return len(content)
    
    def remove_descriptions_and_linefeeds(self, content: str) -> str:
        """
        Remove FASTA sequence descriptions and all linefeed characters
        using regex pattern matching as specified.
        
        Args:
            content: Raw FASTA content
            
        Returns:
            str: Cleaned sequence without descriptions and linefeeds
        """
        # Remove FASTA description lines (lines starting with >)
        # This regex matches entire lines starting with >
        content_no_desc = re.sub(r'>.*\n', '', content)
        
        # Remove all linefeed characters (newlines)
        content_clean = re.sub(r'\n', '', content_no_desc)
        
        return content_clean
    
    def count_dna_patterns(self, sequence: str) -> List[Tuple[str, int]]:
        """
        Count occurrences of DNA 8-mer patterns and their reverse complements.
        
        Args:
            sequence: Clean DNA sequence string
            
        Returns:
            List of tuples containing (pattern, count)
        """
        pattern_counts = []
        
        for i, pattern in enumerate(self.dna_patterns):
            # Use compiled regex for efficiency
            matches = self.compiled_dna_patterns[i].findall(sequence)
            count = len(matches)
            pattern_counts.append((pattern, count))
            
        return pattern_counts
    
    def apply_magic_transformations(self, sequence: str) -> str:
        """
        Apply magic regex transformations in specified order.
        
        Args:
            sequence: DNA sequence to transform
            
        Returns:
            str: Transformed sequence
        """
        result = sequence
        
        # Apply each transformation pattern in order
        for compiled_pattern, replacement in self.compiled_magic_patterns:
            result = compiled_pattern.sub(replacement, result)
            
        return result
    
    def process_fasta(self) -> None:
        """
        Main processing algorithm following exact specification:
        1. Read FASTA from stdin and record length
        2. Remove descriptions/linefeeds and record length  
        3. Count DNA pattern matches
        4. Apply magic transformations and record final length
        5. Output all results
        """
        print("Starting regex-redux FASTA processing...", file=sys.stderr)
        
        # Step 1: Read all FASTA data from stdin
        fasta_content = self.read_fasta_from_stdin()
        original_length = self.get_original_length(fasta_content)
        
        # Step 2: Remove FASTA descriptions and linefeeds
        clean_sequence = self.remove_descriptions_and_linefeeds(fasta_content)
        clean_length = len(clean_sequence)
        
        # Step 3: Count DNA 8-mer patterns
        pattern_counts = self.count_dna_patterns(clean_sequence)
        
        # Step 4: Apply magic regex transformations
        transformed_sequence = self.apply_magic_transformations(clean_sequence)
        final_length = len(transformed_sequence)
        
        # Output results as specified
        print("\nDNA Pattern Match Counts:")
        print("-" * 40)
        for pattern, count in pattern_counts:
            print(f"{pattern} {count}")
        
        print(f"\nSequence Lengths:")
        print("-" * 20)
        print(f"Original length: {original_length}")
        print(f"Clean length: {clean_length}")
        print(f"Final length: {final_length}")


def generate_test_fasta(length: int, filename: str) -> None:
    """
    Generate a larger FASTA test file for performance testing.
    
    Args:
        length: Desired sequence length
        filename: Output filename
    """
    import random
    
    # DNA nucleotides
    nucleotides = ['A', 'T', 'G', 'C']
    
    with open(filename, 'w') as f:
        # Write FASTA header
        f.write(f">Generated DNA sequence of length {length}\n")
        
        # Generate random DNA sequence with line breaks every 80 characters
        for i in range(length):
            if i % 80 == 0 and i > 0:
                f.write('\n')
            f.write(random.choice(nucleotides))
        
        f.write('\n')
    
    print(f"Generated test file: {filename} with {length} nucleotides")


def main():
    """
    Main entry point for the regex-redux FASTA processor.
    """
    if len(sys.argv) > 1:
        # Generate test file mode
        try:
            length = int(sys.argv[1])
            filename = f"input{length}.txt"
            generate_test_fasta(length, filename)
            print(f"Use: cat {filename} | python3 {sys.argv[0]}")
        except ValueError:
            print("Usage for generation: python3 script.py <sequence_length>")
            sys.exit(1)
    else:
        # Normal processing mode
        processor = RegexReduxProcessor()
        processor.process_fasta()


if __name__ == "__main__":
    main()