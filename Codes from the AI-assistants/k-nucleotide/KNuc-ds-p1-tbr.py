import sys
import collections
import itertools
from multiprocessing import Pool
from typing import Dict, List, Tuple

def read_fasta(file_path: str) -> str:
    """Read FASTA file and extract DNA sequence after '>THREE'."""
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
    
    # Find and extract sequence after '>THREE'
    start = False
    seq_parts = []
    for line in lines:
        if line.startswith('>THREE'):
            start = True
            continue
        if line.startswith('>'):
            if start:
                break
            continue
        if start:
            seq_parts.append(line.upper())
    
    return ''.join(seq_parts)

def count_kmers_sequential(seq: str, k: int) -> Dict[str, int]:
    """Count k-mers using sliding window and collections.Counter."""
    # Use generator expression for memory efficiency
    kmers = (seq[i:i+k] for i in range(len(seq) - k + 1))
    return collections.Counter(kmers)

def count_kmers_parallel(seq: str, k: int, workers: int = 4) -> Dict[str, int]:
    """Parallel k-mer counting using multiprocessing."""
    chunk_size = len(seq) // workers + k  # Add overlap to avoid missing kmers
    chunks = []
    
    for i in range(workers):
        start = i * chunk_size
        end = min(start + chunk_size + k - 1, len(seq))
        if start < len(seq):
            chunks.append(seq[start:end])
    
    with Pool(workers) as pool:
        results = pool.starmap(count_kmers_sequential, [(chunk, k) for chunk in chunks])
    
    # Merge results
    total_counter = collections.Counter()
    for counter in results:
        total_counter.update(counter)
    
    return total_counter

def calculate_frequencies(seq: str) -> List[Tuple[int, Dict[str, float]]]:
    """Calculate frequencies for all required k-values."""
    results = []
    
    # Counts for all required k values
    for k in [1, 2, 3, 4, 6, 12, 18]:
        if len(seq) >= k:
            # Use parallel counting for larger k-mers
            if k >= 6:
                counts = count_kmers_parallel(seq, k)
            else:
                counts = count_kmers_sequential(seq, k)
            
            # Calculate frequencies
            total = sum(counts.values())
            freqs = {kmer: (count / total) * 100 for kmer, count in counts.items()}
            results.append((k, freqs))
    
    return results

def get_sorted_frequencies(freqs: Dict[str, float]) -> List[Tuple[str, float]]:
    """Sort frequencies by count (descending) then by k-mer (ascending)."""
    return sorted(freqs.items(), key=lambda x: (-x[1], x[0]))

def format_output(all_freqs: List[Tuple[int, Dict[str, float]]], seq: str) -> str:
    """Format output according to benchmark specifications."""
    output_lines = []
    
    for k, freqs in all_freqs:
        if k in [1, 2]:
            # For k=1, output all nucleotides in fixed order
            if k == 1:
                for nuc in ['A', 'C', 'G', 'T']:
                    freq = freqs.get(nuc, 0.0)
                    output_lines.append(f"{nuc} {freq:.3f}")
            # For k=2, output all 16 dinucleotides sorted
            else:
                # Generate all possible 2-mers
                nucleotides = ['A', 'C', 'G', 'T']
                all_2mers = [f"{a}{b}" for a in nucleotides for b in nucleotides]
                two_mer_freqs = {kmer: freqs.get(kmer, 0.0) for kmer in all_2mers}
                sorted_2mers = get_sorted_frequencies(two_mer_freqs)
                for kmer, freq in sorted_2mers:
                    output_lines.append(f"{kmer} {freq:.3f}")
        else:
            # For other k values, output specific k-mers if they exist
            specific_kmers = {
                3: ['GGT'],
                4: ['GGTA'],
                6: ['GGTATT'],
                12: ['GGTATTTTAATT'],
                18: ['GGTATTTTAATTTATAGT']
            }
            if k in specific_kmers:
                for kmer in specific_kmers[k]:
                    freq = freqs.get(kmer, 0.0)
                    output_lines.append(f"{kmer} {freq:.3f}")
    
    # Add top 10 18-mers
    if len(seq) >= 18:
        _, freq_18 = next((k, f) for k, f in all_freqs if k == 18)
        top_10 = get_sorted_frequencies(freq_18)[:10]
        for kmer, freq in top_10:
            output_lines.append(f"{kmer} {freq:.3f}")
    
    return '\n'.join(output_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python knucleotide.py <input_file>")
        sys.exit(1)
    
    # Read and process sequence
    seq = read_fasta(sys.argv[1])
    
    # Calculate all frequencies
    all_freqs = calculate_frequencies(seq)
    
    # Format and print output
    print(format_output(all_freqs, seq))

if __name__ == "__main__":
    main()