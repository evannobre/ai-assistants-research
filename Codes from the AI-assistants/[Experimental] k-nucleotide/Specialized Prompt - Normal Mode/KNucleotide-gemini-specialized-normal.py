import sys
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import itertools # For efficient iteration if needed, though direct slicing is fine

# --- Helper Functions ---

def read_fasta_sequence():
    """
    Reads the DNA sequence from stdin, skipping headers and converting to uppercase.
    """
    sequence_lines = []
    for line in sys.stdin:
        if line.startswith('>'):
            # Clear previous lines if we encounter a new header (assuming only one sequence matters)
            sequence_lines = []
            continue
        # Only process lines that are not empty and don't start with '>'
        if line.strip() and not line.startswith('>'):
            sequence_lines.append(line.strip().upper())
    return "".join(sequence_lines)

def count_k_mers(sequence, k):
    """
    Counts k-mer occurrences in the given sequence.
    Uses collections.defaultdict for efficient counting.
    """
    counts = defaultdict(int)
    n = len(sequence)
    if n < k:
        return counts

    for i in range(n - k + 1):
        k_mer = sequence[i : i + k]
        counts[k_mer] += 1
    return counts

def calculate_frequencies_and_format(counts, total_k_mers):
    """
    Calculates frequencies, sorts, and formats the output for frequency results.
    """
    items = sorted(counts.items(), key=lambda item: (-item[1], item[0])) # Sort by count (desc), then k-mer (asc)
    result = []
    for k_mer, count in items:
        percentage = (count / total_k_mers) * 100
        result.append(f"{k_mer} {percentage:.3f}")
    return "\n".join(result)

def find_specific_k_mer_and_format(counts, specific_k_mer):
    """
    Finds the count of a specific k-mer and formats the output.
    """
    count = counts.get(specific_k_mer, 0)
    return f"{count}\t{specific_k_mer}"

# --- Main Logic ---

if __name__ == "__main__":
    # 1. Read and prepare sequence
    sequence = read_fasta_sequence()
    # Filter non-ACGT characters - critical for robust k-mer counting
    # This step might be slow for extremely long sequences if done naively.
    # Consider using a more performant way like str.translate or regex for very large files.
    # For typical DNA sequence sizes, a simple comprehension is fine.
    sequence = "".join(char for char in sequence if char in "ACGT")
    
    # Define tasks for parallel processing
    k_frequency_lengths = [1, 2]
    specific_k_mers_to_find = [
        "GGTATTTTAATTTATAGT",
        "GGTA"
    ]
    
    all_k_lengths_needed = set(k_frequency_lengths)
    for specific_k_mer in specific_k_mers_to_find:
        all_k_lengths_needed.add(len(specific_k_mer))
    
    # Prepare arguments for multiprocessing map
    # Each item in `tasks` will be (sequence, k)
    tasks = [(sequence, k) for k in sorted(list(all_k_lengths_needed))]
    
    # 2. Parallel K-mer Counting
    # Use cpu_count() to maximize utilization of available cores
    num_processes = max(1, cpu_count() - 1) # Leave one core free for OS, or adjust based on system load
    if sys.platform == "win32": # Multiprocessing behavior differs on Windows
        num_processes = 1 # Avoid issues with large data on Windows if not careful with pickling
        
    k_mer_counts_map = {} # Store results of parallel processing
    
    with Pool(processes=num_processes) as pool:
        # pool.starmap applies the function to each tuple in tasks
        results = pool.starmap(count_k_mers, tasks)
        for i, k in enumerate(sorted(list(all_k_lengths_needed))):
            k_mer_counts_map[k] = results[i]

    # 3. Output Generation
    
    # Frequencies for 1-mers and 2-mers
    for k in k_frequency_lengths:
        counts = k_mer_counts_map[k]
        total_k_mers = len(sequence) - k + 1
        if total_k_mers > 0: # Avoid division by zero for very short sequences
            print(calculate_frequencies_and_format(counts, total_k_mers))
            print() # Blank line between sections

    # Counts for specific k-mers
    for specific_k_mer in specific_k_mers_to_find:
        k = len(specific_k_mer)
        counts = k_mer_counts_map[k]
        print(find_specific_k_mer_and_format(counts, specific_k_mer))