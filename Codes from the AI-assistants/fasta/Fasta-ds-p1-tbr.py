import sys
import time
import math
import itertools
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Generator
import gzip
import io


class NaiveLCG:
    """Linear Congruential Generator using native arithmetic only"""
    
    def __init__(self, seed: int = None, 
                 multiplier: int = 1103515245,
                 increment: int = 12345,
                 modulus: int = 2**31):
        """
        Initialize LCG with parameters (using ANSI C parameters by default)
        Formula: X_{n+1} = (a * X_n + c) % m
        """
        self.multiplier = multiplier
        self.increment = increment
        self.modulus = modulus
        self.state = seed if seed is not None else int(time.time() * 1000) % modulus
    
    def next(self) -> float:
        """Generate next random number in [0, 1)"""
        self.state = (self.multiplier * self.state + self.increment) % self.modulus
        return self.state / self.modulus
    
    def randint(self, low: int, high: int) -> int:
        """Generate random integer in [low, high] inclusive"""
        return low + int(self.next() * (high - low + 1))
    
    def choice(self, sequence: List) -> any:
        """Random choice from sequence using LCG"""
        idx = self.randint(0, len(sequence) - 1)
        return sequence[idx]
    
    def sample(self, population: List, k: int) -> List:
        """Simple sampling without replacement"""
        if k > len(population):
            raise ValueError("Sample larger than population")
        
        # Fisher-Yates shuffle using LCG
        result = population[:]
        for i in range(len(result) - 1, len(result) - k - 1, -1):
            j = self.randint(0, i)
            result[i], result[j] = result[j], result[i]
        
        return result[-k:]


