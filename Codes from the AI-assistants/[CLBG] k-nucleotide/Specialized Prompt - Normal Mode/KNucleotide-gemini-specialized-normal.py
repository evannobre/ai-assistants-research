import sys
from collections import defaultdict
import time # For potential performance insights (though not required for output)

# --- Global Mappings for DNA to Integer Conversion ---
# Maps DNA characters to 2-bit integer representations.
# A: 00 (0), C: 01 (1), G: 10 (2), T: 11 (3)
DNA_TO_INT = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

# Maps integer representations back to DNA characters (for reconstructing k-mer strings).
INT_TO_DNA = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}

def dna_to_int_key(kmer_str):
    """
    Converts a k-mer string (e.g., "GGT") into a single integer key.
    Each nucleotide is represented by 2 bits, concatenated to form the integer.
    Example: "AG" -> A (00) G (10) -> 0010 (binary) -> 2 (decimal)
    This is an acceptable optimization for efficient hashing and memory usage.
    """
    key = 0
    for char in kmer_str:
        # Shift the existing key 2 bits to the left to make space for the new nucleotide,
        # then OR with the integer representation of the current nucleotide.
        key = (key << 2) | DNA_TO_INT[char]
    return key

def int_key_to_dna(key_int, k):
    """
    Converts an integer key back into its original k-mer DNA string.
    This is used for displaying the results in the required string format.
    """
    dna_chars = []
    # Iterate 'k' times, extracting 2 bits at a time from the right (LSB).
    for _ in range(k):
        # Extract the last 2 bits (0b11 is binary for 3)
        nucleotide_int = key_int & 0b11
        dna_chars.append(INT_TO_DNA[nucleotide_int])
        # Shift the key 2 bits to the right to process the next nucleotide.
        key_int >>= 2
    # The nucleotides were appended in reverse order, so reverse the list before joining.
    return "".join(reversed(dna_chars))

def count_sequences(sequence, k):
    """
    Counts all k-nucleotide sequences (k-mers) in the given DNA sequence.
    It uses a defaultdict (a type of hash table) to store the counts,
    with integer representations of k-mers as keys for efficiency.

    Args:
        sequence (str): The DNA sequence to analyze.
        k (int): The length of the k-nucleotide sequences to count.

    Returns:
        defaultdict: A dictionary where keys are integer representations of k-mers
                     and values are their counts.
    """
    counts = defaultdict(int)
    sequence_length = len(sequence)

    # Pre-calculate the bit mask for extracting the last 'k' nucleotides
    # from the 'current_key'. This mask will have 'k * 2' set bits.
    # Example: if k=2, k*2=4. (1 << 4) - 1 = 16 - 1 = 15 (binary 1111).
    # This ensures that 'current_key & mask' only keeps the bits relevant to the
    # current k-mer, discarding older nucleotides that are no longer part of it.
    mask = (1 << (k * 2)) - 1

    current_key_accumulator = 0 # Accumulates the integer representation of the sliding window

    # Iterate through the sequence to generate and count k-mers
    for i in range(sequence_length):
        char = sequence[i]
        
        # Shift the accumulator 2 bits to the left and add the new nucleotide's integer value.
        current_key_accumulator = (current_key_accumulator << 2) | DNA_TO_INT[char]
        
        # Once we have accumulated at least 'k' nucleotides, we can start counting k-mers.
        if i >= k - 1:
            # Apply the mask to get the integer key for the current k-mer.
            # This effectively "slides" the window by discarding the oldest nucleotide's bits.
            kmer_int_key = current_key_accumulator & mask
            counts[kmer_int_key] += 1
            
    return counts

