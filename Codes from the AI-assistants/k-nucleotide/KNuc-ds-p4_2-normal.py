import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from functools import lru_cache

def extract_sequence_mmap():
    """Memory-mapped FASTA reading for large files"""
    # Read all data efficiently
    data = sys.stdin.buffer.read()
    
    # Convert to memoryview for zero-copy slicing
    mv = memoryview(data)
    
    # Find sequence THREE
    three_pos = data.find(b'>THREE')
    if three_pos == -1:
        three_pos = data.find(b'>Three')
    
    if three_pos == -1:
        return bytearray()
    
    # Find the end of the THREE sequence
    next_header = data.find(b'>', three_pos + 1)
    if next_header == -1:
        sequence_data = data[three_pos:]
    else:
        sequence_data = data[three_pos:next_header]
    
    # Extract DNA sequence
    lines = sequence_data.split(b'\n')
    sequence = bytearray()
    
    for line in lines[1:]:  # Skip header line
        if line:
            clean_line = line.strip().upper()
            for char in clean_line:
                if char in b"ACGT":
                    sequence.append(char)
    
    return sequence

def count_kmers_chunk(seq_chunk, k, start_idx, chunk_size, overlap):
    """Count k-mers in a chunk of sequence with overlap for boundary handling"""
    counts = defaultdict(int)
    chunk_with_overlap = seq_chunk
    
    for i in range(len(chunk_with_overlap) - k + 1):
        key = chunk_with_overlap[i:i+k]
        # Use bytes as key directly (more efficient than bytearray)
        counts[key] += 1
    
    return counts

def parallel_count(sequence, k, num_processes=None):
    """Parallel k-mer counting using multiprocessing"""
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    seq_len = len(sequence)
    chunk_size = seq_len // num_processes
    overlap = k - 1
    
    # Convert to bytes for slicing efficiency
    seq_bytes = bytes(sequence)
    
    chunks = []
    for i in range(num_processes):
        start = i * chunk_size
        end = start + chunk_size + overlap if i < num_processes - 1 else seq_len
        chunks.append((seq_bytes[start:end], k, start, chunk_size, overlap))
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = list(executor.map(
            lambda args: count_kmers_chunk(*args), chunks
        ))
    
    # Merge results
    total_counts = defaultdict(int)
    for result in results:
        for key, count in result.items():
            total_counts[key] += count
    
    return total_counts

def main_optimized():
    """Optimized main function for large inputs"""
    # Extract sequence
    sequence = extract_sequence_mmap()
    seq_len = len(sequence)
    
    print(f"Sequence length: {seq_len}")
    
    # Count 1-mers and 2-mers (fast, don't need parallel)
    counts_1 = defaultdict(int)
    counts_2 = defaultdict(int)
    
    # Use efficient iteration
    seq_bytes = bytes(sequence)
    
    # Count 1-mers
    for i in range(seq_len):
        counts_1[seq_bytes[i:i+1]] += 1
    
    # Count 2-mers
    for i in range(seq_len - 1):
        counts_2[seq_bytes[i:i+2]] += 1
    
    # Sort and print 1-mer results
    freq_1 = [(k.decode('ascii'), v, v/seq_len*100) 
              for k, v in counts_1.items()]
    freq_1.sort(key=lambda x: (-x[1], x[0]))
    
    for k, count, percent in freq_1:
        print(f"{k} {percent:.3f}")
    print()
    
    # Sort and print 2-mer results
    freq_2 = [(k.decode('ascii'), v, v/(seq_len-1)*100) 
              for k, v in counts_2.items()]
    freq_2.sort(key=lambda x: (-x[1], x[0]))
    
    for k, count, percent in freq_2:
        print(f"{k} {percent:.3f}")
    print()
    
    # Count specific sequences
    targets = [
        (3, b'GGT'),
        (4, b'GGTA'),
        (6, b'GGTATT'),
        (12, b'GGTATTTTAATT'),
        (18, b'GGTATTTTAATTTATAGT')
    ]
    
    for k, target in targets:
        if k <= 6:  # Shorter sequences, count directly
            counts = defaultdict(int)
            for i in range(seq_len - k + 1):
                key = seq_bytes[i:i+k]
                if len(key) == k:  # Ensure full length
                    counts[key] += 1
            count = counts.get(target, 0)
        else:  # Longer sequences, use sliding window
            count = 0
            target_str = target.decode('ascii')
            # Convert to string for find() which is efficient for few searches
            seq_str = sequence.decode('ascii')
            for i in range(len(seq_str) - k + 1):
                if seq_str[i:i+k] == target_str:
                    count += 1
        
        print(f"{count}\t{target.decode('ascii')}")

if __name__ == "__main__":
    # Use optimized version for performance
    main_optimized()