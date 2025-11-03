import sys
from collections import defaultdict

def read_fasta_three(input_stream):
    """
    Reads a FASTA file from the provided input stream and extracts the DNA
    sequence labeled '>THREE'. It handles multi-line FASTA entries and
    converts the sequence to uppercase.
    """
    sequence_lines = []
    found_sequence = False
    for line in input_stream:
        if line.startswith('>THREE'):
            found_sequence = True
        elif found_sequence and line.startswith('>'):
            break  # Stop at the beginning of the next sequence
        elif found_sequence:
            sequence_lines.append(line.strip())
    return "".join(sequence_lines).upper()

def count_knucleotides(sequence, k):
    """
    Creates a hash table (dictionary) to count the occurrences of
    k-nucleotides of a specific length 'k' within a given DNA sequence.
    """
    counts = defaultdict(int)
    for i in range(len(sequence) - k + 1):
        k_nucleotide = sequence[i:i+k]
        counts[k_nucleotide] += 1
    return counts

def calculate_and_print_frequencies(sequence, k):
    """
    Calculates and prints the frequencies of k-nucleotides. The results
    are sorted by frequency in descending order, and then by the
    k-nucleotide key in ascending order for ties.
    """
    total_count = len(sequence) - k + 1
    counts = count_knucleotides(sequence, k)
    
    # Sort by frequency (descending) and then by key (ascending)
    sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    
    for key, count in sorted_counts:
        percentage = (count * 100.0) / total_count if total_count > 0 else 0
        print(f"{key} {percentage:.3f}")
    print()

def print_specific_counts(sequence, specific_sequences):
    """
    Finds and prints the counts of a predefined list of specific
    nucleotide sequences.
    """
    k_to_sequence = {len(s): s for s in specific_sequences}
    for k, seq_to_find in k_to_sequence.items():
        counts = count_knucleotides(sequence, k)
        count = counts.get(seq_to_find, 0)
        print(f"{count}\t{seq_to_find}")

def main():
    """
    Main function to execute the k-nucleotide simulation.
    """
    # Read and extract the DNA sequence THREE from standard input
    dna_sequence = read_fasta_three(sys.stdin)

    # Count and print frequencies for 1-nucleotide and 2-nucleotide sequences
    calculate_and_print_frequencies(dna_sequence, 1)
    calculate_and_print_frequencies(dna_sequence, 2)

    # Count and print the occurrences of specific nucleotide sequences
    specific_sequences_to_find = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    print_specific_counts(dna_sequence, specific_sequences_to_find)

if __name__ == "__main__":
    main()