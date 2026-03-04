import sys
import mmap
from collections import defaultdict
from functools import lru_cache

def read_fasta():
    """Read FASTA format from stdin and extract sequence THREE"""
    sequences = {}
    current_id = None
    current_seq = []
    
    # Use mmap for efficient large file reading
    if sys.stdin.isatty():
        print("Error: Input must be redirected from a file", file=sys.stderr)
        sys.exit(1)
    
    # Read line by line for simplicity with FASTA format
    for line in sys.stdin.buffer:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith(b'>'):
            if current_id:
                sequences[current_id] = b''.join(current_seq).upper()
            current_id = line[1:].split()[0]
            current_seq = []
        else:
            current_seq.append(line)
    
    if current_id:
        sequences[current_id] = b''.join(current_seq).upper()
    
    return sequences.get(b'THREE', b'')

# DNA to byte mapping (optional optimization)
DNA_TO_BYTE = {b'A': 0, b'C': 1, b'G': 2, b'T': 3}
BYTE_TO_DNA = [b'A', b'C', b'G', b'T']

@lru_cache(maxsize=256)
def byte_to_dna_key(key):
    """Convert integer key back to DNA string for printing"""
    if key < 4:
        return BYTE_TO_DNA[key]
    
    result = bytearray()
    while key > 0:
        result.append(ord(BYTE_TO_DNA[key & 3][0]))
        key >>= 2
    return bytes(reversed(result))

def update_hash_table(seq, k, start, counts):
    """Update hash table for a particular reading frame"""
    end = len(seq) - k + 1
    for i in range(start, end, k):
        # Create key using byte concatenation optimization
        if k == 1:
            key = DNA_TO_BYTE.get(seq[i:i+1], 0)
        else:
            key = 0
            for j in range(k):
                key = (key << 2) | DNA_TO_BYTE.get(seq[i+j:i+j+1], 0)
        
        # Update count in hash table
        counts[key] = counts.get(key, 0) + 1

def count_sequences(seq, k):
    """Count all k-nucleotide sequences for all reading frames"""
    # Start with small dictionary (Python dict grows automatically)
    counts = {}
    
    # Count for all reading frames
    for frame in range(k):
        update_hash_table(seq, k, frame, counts)
    
    return counts

def calculate_and_print(seq, k_values, specific_sequences=None):
    """Calculate and print results for given k values"""
    if specific_sequences is None:
        specific_sequences = []
    
    for k in k_values:
        counts = count_sequences(seq, k)
        
        if k <= 2:
            # For k=1,2: print all with percentages, sorted properly
            total = sum(counts.values())
            items = []
            
            for key, count in counts.items():
                dna_str = byte_to_dna_key(key)
                if len(dna_str) == k:  # Ensure correct length
                    percentage = (count * 100.0) / (total / k)  # Adjust for reading frames
                    items.append((dna_str.decode(), percentage, count))
            
            # Sort by descending frequency, then ascending key
            items.sort(key=lambda x: (-x[1], x[0]))
            
            for dna_str, percentage, count in items:
                print(f"{dna_str} {percentage:.3f}")
            print()
        else:
            # For k>=3: print only specific sequences
            for pattern in specific_sequences:
                if len(pattern) == k:
                    # Calculate key for the pattern
                    key = 0
                    for j in range(k):
                        key = (key << 2) | DNA_TO_BYTE.get(pattern[j:j+1], 0)
                    
                    count = counts.get(key, 0)
                    print(f"{count}\t{pattern.decode()}")
            print()

def main():
    # Read and extract DNA sequence THREE
    seq = read_fasta()
    
    if not seq:
        print("Error: Sequence THREE not found", file=sys.stderr)
        sys.exit(1)
    
    # Validate DNA sequence
    valid_chars = b'ACGT'
    if any(c not in valid_chars for c in seq):
        print("Error: Invalid DNA characters found", file=sys.stderr)
        sys.exit(1)
    
    # Count 1-nucleotide and 2-nucleotide sequences
    print("1-nucleotide sequences:")
    calculate_and_print(seq, [1])
    
    print("2-nucleotide sequences:")
    calculate_and_print(seq, [2])
    
    # Count specific sequences for k=3,4,6,12,18
    specific_patterns = [b'GGT', b'GGTA', b'GGTATT', 
                        b'GGTATTTTAATT', b'GGTATTTTAATTTATAGT']
    
    for pattern in specific_patterns:
        k = len(pattern)
        print(f"{k}-nucleotide sequences:")
        calculate_and_print(seq, [k], [pattern])

if __name__ == "__main__":
    main()