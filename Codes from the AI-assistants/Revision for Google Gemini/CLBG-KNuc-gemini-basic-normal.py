import sys
from collections import defaultdict
from multiprocessing import Pool
def read_sequence_three(file_obj):
    """
    Reads the FASTA file from the given file object.
    Skips everything until it finds the '>THREE' identifier,
    then reads the sequence until the next identifier or EOF.
    """
    for line in file_obj:
        if line.startswith(">THREE"):
            break
            
    sequence_lines = []
    for line in file_obj:
        if line.startswith(">"):
            break
        # FASTA files can contain newlines; strip them and build the sequence
        sequence_lines.append(line.strip().encode('ascii'))
        
    return b"".join(sequence_lines).upper()
def count_kmers(args):
    """
    Procedure to update a hash table (defaultdict) of k-nucleotide keys.
    Processes all reading-frames by using a sliding window of length k.
    """
    sequence, k = args
    counts = defaultdict(int)
    
    # Calculate counts for all reading frames combined
    limit = len(sequence) - k + 1
    for i in range(limit):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
        
    return counts
def calculate_frequencies(sequence, k):
    """Counts k-mers and formats them as percentage frequencies."""
    counts = count_kmers((sequence, k))
    total_kmers = sum(counts.values())
    
    # Sort by frequency (descending), then by key (ascending)
    sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    
    results = []
    for kmer, count in sorted_counts:
        freq = (count * 100.0) / total_kmers
        results.append(f"{kmer.decode('ascii')} {freq:.3f}")
    
    return "\n".join(results) + "\n"
def calculate_specific_count(sequence, specific_kmer):
    """Counts k-mers and returns the exact count of a specific sequence."""
    k = len(specific_kmer)
    counts = count_kmers((sequence, k))
    kmer_bytes = specific_kmer.encode('ascii')
    
    count = counts.get(kmer_bytes, 0)
    return f"{count}\t{specific_kmer}"
def main():
    # 1. Read sequence THREE from stdin
    sequence = read_sequence_three(sys.stdin)
    
    if not sequence:
        return
# 2. Setup multiprocessing pool to compute tasks concurrently
    # This prevents optimizing away the work while making the script performant
    pool = Pool()
    
    # Dispatch frequency tasks
    freq_tasks = [
        pool.apply_async(calculate_frequencies, (sequence, 1)),
        pool.apply_async(calculate_frequencies, (sequence, 2))
    ]
    
    # Dispatch specific count tasks
    specific_sequences = [
        "GGT", 
        "GGTA", 
        "GGTATT", 
        "GGTATTTTAATT", 
        "GGTATTTTAATTTATAGT"
    ]
    count_tasks = [
        pool.apply_async(calculate_specific_count, (sequence, seq)) 
        for seq in specific_sequences
    ]
    
    pool.close()
    pool.join()
# 3. Print 1-nucleotide and 2-nucleotide frequencies
    for task in freq_tasks:
        print(task.get())
# 4. Print specific counts for 3, 4, 6, 12, and 18-nucleotide sequences
    for task in count_tasks:
        print(task.get())
if __name__ == "__main__":
    main()
