import sys
import collections
import re
from collections import defaultdict
from itertools import islice

def read_fasta():
    """Read FASTA format from stdin, extract DNA sequence THREE."""
    data = sys.stdin.read()
    # Find THRExxx pattern
    match = re.search(r'>THREE\s*\n([ACGT\n]+)', data, re.IGNORECASE)
    if not match:
        return ""
    
    sequence = match.group(1).upper()
    # Remove whitespace and newlines
    sequence = re.sub(r'\s+', '', sequence)
    return sequence

def update_counts(sequence, k, counts=None):
    """
    Count k-nucleotide sequences for all reading frames.
    Returns a dictionary with counts.
    """
    if counts is None:
        counts = defaultdict(int)
    
    n = len(sequence)
    for i in range(n - k + 1):
        subseq = sequence[i:i + k]
        counts[subseq] += 1
    
    return counts

def letter_to_code(c):
    """Map DNA letters to codes: A->0, C->1, G->2, T->3"""
    if c == 'A': return 0
    if c == 'C': return 1
    if c == 'G': return 2
    if c == 'T': return 3
    return -1

def optimized_update_counts(sequence, k, counts=None):
    """
    Optimized version using integer encoding.
    Concatenates 2-bit codes for each nucleotide.
    """
    if counts is None:
        counts = defaultdict(int)
    
    n = len(sequence)
    if n < k:
        return counts
    
    # Precompute codes for each position
    codes = [letter_to_code(c) for c in sequence]
    
    # Build initial hash for first k-1 nucleotides
    hash_val = 0
    for i in range(k - 1):
        hash_val = (hash_val << 2) | codes[i]
    
    # Slide window and update counts
    for i in range(k - 1, n):
        hash_val = ((hash_val << 2) & ((1 << (2 * k)) - 1)) | codes[i]
        # We'll still store as string for consistency with output requirements
        subseq = sequence[i - k + 1:i + 1]
        counts[subseq] += 1
    
    return counts

def sort_and_write(counts, k):
    """Sort by descending frequency, then ascending key, and print results."""
    total = sum(counts.values())
    
    # Create list of (key, count) pairs
    items = list(counts.items())
    
    # Sort by descending count, then ascending key
    items.sort(key=lambda x: (-x[1], x[0]))
    
    # Print results
    for key, count in items:
        frequency = (count * 100.0) / total
        print(f"{key} {frequency:.3f}")

def main():
    # Read and prepare sequence
    sequence = read_fasta()
    if not sequence:
        print("No THRExxx sequence found")
        return
    
    # 1. Count 1-nucleotide sequences
    print("\n1-nucleotide sequences:")
    counts_1 = update_counts(sequence, 1)
    sort_and_write(counts_1, 1)
    
    # 2. Count 2-nucleotide sequences
    print("\n2-nucleotide sequences:")
    counts_2 = update_counts(sequence, 2)
    sort_and_write(counts_2, 2)
    
    # 3. Count specific sequences (3, 4, 6, 12, 18 nucleotides)
    # Use optimized version for performance with larger k
    all_counts = defaultdict(int)
    
    # Count all 3, 4, 6, 12, 18-nucleotide sequences
    for k in [3, 4, 6, 12, 18]:
        optimized_update_counts(sequence, k, all_counts)
    
    # Print specific sequences
    specific_sequences = [
        "GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"
    ]
    
    print("\nSpecific sequences:")
    for seq in specific_sequences:
        count = all_counts.get(seq, 0)
        print(f"{count}\t{seq}")

def benchmark_version():
    """
    Alternative version optimized for the benchmark with larger inputs.
    This uses integer hashing for better performance.
    """
    import sys
    import re
    from collections import defaultdict
    
    # Read input
    data = sys.stdin.read()
    
    # Extract THRExxx sequence
    match = re.search(r'>THREE\s*\n([ACGT\n]+)', data, re.IGNORECASE)
    if not match:
        return
    
    sequence = match.group(1).upper()
    sequence = re.sub(r'\s+', '', sequence)
    
    # Convert to bytes for faster processing
    # A=0, C=1, G=2, T=3
    trans = str.maketrans('ACGT', '\x00\x01\x02\x03')
    seq_bytes = sequence.translate(trans)
    
    def count_k(k, use_bytes=True):
        """Count k-mers using byte representation for speed."""
        counts = defaultdict(int)
        n = len(sequence)
        
        if use_bytes and k <= 18:  # Practical limit for integer hashing
            # Integer hashing approach
            mask = (1 << (2 * k)) - 1
            hash_val = 0
            
            # Build initial hash
            for i in range(min(k - 1, n)):
                hash_val = (hash_val << 2) | seq_bytes[i]
            
            # Slide window
            for i in range(k - 1, n):
                hash_val = ((hash_val << 2) & mask) | seq_bytes[i]
                
                # Convert back to string for storage
                # This is slower but maintains compatibility
                start = i - k + 1
                subseq = sequence[start:start + k]
                counts[subseq] += 1
        else:
            # Fallback for very large k
            for i in range(n - k + 1):
                subseq = sequence[i:i + k]
                counts[subseq] += 1
        
        return counts
    
    # 1. 1-nucleotide counts
    counts_1 = count_k(1)
    total = len(sequence)
    sorted_1 = sorted(counts_1.items(), key=lambda x: (-x[1], x[0]))
    for key, count in sorted_1:
        print(f"{key} {(count * 100.0 / total):.3f}")
    
    print()
    
    # 2. 2-nucleotide counts
    counts_2 = count_k(2)
    total_2 = len(sequence) - 1
    sorted_2 = sorted(counts_2.items(), key=lambda x: (-x[1], x[0]))
    for key, count in sorted_2:
        print(f"{key} {(count * 100.0 / total_2):.3f}")
    
    # 3. Specific sequences
    print()
    
    # Count all needed k-mers at once for efficiency
    all_counts = defaultdict(int)
    for k in [3, 4, 6, 12, 18]:
        counts_k = count_k(k)
        for key, value in counts_k.items():
            all_counts[key] = value
    
    specific = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    for seq in specific:
        print(f"{all_counts.get(seq, 0)}\t{seq}")

if __name__ == "__main__":
    # Use benchmark_version for better performance with large inputs
    benchmark_version()