import sys
from collections import defaultdict

def read_sequence(file_path):
    """
    Reads a FASTA file and extracts the sequence associated with '>THREE'.
    """
    seq_lines = []
    try:
        with open(file_path, 'r') as f:
            # Skip lines until ">THREE" is found
            for line in f:
                if line.startswith(">THREE"):
                    break
            
            # Read the sequence lines
            for line in f:
                if line.startswith(">"):
                    break
                seq_lines.append(line.strip().upper())
                
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
        
    return "".join(seq_lines)

def get_frequencies(seq, k):
    """
    Generates overlapping k-mers and counts them using a native hash table.
    """
    counts = defaultdict(int)
    # The bound ensures we don't go out of index range
    bound = len(seq) - k + 1
    
    for i in range(bound):
        kmer = seq[i:i+k]
        counts[kmer] += 1
        
    return counts

def print_percentages(seq, k):
    """
    Prints the frequencies of all k-mers of length k as a percentage.
    """
    counts = get_frequencies(seq, k)
    total = sum(counts.values())
    
    # Sort by frequency (descending), then by sequence (ascending)
    sorted_kmers = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    for kmer, count in sorted_kmers:
        print(f"{kmer} {count * 100.0 / total:.3f}")
    print()

def print_count(seq, kmer):
    """
    Prints the absolute count of a specific k-mer.
    """
    # Only calculate counts for the length of the requested k-mer
    counts = get_frequencies(seq, len(kmer))
    print(f"{counts.get(kmer, 0)}\t{kmer}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python knucleotide.py <fasta_file>")
        sys.exit(1)

    # 1. Read the DNA file from the command-line argument
    file_path = sys.argv[1]
    seq = read_sequence(file_path)

    if not seq:
        print("Error: Sequence '>THREE' not found or is empty.")
        sys.exit(1)

    # 2. Output frequencies for lengths 1 and 2
    print_percentages(seq, 1)
    print_percentages(seq, 2)

    # 3. Output specific counts for longer k-mers
    specific_kmers = [
        "GGT", 
        "GGTA", 
        "GGTATT", 
        "GGTATTTTAATT", 
        "GGTATTTTAATTTATAGT"
    ]
    
    for kmer in specific_kmers:
        print_count(seq, kmer)

if __name__ == "__main__":
    main()