import sys
from multiprocessing import Pool

def count_kmers(sequence, k):
    """Updates a hash table of k-nucleotide keys and count values."""
    counts = {}
    # Sliding window over the sequence
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i + k]
        counts[kmer] = counts.get(kmer, 0) + 1
    return counts

def format_freq(counts):
    """Sorts and formats 1-nucleotide and 2-nucleotide frequencies."""
    total = sum(counts.values())
    # Sort by frequency descending, then key ascending
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return "\n".join(f"{k} {v * 100 / total:.3f}" for k, v in sorted_counts)

def format_specific(counts, kmer):
    """Returns the count for a specific k-nucleotide sequence."""
    return f"{counts.get(kmer, 0)}\t{kmer}"

def solve():
    # 1. Extract DNA sequence THREE
    lines = sys.stdin
    for line in lines:
        if line.startswith(">THREE"):
            break
            
    sequence = []
    for line in lines:
        if line.startswith(">"):
            break
        sequence.append(line.strip().upper())
    
    full_seq = "".join(sequence)
    
    # 2. Parallel processing for different k-mer lengths
    # We define the tasks: (length, specific_string_if_needed)
    tasks = [1, 2, 3, 4, 6, 12, 18]
    
    with Pool() as pool:
        # Calculate counts for each k in parallel
        results = pool.starmap(count_kmers, [(full_seq, k) for k in tasks])
    
    # Mapping results back to lengths for easy access
    res_map = dict(zip(tasks, results))

    # 3. Output results
    # 1-nucleotide and 2-nucleotide frequencies
    print(format_freq(res_map[1]))
    print()
    print(format_freq(res_map[2]))
    print()

    # Specific sequences
    specifics = [
        (3, "GGT"), (4, "GGTA"), (6, "GGTATT"), 
        (12, "GGTATTTTAATT"), (18, "GGTATTTTAATTTATAGT")
    ]
    for k, seq in specifics:
        print(format_specific(res_map[k], seq))

if __name__ == "__main__":
    solve()