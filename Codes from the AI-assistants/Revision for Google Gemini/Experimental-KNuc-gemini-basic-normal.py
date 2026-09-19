import sys
from multiprocessing import Pool
from collections import defaultdict

def extract_sequence(filepath, sequence_name=">THREE"):
    """
    Parses the FASTA file and extracts the DNA sequence for the given identifier.
    Uses generators/line-reading to keep memory overhead low during parsing.
    """
    seq_lines = []
    with open(filepath, 'r') as file:
        # Step 1: Fast-forward to the target sequence
        for line in file:
            if line.startswith(sequence_name):
                break
                
        # Step 2: Read the sequence until the next identifier or EOF
        for line in file:
            if line.startswith(">"):
                break
            seq_lines.append(line.strip().upper())
            
    return "".join(seq_lines)

def count_kmers(args):
    """
    Counts k-mers using a sliding window and Python's native hash map (dict).
    """
    seq, k = args
    counts = defaultdict(int)
    
    # Slide a window of size 'k' across the sequence
    limit = len(seq) - k + 1
    for i in range(limit):
        kmer = seq[i:i+k]
        counts[kmer] += 1
        
    return counts

def print_frequencies(counts):
    """
    Calculates and prints the frequency percentages of k-mers.
    Sorted by frequency descending, then alphabetically ascending.
    """
    total = sum(counts.values())
    # Sort key: (-count, kmer_string) achieves the exact required sorting
    sorted_kmers = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    for kmer, count in sorted_kmers:
        freq = (count * 100.0) / total
        print(f"{kmer} {freq:.3f}")
    print()

def print_specific_count(counts, target_kmer):
    """
    Prints the absolute count of a specific k-mer.
    """
    # Native O(1) hash map lookup
    count = counts.get(target_kmer, 0)
    print(f"{count}\t{target_kmer}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python knucleotide.py <path_to_fasta_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    
    # 1. Read the DNA sequence
    try:
        seq = extract_sequence(filepath)
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        sys.exit(1)

    if not seq:
        print("Error: Target sequence '>THREE' not found or is empty.")
        sys.exit(1)

    # 2. Define the tasks required by the benchmark
    frequency_k_values = [1, 2]
    specific_kmers = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    
    # Aggregate all distinct k-lengths we need to count
    all_k_values = frequency_k_values + [len(kmer) for kmer in specific_kmers]
    
    # 3. Parallelize the counting process using native multiprocessing
    # Pass the sequence and the required k-size to the worker pool
    tasks = [(seq, k) for k in all_k_values]
    
    with Pool() as pool:
        # map() blocks until all processes return their hash maps
        results = pool.map(count_kmers, tasks)

    # 4. Format and output the results
    # The first two results correspond to k=1 and k=2 frequencies
    print_frequencies(results[0])
    print_frequencies(results[1])

    # The remaining results map directly to our specific_kmers list
    specific_counts_results = results[2:]
    for kmer, counts_dict in zip(specific_kmers, specific_counts_results):
        print_specific_count(counts_dict, kmer)

if __name__ == '__main__':
    main()