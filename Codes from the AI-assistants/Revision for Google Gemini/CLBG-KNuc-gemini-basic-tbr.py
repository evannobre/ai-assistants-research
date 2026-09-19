import sys
from collections import defaultdict
from multiprocessing import Pool
def get_sequence_three():
    """
    Reads a FASTA format file from stdin and extracts DNA sequence THREE.
    Uses an iterative approach to minimize memory footprint.
    """
    seq_parts = []
    in_three = False
    
    for line in sys.stdin:
        if line.startswith('>'):
            if in_three:
                break # We've reached the end of sequence THREE
            if line.startswith('>THREE'):
                in_three = True
        elif in_three:
            seq_parts.append(line.strip().upper())
            
    return "".join(seq_parts)
def update_k_nucleotide_counts(args):
    """
    The core procedure to update a hash table of k-nucleotide keys.
    We iterate over the reading frame and update the count for each sequence.
    """
    sequence, k = args
    # Using Python's native built-in dictionary/hash-table
    counts = defaultdict(int)
    
    # Calculate bounds for combined reading-frames
    for i in range(len(sequence) - k + 1):
        k_mer = sequence[i:i+k]
        # Lookup the count for a key and update it
        counts[k_mer] += 1
        
    return counts
def main():
    # 1. Read from stdin and extract sequence
    sequence = get_sequence_three()
    if not sequence:
        print("Sequence >THREE not found.", file=sys.stderr)
        return
# Specific sequences we need to find exact counts for
    specific_sequences = [
        "GGT", 
        "GGTA", 
        "GGTATT", 
        "GGTATTTTAATT", 
        "GGTATTTTAATTTATAGT"
    ]
    
    # K-mer lengths required: 1, 2, 3, 4, 6, 12, 18
    k_values = [1, 2] + [len(seq) for seq in specific_sequences]
    
    # Map the work to a pool of worker processes to process all k-lengths in parallel
    pool_args = [(sequence, k) for k in k_values]
    with Pool() as pool:
        results = pool.map(update_k_nucleotide_counts, pool_args)
# 2. Print 1-nucleotide and 2-nucleotide percentage frequencies
    for i in range(2):
        counts = results[i]
        total_k_mers = sum(counts.values())
        
        # Sort by descending frequency (-item[1]), then ascending key (item[0])
        sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        
        for k_mer, count in sorted_counts:
            # Calculate percentage frequency
            percentage = (count * 100.0) / total_k_mers
            print(f"{k_mer} {percentage:.3f}")
        print() # Empty line between blocks
# 3. Print counts for specific sequences
    for i, target_seq in enumerate(specific_sequences, start=2):
        counts = results[i]
        # Lookup exact sequence count, default to 0 if not found
        count = counts.get(target_seq, 0)
        print(f"{count}\t{target_seq}")
if __name__ == "__main__":
    main()
