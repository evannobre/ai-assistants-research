import sys
from itertools import product

base_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

def encode_kmer(s, base_map):
    num = 0
    for c in s:
        num = (num << 2) | base_map[c]
    return num

def count_kmers(seq, k, base_map):
    n = len(seq)
    if n < k:
        return {}
    mask = (1 << (2 * k)) - 1
    num = 0
    for i in range(k):
        num = (num << 2) | base_map[seq[i]]
    counts = {}
    counts[num] = 1
    for i in range(0, n - k):
        num = (num << 2) | base_map[seq[i + k]]
        num &= mask
        counts[num] = counts.get(num, 0) + 1
    return counts

def main():
    data = sys.stdin.read()
    lines = data.splitlines()
    seq_lines = []
    found = False
    for line in lines:
        if line.startswith('>'):
            if "THREE" in line:
                found = True
            else:
                found = False
        elif found:
            seq_lines.append(line.strip().upper())
    sequence = ''.join(seq_lines)
    
    k1 = 1
    all_1mers = [''.join(p) for p in product("ACGT", repeat=k1)]
    counts_dict1 = count_kmers(sequence, k1, base_map)
    total1 = len(sequence) - k1 + 1
    freqs1 = []
    for kmer in all_1mers:
        num = encode_kmer(kmer, base_map)
        cnt = counts_dict1.get(num, 0)
        pct = cnt * 100.0 / total1
        freqs1.append((kmer, pct))
    freqs1.sort(key=lambda x: (-x[1], x[0]))
    for kmer, pct in freqs1:
        print(f"{kmer} {pct:.3f}")
    
    k2 = 2
    all_2mers = [''.join(p) for p in product("ACGT", repeat=k2)]
    counts_dict2 = count_kmers(sequence, k2, base_map)
    total2 = len(sequence) - k2 + 1
    freqs2 = []
    for kmer in all_2mers:
        num = encode_kmer(kmer, base_map)
        cnt = counts_dict2.get(num, 0)
        pct = cnt * 100.0 / total2
        freqs2.append((kmer, pct))
    freqs2.sort(key=lambda x: (-x[1], x[0]))
    for kmer, pct in freqs2:
        print(f"{kmer} {pct:.3f}")
    
    patterns = ["GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"]
    for pattern in patterns:
        k = len(pattern)
        counts_dict = count_kmers(sequence, k, base_map)
        num_pat = encode_kmer(pattern, base_map)
        count_val = counts_dict.get(num_pat, 0)
        print(count_val)

if __name__ == "__main__":
    main()