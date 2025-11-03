import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

def read_fasta(stdin_data):
    # Skip header lines and join all sequence lines
    return ''.join(line.strip() for line in stdin_data if not line.startswith('>')).upper()

def count_kmers(sequence, k):
    return Counter(sequence[i:i+k] for i in range(len(sequence) - k + 1))

def format_output(k, counter):
    total = sum(counter.values())
    sorted_kmers = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    return f"\n{k}-mer Frequencies:\n" + '\n'.join(
        f"{seq} {count * 100 / total:.3f}%" for seq, count in sorted_kmers
    )

def report_counts(sequence, ks):
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(count_kmers, sequence, k): k for k in ks}
        for future in futures:
            k = futures[future]
            results[k] = future.result()
    return results

if __name__ == "__main__":
    stdin_data = sys.stdin if sys.stdin.isatty() is False else open("input.txt")
    sequence = read_fasta(stdin_data)
    ks_to_check = [1, 2, 3, 4, 6, 12, 18]  # you can adjust

    counts = report_counts(sequence, ks_to_check)
    for k in ks_to_check:
        print(format_output(k, counts[k]))
