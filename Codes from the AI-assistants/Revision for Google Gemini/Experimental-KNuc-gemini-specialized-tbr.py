import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Tuple

def extract_sequence(filepath: str, identifier: str = ">THREE") -> str:
    """
    Streams the FASTA file to find a specific sequence and loads it into memory.
    """
    seq_chunks = []
    try:
        with open(filepath, 'r') as file:
            # Fast-forward to the target sequence
            for line in file:
                if line.startswith(identifier):
                    break
            
            # Accumulate sequence chunks until the next identifier or EOF
            for line in file:
                if line.startswith(">"):
                    break
                seq_chunks.append(line.strip().upper())
                
    except FileNotFoundError:
        print(f"Error: Could not find file at '{filepath}'", file=sys.stderr)
        sys.exit(1)
        
    return "".join(seq_chunks)

def calculate_kmer_frequencies(sequence: str, k: int) -> Dict[str, int]:
    """
    Slides a window of size 'k' over the sequence to count k-mer occurrences 
    using Python's native optimized hash table (dict).
    """
    counts: Dict[str, int] = defaultdict(int)
    limit = len(sequence) - k + 1
    
    # Sliding window extraction
    for i in range(limit):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
        
    return counts

def get_percentage_distribution(sequence: str, k: int) -> List[Tuple[str, float]]:
    """
    Calculates the frequency percentages of all k-mers of a given length.
    """
    counts = calculate_kmer_frequencies(sequence, k)
    total_kmers = sum(counts.values())
    
    # Sort by frequency descending, then by sequence ascending alphabetically
    sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    
    return [(kmer, (count / total_kmers) * 100.0) for kmer, count in sorted_counts]

def count_specific_kmer(sequence: str, kmer: str) -> Tuple[int, str]:
    """
    Returns the exact occurrence count of a specific k-mer.
    """
    counts = calculate_kmer_frequencies(sequence, len(kmer))
    return counts.get(kmer, 0), kmer

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <fasta_file>", file=sys.stderr)
        sys.exit(1)
        
    fasta_file = sys.argv[1]
    sequence = extract_sequence(fasta_file)
    
    if not sequence:
        print("Error: Target sequence not found or is empty.", file=sys.stderr)
        sys.exit(1)

    # Standard lengths and specific k-mers required by the simulation
    lengths_to_percent = [1, 2]
    specific_kmers = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]

    # Utilize ProcessPoolExecutor to distribute workloads across available CPU cores.
    # Python's GIL is bypassed here because each process runs its own interpreter.
    with ProcessPoolExecutor() as executor:
        # Scatter phase: schedule the tasks asynchronously
        percent_futures = [executor.submit(get_percentage_distribution, sequence, length) 
                           for length in lengths_to_percent]
        
        count_futures = [executor.submit(count_specific_kmer, sequence, kmer) 
                         for kmer in specific_kmers]
        
        # Gather phase: await results and format output
        for future in percent_futures:
            for kmer, percentage in future.result():
                print(f"{kmer} {percentage:.3f}")
            print()
            
        for future in count_futures:
            count, kmer = future.result()
            print(f"{count}\t{kmer}")

if __name__ == "__main__":
    main()