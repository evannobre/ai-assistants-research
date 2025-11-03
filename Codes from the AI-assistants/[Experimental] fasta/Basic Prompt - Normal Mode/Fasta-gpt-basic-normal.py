import sys
from itertools import islice

# Naïve Linear Congruential Generator
class NaiveLCG:
    def __init__(self, seed=42):
        self.modulus = 2**31
        self.a = 1103515245
        self.c = 12345
        self.state = seed

    def next(self):
        self.state = (self.a * self.state + self.c) % self.modulus
        return self.state

    def next_float(self):
        return self.next() / self.modulus


# DNA base generator using LCG
class FastaGenerator:
    def __init__(self, lcg, width=60):
        self.lcg = lcg
        self.width = width
        self.bases = "ACGT"
        self.probs = [0.25, 0.25, 0.25, 0.25]  # Uniform distribution

        # Precompute cumulative probability for faster mapping
        self.cdf = []
        cumulative = 0.0
        for p in self.probs:
            cumulative += p
            self.cdf.append(cumulative)

    def random_base(self):
        r = self.lcg.next_float()
        for i, p in enumerate(self.cdf):
            if r < p:
                return self.bases[i]
        return self.bases[-1]  # fallback

    def generate_sequence(self, length):
        for _ in range(0, length, self.width):
            line = ''.join(self.random_base() for _ in range(min(self.width, length)))
            yield line
            length -= self.width


# FASTA output
def fasta_simulation(label, length, seed=42, width=60):
    lcg = NaiveLCG(seed)
    generator = FastaGenerator(lcg, width)

    print(f">{label}")
    for line in generator.generate_sequence(length):
        print(line)


# Example usage
if __name__ == "__main__":
    # Simulate a 1000-base sequence with label 'SEQ1'
    fasta_simulation(label="SEQ1", length=1000)
