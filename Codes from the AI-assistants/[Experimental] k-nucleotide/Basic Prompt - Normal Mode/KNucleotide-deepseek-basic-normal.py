import sys
from collections import defaultdict

def main():
    # Read input data
    data = sys.stdin.read()
    
    # Find the sequence starting with >THREE ...
    start = data.find(">THREE")
    if start == -1:
        return
    seq_start = data.find("\n", start) + 1
    seq_end = data.find("\n>", seq_start)
    sequence = data[seq_start:seq_end if seq_end != -1 else None]
    sequence = sequence.replace("\n", "").upper()
    
    # Define the lengths we're interested in
    lengths = [1, 2, 3, 4, 6, 12, 18]
    
    # Process each length
    for n in lengths:
        counts = defaultdict(int)
        total = 0
        
        # Count all n-length subsequences
        for i in range(len(sequence) - n + 1):
            subsequence = sequence[i:i+n]
            counts[subsequence] += 1
            total += 1
        
        # Special sequences to report
        special_sequences = []
        if n == 1:
            special_sequences = ['G', 'T', 'A', 'C']
        elif n == 2:
            special_sequences = ['GG', 'GT', 'AT', 'TT', 'GA', 'CT', 'AG', 'AA', 'AC', 'TG', 'TC', 'CA', 'CG', 'TA', 'GC', 'CC']
        
        # Report results
        if special_sequences:
            for seq in special_sequences:
                print(f"{seq} {counts.get(seq, 0)}")
        else:
            # For longer sequences, find the most frequent
            sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
            top = sorted_counts[:7]
            for seq, count in top:
                print(f"{seq} {count}")
        
        print()

if __name__ == "__main__":
    main()