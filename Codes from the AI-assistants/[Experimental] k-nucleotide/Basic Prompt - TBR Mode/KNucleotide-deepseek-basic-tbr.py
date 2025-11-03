import sys

def main():
    if len(sys.argv) < 2:
        return
    
    filename = sys.argv[1]
    with open(filename) as f:
        sequence_lines = []
        found_three = False
        for line in f:
            if line.startswith('>') and 'THREE' in line:
                found_three = True
                break
        if not found_three:
            return
        for line in f:
            if line.startswith('>'):
                break
            sequence_lines.append(line.strip().upper())
    sequence = ''.join(sequence_lines)
    n = len(sequence)
    
    # k=1
    total = n
    bases = "ACGT"
    base_counts = {}
    for base in bases:
        base_counts[base] = sequence.count(base)
    for base in sorted(bases):
        count_val = base_counts[base]
        percentage = (count_val * 100.0) / total
        print(f"{base} {percentage:.3f}")
    
    # k=2
    k2_mers = [a + b for a in bases for b in bases]
    k2_mers.sort()
    k2_counts = {mer: 0 for mer in k2_mers}
    for i in range(n - 1):
        mer = sequence[i:i+2]
        if mer in k2_counts:
            k2_counts[mer] += 1
    for mer in k2_mers:
        count_val = k2_counts[mer]
        percentage = (count_val * 100.0) / (n - 1)
        print(f"{mer} {percentage:.3f}")
    
    # Specific queries
    queries = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT"
    ]
    for q in queries:
        k = len(q)
        count = 0
        start = 0
        while start <= n - k:
            pos = sequence.find(q, start)
            if pos == -1:
                break
            count += 1
            start = pos + 1
        print(f"{count}\t{q}")

if __name__ == "__main__":
    main()