class FASTASimulator:
    """FASTA format simulator using LCG for randomness"""
    
    # DNA nucleotide frequencies (approximate human genome)
    NUCLEOTIDES = ['A', 'C', 'G', 'T']
    DEFAULT_FREQUENCIES = {'A': 0.295, 'C': 0.205, 'G': 0.205, 'T': 0.295}
    
    # Amino acid codons (simplified)
    CODON_TABLE = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
        'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W',
    }
    
    def __init__(self, seed: int = None):
        """Initialize simulator with LCG"""
        self.lcg = NaiveLCG(seed)
        self.sequences = []
    
    def generate_dna_sequence(self, length: int, 
                             frequencies: Dict[str, float] = None) -> str:
        """
        Generate random DNA sequence using LCG with given frequencies
        """
        if frequencies is None:
            frequencies = self.DEFAULT_FREQUENCIES
        
        # Validate frequencies
        if not math.isclose(sum(frequencies.values()), 1.0, rel_tol=1e-9):
            raise ValueError("Frequencies must sum to 1.0")
        
        # Create cumulative distribution
        cumulative = []
        current = 0.0
        for nt in self.NUCLEOTIDES:
            current += frequencies.get(nt, 0.0)
            cumulative.append((nt, current))
        
        # Generate sequence using LCG
        sequence = []
        for _ in range(length):
            r = self.lcg.next()
            for nt, prob in cumulative:
                if r < prob:
                    sequence.append(nt)
                    break
        
        return ''.join(sequence)
    
    def simulate_mutation(self, sequence: str, 
                         mutation_rate: float = 1e-6) -> str:
        """
        Simulate mutations using LCG
        """
        if mutation_rate <= 0:
            return sequence
        
        seq_list = list(sequence)
        mutations = 0
        
        for i in range(len(seq_list)):
            if self.lcg.next() < mutation_rate:
                # Choose different nucleotide
                current = seq_list[i]
                alternatives = [nt for nt in self.NUCLEOTIDES if nt != current]
                seq_list[i] = self.lcg.choice(alternatives)
                mutations += 1
        
        return ''.join(seq_list), mutations
    
    def generate_coding_sequence(self, length: int) -> str:
        """
        Generate protein-coding DNA sequence (length must be multiple of 3)
        """
        if length % 3 != 0:
            length = (length // 3) * 3
        
        # Generate sequence with start and stop codons
        codons = list(self.CODON_TABLE.keys())
        
        # Start with start codon (ATG)
        sequence = ['ATG']
        
        # Add middle codons (avoid stop codons)
        middle_codons = [c for c in codons if self.CODON_TABLE[c] != '*']
        for _ in range(length // 3 - 2):
            sequence.append(self.lcg.choice(middle_codons))
        
        # End with stop codon
        stop_codons = [c for c in codons if self.CODON_TABLE[c] == '*']
        sequence.append(self.lcg.choice(stop_codons))
        
        return ''.join(sequence)
    
    def translate_dna(self, dna_sequence: str) -> str:
        """
        Translate DNA sequence to protein using codon table
        """
        protein = []
        for i in range(0, len(dna_sequence) - 2, 3):
            codon = dna_sequence[i:i+3]
            if len(codon) == 3:
                protein.append(self.CODON_TABLE.get(codon, 'X'))
        return ''.join(protein)
    
    def generate_fasta_record(self, sequence_id: str, 
                             sequence: str, 
                             line_length: int = 60) -> str:
        """
        Format sequence as FASTA record
        """
        lines = [f'>{sequence_id}']
        
        # Split sequence into lines of specified length
        for i in range(0, len(sequence), line_length):
            lines.append(sequence[i:i+line_length])
        
        return '\n'.join(lines)
    
    def simulate_population(self, num_individuals: int,
                           sequence_length: int,
                           mutation_rate: float = 1e-6) -> List[Tuple[str, str]]:
        """
        Simulate population with genetic variation using LCG
        """
        # Generate ancestral sequence
        ancestral = self.generate_dna_sequence(sequence_length)
        
        population = []
        for i in range(num_individuals):
            # Each individual gets mutations from ancestral
            individual_seq, mut_count = self.simulate_mutation(
                ancestral, mutation_rate
            )
            population.append((f"INDV_{i:04d}", individual_seq, mut_count))
        
        return population
    
    def calculate_statistics(self, sequences: List[str]) -> Dict:
        """
        Calculate basic sequence statistics using collections module
        """
        all_stats = []
        
        for seq in sequences:
            # Use Counter for frequency analysis
            counter = Counter(seq)
            total = len(seq)
            
            stats = {
                'length': total,
                'gc_content': (counter.get('G', 0) + counter.get('C', 0)) / total * 100,
                'nucleotide_counts': dict(counter),
                'entropy': self._calculate_entropy(counter, total)
            }
            all_stats.append(stats)
        
        # Aggregate statistics
        return {
            'individual_stats': all_stats,
            'average_gc': sum(s['gc_content'] for s in all_stats) / len(all_stats),
            'total_sequences': len(sequences)
        }
    
    def _calculate_entropy(self, counter: Counter, total: int) -> float:
        """Calculate Shannon entropy of sequence"""
        entropy = 0.0
        for count in counter.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def write_fasta_file(self, filename: str, 
                        records: List[Tuple[str, str]],
                        compress: bool = False):
        """
        Write FASTA file using native file I/O
        """
        if compress:
            opener = gzip.open
            filename = f"{filename}.gz"
        else:
            opener = open
        
        with opener(filename, 'wt', encoding='utf-8') as f:
            for seq_id, sequence in records:
                f.write(self.generate_fasta_record(seq_id, sequence))
                f.write('\n')
    
    def read_fasta_file(self, filename: str) -> List[Tuple[str, str]]:
        """
        Read FASTA file using native file I/O
        """
        records = []
        current_id = None
        current_seq = []
        
        if filename.endswith('.gz'):
            opener = gzip.open
        else:
            opener = open
        
        with opener(filename, 'rt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id is not None:
                        records.append((current_id, ''.join(current_seq)))
                    current_id = line[1:].split()[0]
                    current_seq = []
                else:
                    current_seq.append(line)
            
            if current_id is not None:
                records.append((current_id, ''.join(current_seq)))
        
        return records


def main():
    """Example usage of the FASTA simulator"""
    
    # Initialize simulator with seed for reproducibility
    simulator = FASTASimulator(seed=42)
    
    print("=== FASTA Simulation using Naive LCG ===")
    
    # 1. Generate random DNA sequences
    print("\n1. Generating random DNA sequences...")
    sequences = []
    for i in range(5):
        seq = simulator.generate_dna_sequence(100)
        sequences.append((f"RANDOM_SEQ_{i}", seq))
        print(f"  Sequence {i}: {seq[:50]}...")
    
    # 2. Simulate population with mutations
    print("\n2. Simulating population genetics...")
    population = simulator.simulate_population(
        num_individuals=10,
        sequence_length=100,
        mutation_rate=0.001  # Higher rate for demonstration
    )
    
    for seq_id, seq, mut_count in population[:3]:
        print(f"  {seq_id}: {mut_count} mutations, {seq[:50]}...")
    
    # 3. Calculate statistics
    print("\n3. Calculating sequence statistics...")
    stats = simulator.calculate_statistics([seq for _, seq, _ in population])
    print(f"  Average GC content: {stats['average_gc']:.2f}%")
    print(f"  Total sequences analyzed: {stats['total_sequences']}")
    
    # 4. Generate coding sequence
    print("\n4. Generating protein-coding sequence...")
    coding_seq = simulator.generate_coding_sequence(99)  # Will round to 99
    protein = simulator.translate_dna(coding_seq)
    print(f"  DNA: {coding_seq[:50]}...")
    print(f"  Protein: {protein[:20]}...")
    
    # 5. Write to FASTA file
    print("\n5. Writing to FASTA file...")
    records = [(f"SEQ_{i}", simulator.generate_dna_sequence(200)) 
               for i in range(3)]
    simulator.write_fasta_file("simulated_sequences.fasta", records)
    print("  File written: simulated_sequences.fasta")
    
    # 6. Demonstrate LCG properties
    print("\n6. LCG Randomness Analysis...")
    lcg = NaiveLCG(seed=12345)
    random_numbers = [lcg.next() for _ in range(1000)]
    
    # Basic statistics using native modules
    avg = sum(random_numbers) / len(random_numbers)
    variance = sum((x - avg) ** 2 for x in random_numbers) / len(random_numbers)
    
    print(f"  Mean: {avg:.4f} (expected: ~0.5)")
    print(f"  Variance: {variance:.4f} (expected: ~1/12 ≈ 0.0833)")
    
    # Test uniform distribution
    bins = [0] * 10
    for num in random_numbers:
        idx = int(num * 10)
        if idx == 10:  # Handle edge case for 1.0
            idx = 9
        bins[idx] += 1
    
    print(f"  Distribution test: {bins}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())