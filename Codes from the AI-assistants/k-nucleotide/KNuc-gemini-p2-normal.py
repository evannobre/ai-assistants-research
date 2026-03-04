import sys
from multiprocessing import Pool
from collections import Counter

def get_frequencies(sequence, length):
    """Generates a frequency map for substrings of a specific length."""
    frequencies = Counter()
    # Sliding window across the sequence
    for i in range(len(sequence) - length + 1):
        frequencies[sequence[i:i + length]] += 1
    return frequencies

def format_stat(frequencies, length):
    """Sorts and formats frequencies for output."""
    total = sum(frequencies.values())
    # Sort by frequency descending, then alphabetically
    sorted_freqs = sorted(frequencies.items(), key=lambda x: (-x[1], x[0]))
    
    output = []
    for seq, count in sorted_freqs:
        percentage = (count * 100) / total
        output.append(f"{seq} {percentage:.3f}")
    return "\n".join(output)

def find_sequence(frequencies, target):
    """Finds the count of a specific sequence."""
    return f"{frequencies.get(target, 0)}\t{target}"

def main():
    # Step 1: Efficiently extract sequence >THREE
    # We read from stdin to allow command-line piping
    lines = sys.stdin
    for line in lines:
        if line.startswith(">THREE"):
            break
            
    sequence_list = []
    for line in lines:
        if line.startswith(">"):
            break
        sequence_list.append(line.strip().upper())
    
    full_sequence = "".join(sequence_list)

    # Step 2: Parallel processing using native Pool
    # 8GB RAM is plenty for Python's overhead on standard benchmarks
    with Pool() as pool:
        # Calculate for single and double nucleotides
        results_1 = pool.apply_async(get_frequencies, (full_sequence, 1))
        results_2 = pool.apply_async(get_frequencies, (full_sequence, 2))
        
        # Specific targets defined by the benchmark
        targets = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
        target_results = [pool.apply_async(get_frequencies, (full_sequence, len(t))) 
                         for t in targets]

        # Output formatting
        print(format_stat(results_1.get(), 1))
        print(f"\n{format_stat(results_2.get(), 2)}\n")
        
        for i, t in enumerate(targets):
            print(find_sequence(target_results[i].get(), t))

if __name__ == "__main__":
    main()