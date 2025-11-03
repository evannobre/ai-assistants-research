import sys

def read_fasta(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    seq = []
    for line in lines:
        if line.startswith('>'):
            continue
        seq.append(line.strip())
    return ''.join(seq).upper()

def count_kmers(seq, k):
    counts = {}
    n = len(seq)
    for i in range(0, n - k + 1):
        kmer = seq[i:i+k]
        counts[kmer] = counts.get(kmer, 0) + 1
    return counts

def count_specific(seq, pattern):
    k = len(pattern)
    n = len(seq)
    count = 0
    for i in range(0, n - k + 1):
        if seq[i:i+k] == pattern:
            count += 1
    return count

def main():
    if len(sys.argv) != 2:
        print("Usage: knucleotide <input-file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    seq = read_fasta(filename)
    total_length = len(seq)
    
    # Process k=1
    k1_counts = count_kmers(seq, 1)
    total_kmers_1 = total_length
    items1 = sorted(k1_counts.items(), key=lambda x: (-x[1], x[0]))
    for kmer, count in items1:
        freq = (count / total_kmers_1) * 100
        print(f"{kmer} {count} {freq:.1f}%")
    
    # Process k=2
    k2_counts = count_kmers(seq, 2)
    total_kmers_2 = total_length - 1
    items2 = sorted(k2_counts.items(), key=lambda x: (-x[1], x[0]))
    for kmer, count in items2:
        freq = (count / total_kmers_2) * 100
        print(f"{kmer} {count} {freq:.1f}%")
    
    # Process k=3
    k3_counts = count_kmers(seq, 3)
    total_kmers_3 = total_length - 2
    items3 = sorted(k3_counts.items(), key=lambda x: (-x[1], x[0]))
    freqs3 = sorted(set(k3_counts.values()), reverse=True)
    top5_freq_set3 = set(freqs3[:5]) if len(freqs3) >= 5 else set(freqs3)
    for kmer, count in items3:
        if count in top5_freq_set3:
            freq_val = (count / total_kmers_3) * 100
            print(f"{kmer} {count} {freq_val:.1f}%")
    spec_count3 = k3_counts.get('GGT', 0)
    freq_spec3 = (spec_count3 / total_kmers_3) * 100
    print(f"GGT {spec_count3} {freq_spec3:.1f}%")
    
    # Process k=4
    k4_counts = count_kmers(seq, 4)
    total_kmers_4 = total_length - 3
    items4 = sorted(k4_counts.items(), key=lambda x: (-x[1], x[0]))
    freqs4 = sorted(set(k4_counts.values()), reverse=True)
    top5_freq_set4 = set(freqs4[:5]) if len(freqs4) >= 5 else set(freqs4)
    for kmer, count in items4:
        if count in top5_freq_set4:
            freq_val = (count / total_kmers_4) * 100
            print(f"{kmer} {count} {freq_val:.1f}%")
    spec_count4 = k4_counts.get('GGTA', 0)
    freq_spec4 = (spec_count4 / total_kmers_4) * 100
    print(f"GGTA {spec_count4} {freq_spec4:.1f}%")
    
    # Process k=6
    pattern6 = 'GGTATT'
    total_kmers_6 = total_length - 5
    count6 = count_specific(seq, pattern6)
    freq6 = (count6 / total_kmers_6) * 100
    print(f"GGTATT {count6} {freq6:.1f}%")
    
    # Process k=12
    pattern12 = 'GGTATTTTAATT'
    total_kmers_12 = total_length - 11
    count12 = count_specific(seq, pattern12)
    freq12 = (count12 / total_kmers_12) * 100
    print(f"GGTATTTTAATT {count12} {freq12:.1f}%")
    
    # Process k=18
    pattern18 = 'GGTATTTTAATTTATAGT'
    total_kmers_18 = total_length - 17
    count18 = count_specific(seq, pattern18)
    freq18 = (count18 / total_kmers_18) * 100
    print(f"GGTATTTTAATTTATAGT {count18} {freq18:.1f}%")

if __name__ == '__main__':
    main()