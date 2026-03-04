#!/usr/bin/env python3
"""
k-nucleotide solution using Python's native collections and optimized for Ubuntu 24.04
"""
import sys
import mmap
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple
import os
from pathlib import Path

@dataclass
class SequenceData:
    """Store parsed sequence information"""
    description: str
    sequence: str
    length: int

class KNucleotideCounter:
    """Efficient nucleotide frequency counter using native Python data structures"""
    
    COMPLEMENT = str.maketrans('ACGTacgt', 'TGCAtgca')
    
    def __init__(self):
        self.sequence = ""
        self.total_length = 0
        
    def read_fasta_file(self, filepath: str) -> None:
        """Read FASTA file using memory mapping for efficiency"""
        try:
            with open(filepath, 'r') as f:
                # Use memory-mapped file for large sequences
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    content = mm.read().decode('utf-8')
                    
                # Find the 'THREE' section as per benchmark spec
                lines = content.split('\n')
                capture = False
                sequence_parts = []
                
                for line in lines:
                    if line.startswith('>THREE'):
                        capture = True
                        continue
                    if line.startswith('>') and capture:
                        break
                    if capture and line.strip():
                        # Remove whitespace and comments
                        seq_line = line.split()[0] if line.split() else line
                        sequence_parts.append(seq_line.upper())
                
                self.sequence = ''.join(sequence_parts)
                self.total_length = len(self.sequence)
                
                if not self.sequence:
                    raise ValueError("No valid sequence found in file")
                    
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    
    def count_single_nucleotides(self) -> Dict[str, int]:
        """Count A, T, G, C using str.count()"""
        return {
            'A': self.sequence.count('A'),
            'T': self.sequence.count('T'),
            'G': self.sequence.count('G'),
            'C': self.sequence.count('C')
        }
    
    def count_k_mers(self, k: int) -> Counter:
        """Count all k-mers in the sequence"""
        if k <= 0 or k > len(self.sequence):
            return Counter()
        
        counts = Counter()
        # Pre-compute slices for efficiency
        seq = self.sequence
        for i in range(len(seq) - k + 1):
            kmer = seq[i:i+k]
            counts[kmer] += 1
            
        return counts
    
    def count_specific_sequences(self) -> Dict[str, int]:
        """Count specific sequences as per benchmark requirements"""
        specific_counts = {}
        
        # Single nucleotides (already counted)
        single_counts = self.count_single_nucleotides()
        specific_counts.update(single_counts)
        
        # Dinucleotides
        dinucs = ['AA', 'AC', 'AG', 'AT', 'CA', 'CC', 'CG', 'CT',
                  'GA', 'GC', 'GG', 'GT', 'TA', 'TC', 'TG', 'TT']
        for dinuc in dinucs:
            specific_counts[dinuc] = self.sequence.count(dinuc)
        
        # Specific patterns from the benchmark
        patterns = [
            'GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT',
            'GGTATTTTAATTTATAGT'
        ]
        for pattern in patterns:
            specific_counts[pattern] = self.sequence.count(pattern)
            
        return specific_counts
    
    def find_most_frequent_kmers(self, k: int, top_n: int = 7) -> List[Tuple[str, int]]:
        """Find top N most frequent k-mers"""
        counts = self.count_k_mers(k)
        
        # Sort by frequency (descending), then by k-mer (ascending)
        sorted_items = sorted(
            counts.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        return sorted_items[:top_n]
    
    def reverse_complement(self, sequence: str) -> str:
        """Get reverse complement of a DNA sequence"""
        return sequence.translate(self.COMPLEMENT)[::-1]
    
    def parallel_count_kmers(self, k: int) -> Dict[str, int]:
        """
        Count k-mers considering both strands (sequence and its reverse complement)
        This handles the 'canonical' representation
        """
        if k <= 0:
            return {}
        
        counts = defaultdict(int)
        seq = self.sequence
        seq_len = len(seq)
        
        for i in range(seq_len - k + 1):
            kmer = seq[i:i+k]
            # Get canonical form (lexicographically smaller of kmer and its reverse complement)
            rc_kmer = self.reverse_complement(kmer)
            canonical = min(kmer, rc_kmer)
            counts[canonical] += 1
            
        return dict(counts)
    
    def calculate_frequencies(self, k: int) -> List[Tuple[str, float]]:
        """Calculate frequencies of all k-mers"""
        total_kmers = max(1, self.total_length - k + 1)
        counts = self.count_k_mers(k)
        
        frequencies = []
        for kmer, count in counts.items():
            frequency = (count / total_kmers) * 100
            frequencies.append((kmer, frequency))
            
        # Sort by k-mer for consistent output
        frequencies.sort(key=lambda x: x[0])
        return frequencies
    
    def print_results(self) -> None:
        """Print results in benchmark format"""
        print(f"Total sequence length: {self.total_length:,} bp")
        print("\n1. Single nucleotide counts:")
        single_counts = self.count_single_nucleotides()
        for base in ['A', 'C', 'G', 'T']:
            count = single_counts.get(base, 0)
            print(f"{base}: {count:,} ({count/self.total_length*100:.2f}%)")
        
        print("\n2. Dinucleotide frequencies:")
        dinuc_counts = self.count_k_mers(2)
        for kmer in sorted(dinuc_counts.keys()):
            count = dinuc_counts[kmer]
            freq = (count / (self.total_length - 1)) * 100
            print(f"{kmer}: {count:,} ({freq:.3f}%)")
        
        print("\n3. Top 10 most frequent 4-mers:")
        top_4mers = self.find_most_frequent_kmers(4, 10)
        for kmer, count in top_4mers:
            freq = (count / (self.total_length - 3)) * 100
            print(f"{kmer}\t{count:,}\t{freq:.3f}%")
        
        print("\n4. Specific sequence counts (benchmark patterns):")
        specific = self.count_specific_sequences()
        benchmark_patterns = ['GGT', 'GGTA', 'GGTATT', 'GGTATTTTAATT', 'GGTATTTTAATTTATAGT']
        for pattern in benchmark_patterns:
            count = specific.get(pattern, 0)
            if pattern in self.sequence:
                print(f"{pattern}: {count:,}")
            else:
                # Check reverse complement
                rc_pattern = self.reverse_complement(pattern)
                count = self.sequence.count(rc_pattern)
                print(f"{pattern} (reverse complement): {count:,}")
        
        # Memory usage report
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024
        print(f"\nMemory usage: {memory_usage:.2f} MB")

def main():
    if len(sys.argv) != 2:
        print("Usage: python knucleotide.py <fasta_file>")
        print("Example: python knucleotide.py input.fasta")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist")
        sys.exit(1)
    
    print(f"Processing: {filepath}")
    print("=" * 50)
    
    # Initialize counter and process
    counter = KNucleotideCounter()
    
    try:
        counter.read_fasta_file(filepath)
        counter.print_results()
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()