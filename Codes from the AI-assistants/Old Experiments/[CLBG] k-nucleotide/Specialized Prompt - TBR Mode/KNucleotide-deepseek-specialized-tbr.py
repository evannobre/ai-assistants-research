import sys
import array

def to_code(c):
    return {'A': 0, 'C': 1, 'G': 2, 'T': 3}.get(c, 0)

def main():
    seq_str = ""
    found_three = False
    for line in sys.stdin:
        if line.startswith('>'):
            if line[1:].strip() == 'THREE':
                found_three = True
            else:
                found_three = False
        elif found_three:
            seq_str += line.strip().upper()
    
    if not seq_str:
        return
    
    seq_arr = array.array('B')
    for c in seq_str:
        seq_arr.append(to_code(c))
    n = len(seq_arr)

    def count_kmers(seq, k):
        if k <= 0 or k > len(seq):
            return {}
        counts = {}
        mask = (1 << (2 * k)) - 1
        key = 0
        for i in range(k):
            key = (key << 2) | seq[i]
        counts[key] = counts.get(key, 0) + 1
        for i in range(k, len(seq)):
            key = ((key << 2) | seq[i]) & mask
            counts[key] = counts.get(key, 0) + 1
        return counts

    def key_to_string(key, k):
        s = ''
        temp = key
        for _ in range(k):
            c = temp & 3
            temp >>= 2
            s = 'ACGT'[c] + s
        return s

    for k in [1, 2]:
        counts_dict = count_kmers(seq_arr, k)
        total = n - k + 1
        items = []
        for key, count in counts_dict.items():
            kmer = key_to_string(key, k)
            items.append((kmer, count))
        items.sort(key=lambda x: (-x[1], x[0]))
        for kmer, count in items:
            percentage = (count * 100.0) / total
            print(f"{kmer} {percentage:.3f}")

    specific_sequences = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT"
    ]
    
    computed_counts = {}
    for s in specific_sequences:
        k = len(s)
        if k not in computed_counts:
            computed_counts[k] = count_kmers(seq_arr, k)
        key = 0
        for c in s:
            key = (key << 2) | to_code(c)
        count = computed_counts[k].get(key, 0)
        print(f"{count}\t{s}")

if __name__ == "__main__":
    main()