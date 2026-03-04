import time

# Naïve LCG parameters (example values)
a = 1664525
c = 1013904223
m = 2**32
seed = int(time.time())  # Use current time as seed

def lcg(seed):
    while True:
        seed = (a * seed + c) % m
        yield seed / m  # Normalize to [0,1)

# FASTA sequence generator
def generate_fasta_sequence(length, probabilities=None):
    bases = ['A', 'C', 'G', 'T']
    if probabilities is None:
        probabilities = [0.25, 0.25, 0.25, 0.25]  # Uniform

    gen = lcg(seed)
    sequence = []

    for _ in range(length):
        r = next(gen)
        cumulative = 0.0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r < cumulative:
                sequence.append(bases[i])
                break

    return ''.join(sequence)

# Example usage
fasta_seq = generate_fasta_sequence(1000)
print(fasta_seq)