def main():
    """
    Main function to execute the k-nucleotide simulation.
    It reads input from stdin, processes the DNA sequence,
    counts k-mers, and prints the results as specified.
    """
    # 1. Read all of a redirected FASTA format file from stdin;
    # 2. Extract DNA sequence THREE;
    
    # Use a list to efficiently build the DNA sequence string, then join at the end.
    dna_sequence_parts = []
    in_target_sequence = False # Flag to indicate if we are currently reading DNA sequence THREE

    # Read line by line from standard input
    for line in sys.stdin:
        line = line.strip() # Remove leading/trailing whitespace, including newlines
        
        # Check if the line is a FASTA header
        if line.startswith('>'):
            if line == '>THREE':
                in_target_sequence = True # Start capturing lines for DNA sequence THREE
            else:
                in_target_sequence = False # Stop capturing if another header is found
        elif in_target_sequence:
            # If we are in the target sequence block, append the line.
            # Remove any spaces or other non-DNA characters and convert to uppercase
            # for consistent processing.
            dna_sequence_parts.append(line.replace(' ', '').upper())
    
    # Join all parts to form the complete DNA sequence string.
    dna_sequence = "".join(dna_sequence_parts)

    # --- Process 1-nucleotide and 2-nucleotide sequences ---
    # Count all 1-nucleotide sequences
    counts_1_mer = count_sequences(dna_sequence, 1)
    total_1_mer = sum(counts_1_mer.values()) # Total number of 1-mers (length of sequence)

    # Prepare data for sorting: (percentage, k-mer string)
    sorted_1_mer_results = []
    for k_int, count in counts_1_mer.items():
        k_str = int_key_to_dna(k_int, 1)
        percentage = (count * 100.0) / total_1_mer
        sorted_1_mer_results.append((percentage, k_str))
    
    # Sort by descending percentage, then ascending k-nucleotide key
    sorted_1_mer_results.sort(key=lambda x: (-x[0], x[1]))
    
    # Print 1-nucleotide results
    for percentage, k_str in sorted_1_mer_results:
        print(f"{k_str} {percentage:.3f}") # Format percentage to 3 decimal places

    print() # Print a blank line separator as per benchmark output format

    # Count all 2-nucleotide sequences
    counts_2_mer = count_sequences(dna_sequence, 2)
    total_2_mer = sum(counts_2_mer.values()) # Total number of 2-mers (length of sequence - 1)

    # Prepare data for sorting: (percentage, k-mer string)
    sorted_2_mer_results = []
    for k_int, count in counts_2_mer.items():
        k_str = int_key_to_dna(k_int, 2)
        percentage = (count * 100.0) / total_2_mer
        sorted_2_mer_results.append((percentage, k_str))
    
    # Sort by descending percentage, then ascending k-nucleotide key
    sorted_2_mer_results.sort(key=lambda x: (-x[0], x[1]))
    
    # Print 2-nucleotide results
    for percentage, k_str in sorted_2_mer_results:
        print(f"{k_str} {percentage:.3f}") # Format percentage to 3 decimal places

    print() # Print a blank line separator

    # --- Process specific k-nucleotide sequences ---
    # Define the specific sequences to count
    specific_sequences_to_find = [
        "GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"
    ]

    # Group specific sequences by their length (k) to avoid re-counting for the same k
    sequences_by_k_length = defaultdict(list)
    for seq_str in specific_sequences_to_find:
        sequences_by_k_length[len(seq_str)].append(seq_str)

    # Process each k-group (3, 4, 6, 12, 18)
    # Sort keys to ensure consistent output order if not already sorted.
    for k_val in sorted(sequences_by_k_length.keys()):
        # Count all k-mers for the current k_val.
        # This adheres to the "count all" requirement before extracting specific ones.
        current_k_mer_counts = count_sequences(dna_sequence, k_val)
        
        # For each specific sequence of this length, retrieve its count
        for seq_str in sequences_by_k_length[k_val]:
            # Convert the specific sequence string to its integer key
            seq_int_key = dna_to_int_key(seq_str)
            # Get the count from the hash table; default to 0 if not found
            count = current_k_mer_counts.get(seq_int_key, 0)
            # Print the count and the k-mer string, separated by a tab
            print(f"{count}\t{seq_str}")

# Entry point for the script execution
if __name__ == '__main__':
    main()
