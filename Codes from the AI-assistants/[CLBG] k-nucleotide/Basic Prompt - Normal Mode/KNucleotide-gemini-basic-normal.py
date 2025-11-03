import sys
from collections import Counter

def main():
    """
    Main function to read FASTA input, extract DNA sequence THREE,
    count k-nucleotides, and print the results as specified.
    """
    # 1. Read Input and Extract DNA Sequence THREE
    # We'll collect all lines belonging to the target sequence.
    fasta_sequence_lines = []
    in_target_sequence = False

    # Iterate through each line from standard input
    for line in sys.stdin:
        line = line.strip() # Remove leading/trailing whitespace, including newlines
        if not line: # Skip any completely empty lines
            continue

        if line.startswith('>'):
            # If a header line is encountered
            if line == '>THREE':
                # Start collecting lines if it's the target sequence header
                in_target_sequence = True
            else:
                # Stop collecting if another sequence header is found
                in_target_sequence = False
            continue # Skip the header line itself

        # If we are currently in the target sequence section, append the line
        if in_target_sequence:
            fasta_sequence_lines.append(line)

    # Join all collected lines to form the complete DNA sequence
    # Convert to uppercase to ensure consistent matching (e.g., 'a' vs 'A')
    dna_sequence = "".join(fasta_sequence_lines).upper()

    # If no DNA sequence THREE was found or it was empty, exit.
    if not dna_sequence:
        print("Error: No DNA sequence THREE found or the sequence is empty.")
        return

    # 2. K-nucleotide Counting Function
    def count_k_mers(sequence, k):
        """
        Counts occurrences of all k-mers (subsequences of length k) in a given DNA sequence.
        Utilizes collections.Counter for efficient accumulation of counts.

        Args:
            sequence (str): The DNA sequence to analyze.
            k (int): The length of the k-mers to count.

        Returns:
            collections.Counter: A Counter object where keys are k-mers and values are their counts.
        """
        counts = Counter()
        # Iterate through the sequence to extract all possible k-mers
        # The loop runs up to len(sequence) - k + 1 to ensure the last k-mer is included.
        for i in range(len(sequence) - k + 1):
            k_mer = sequence[i : i + k]
            counts[k_mer] += 1 # Increment count for the k-mer
        return counts

    # Helper function to print k-mer frequencies
    def print_frequencies(counts, total):
        """
        Prints k-mer frequencies, formatted as 'KMER PERCENTAGE%',
        sorted by descending frequency and then ascending k-mer key.

        Args:
            counts (collections.Counter): A Counter object of k-mer counts.
            total (int): The total number of k-mers counted (sum of all values in counts).
        """
        if total == 0:
            return # Avoid division by zero if no k-mers were found

        # Sort the items:
        # Primary sort key: negative count (for descending order)
        # Secondary sort key: k-mer string (for ascending alphabetical order)
        sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

        # Print each k-mer and its calculated percentage
        for kmer, count in sorted_items:
            percentage = (count * 100.0) / total
            print(f"{kmer} {percentage:.3f}%") # Format percentage to 3 decimal places

    # 3. Main Logic: Counting and Reporting

    # Count and report 1-nucleotide sequences (1-mers)
    counts_1_mer = count_k_mers(dna_sequence, 1)
    total_1_mer = sum(counts_1_mer.values())
    print_frequencies(counts_1_mer, total_1_mer)
    print() # Add a newline for separation as per common output formats

    # Count and report 2-nucleotide sequences (2-mers)
    counts_2_mer = count_k_mers(dna_sequence, 2)
    total_2_mer = sum(counts_2_mer.values())
    print_frequencies(counts_2_mer, total_2_mer)
    print() # Add a newline for separation

    # Count and report specific k-nucleotide sequences
    specific_kmers_to_find = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT"
    ]

    # For specific k-mers, Python's string.count() method is highly optimized
    # and directly provides the count without needing to build a full Counter object
    # for potentially large k values.
    for kmer in specific_kmers_to_find:
        count = dna_sequence.count(kmer)
        # Print the count followed by a tab and the k-mer itself
        print(f"{count}\t{kmer}")

# Entry point for the script
if __name__ == "__main__":
    main()
