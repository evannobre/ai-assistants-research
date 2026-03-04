def decode(code):
    out = []
    for _ in range(k):
        bits = code & 0b11
        out.append({0b00:'A', 0b01:'C', 0b10:'G', 0b11:'T'}[bits])
        code >>= 2
    return ''.join(reversed(out))

import argparse
from collections import Counter

# 2-bit encoding for A/C/G/T
ENC = {'A':0, 'C':1, 'G':2, 'T':3}

def count_kmers(filepath: str, k: int):
    mask = (1 << (2 * k)) - 1
    counts = Counter()
    rolling_hash = 0
    window_len = 0

    with open(filepath, 'r') as f:
        while True:
            ch = f.read(1)
            if not ch:
                break
            if ch in '\n\r>':  # skip newlines or FASTA headers
                if ch == '>':
                    # skip FASTA header line
                    f.readline()
                continue

            ch = ch.upper()
            if ch not in ENC:
                continue

            rolling_hash = ((rolling_hash << 2) | ENC[ch]) & mask
            window_len += 1

            if window_len >= k:
                counts[rolling_hash] += 1

    return counts

def decode_kmer(code: int, k: int) -> str:
    rev = []
    for _ in range(k):
        rev.append('ACGT'[code & 0b11])
        code >>= 2
    return ''.join(reversed(rev))

def main():
    parser = argparse.ArgumentParser(description='Count k‐mers in a DNA sequence.')
    parser.add_argument('file', help='Input FASTA/text file')
    parser.add_argument('-k', type=int, required=True, help='k‐mer length')
    args = parser.parse_args()

    counts = count_kmers(args.file, args.k)
    # Print top 10 most frequent k-mers
    for code, cnt in counts.most_common(10):
        print(decode_kmer(code, args.k), cnt)

if __name__ == '__main__':
    main()
