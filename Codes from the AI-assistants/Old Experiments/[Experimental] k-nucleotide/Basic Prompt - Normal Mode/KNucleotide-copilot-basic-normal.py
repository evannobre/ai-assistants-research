from collections import Counter

def k_nucleotide_frequencies(dna_sequence: str, k: int) -> dict:
    if k <= 0 or k > len(dna_sequence):
        return {}

    # Extract all k-length substrings
    k_mers = (dna_sequence[i:i + k] for i in range(len(dna_sequence) - k + 1))
    
    # Count using native Counter
    frequencies = Counter(k_mers)
    
    # Optionally sort by frequency or alphabetically
    return dict(sorted(frequencies.items(), key=lambda x: (-x[1], x[0])))

dna = "AGCTAGCTAGCTA"
k = 3

result = k_nucleotide_frequencies(dna, k)
for kmer, count in result.items():
    print(f"{kmer}: {count}")
