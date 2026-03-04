import collections # For Counter, which is a specialized dict
import sys # For stdin/stdout

def solve_k_nucleotide():
    # Phase 1: Preprocessing and Data Extraction
    # Read the entire input, typically from stdin
    lines = []
    # In a real scenario, you'd read line by line or use sys.stdin.read()
    # For demonstration, let's assume content is already read
    # Example input simulation:
    # lines.append(">ONE Homo sapiens\n")
    # lines.append("ATGGCGTA\n")
    # lines.append(">TWO\n")
    # lines.append("CGTA\n")
    # lines.append(">THREE Homo sapiens K\n")
    # lines.append("AGCAGTTAATAGATGCCCTGTCTAGACATTATCGTTTCGATTCCCTTG\n")
    # lines.append("TGCGCTTCAAGTTCGACGATAGAATATTCCGCCGCCTCATCCATACCAT\n")
    # lines.append("AGCGGCGACTGCATCGTTTAAAAGCAGTCAAAAGGAGGAATATTTCTCC\n")
    # lines.append("TGCGTAGGAGCTTAGCGGCGCTTTGCTAATTCCCGCCGCTACTTCGACG\n")
    # lines.append("ATTAGCAGTGCGTTCGACGAACGGTGGGTTACGCCATAGGATACAGGT\n")

    # For the actual problem, you'd filter for the "THIRD" sequence
    # This part depends heavily on the specific input format
    # Let's assume 'filtered_sequence' is the target DNA string after reading
    # and filtering (e.g., 'AGCAGTTAATAGATGCCCTGTCTAGACATTATCGTTTCGATTCCCTTG...' )

    # Simplified sequence for demonstration
    filtered_sequence = "AGCAGTTAATAGATGCCCTGTCTAGACATTATCGTTTCGATTCCCTTG" \
                        "TGCGCTTCAAGTTCGACGATAGAATATTCCGCCGCCTCATCCATACCAT" \
                        "AGCGGCGACTGCATCGTTTAAAAGCAGTCAAAAGGAGGAATATTTCTCC" \
                        "TGCGTAGGAGCTTAGCGGCGCTTTGCTAATTCCCGCCGCTACTTCGACG" \
                        "ATTAGCAGTGCGTTCGACGAACGGTGGGTTACGCCATAGGATACAGGT"


    # Phase 2: Counting K-mers
    def count_k_mers(sequence, k):
        # Using collections.Counter is like a highly optimized dict for counting
        # This is a native library feature.
        counts = collections.Counter()
        for i in range(len(sequence) - k + 1):
            k_mer = sequence[i : i + k] # Native string slicing
            counts[k_mer] += 1
        return counts

    # Phase 3: Reporting Frequencies
    def report_frequencies(k_mer_counts_map):
        total_count = sum(k_mer_counts_map.values())
        items = []
        for k_mer, count in k_mer_counts_map.items():
            percentage = (count * 100.0) / total_count
            items.append((k_mer, percentage))

        # Sort: primary by percentage (desc), secondary by k_mer (asc)
        # Using native list sort with a lambda for custom comparison
        items.sort(key=lambda x: (-x[1], x[0]))

        for k_mer, percentage in items:
            # Native string formatting
            print(f"{k_mer} {percentage:.2f}")

    # Process and Report
    print("1-mer frequencies:")
    report_frequencies(count_k_mers(filtered_sequence, 1))

    print("\n2-mer frequencies:")
    report_frequencies(count_k_mers(filtered_sequence, 2))

    # Phase 4: Reporting Specific K-mer Counts
    def report_specific_counts(sequence, specific_k_mers):
        for target_k_mer in specific_k_mers:
            k = len(target_k_mer)
            counts = count_k_mers(sequence, k)
            count = counts.get(target_k_mer, 0) # Native dict.get with default
            print(f"{count}\t{target_k_mer}")

    print("\nSpecific k-mer counts:")
    specific_kmers_to_find = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATATTTATATATATTTT"
    ]
    report_specific_counts(filtered_sequence, specific_kmers_to_find)

# Call the main function
solve_k_nucleotide()