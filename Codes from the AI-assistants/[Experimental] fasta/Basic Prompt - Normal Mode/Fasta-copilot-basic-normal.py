import sys

# Naïve LCG class
class NaiveLCG:
    def __init__(self, seed=42):
        self.modulus = 2**31
        self.multiplier = 1103515245
        self.increment = 12345
        self.state = seed

    def next(self):
        self.state = (self.multiplier * self.state + self.increment) % self.modulus
        return self.state / self.modulus  # Normalize to [0,1)

# FASTA simulation using LCG
def generate_fasta(sequence_id: str, description: str, length: int, line_width: int = 60):
    lcg = NaiveLCG(seed=2025)
    bases = "ACGT"

    print(f">{sequence_id} {description}")
    for _ in range(0, length, line_width):
        line = ''.join(bases[int(lcg.next() * len(bases))] for _ in range(min(line_width, length)))
        print(line)
        length -= line_width

# Example usage
if __name__ == "__main__":
    generate_fasta("seq1", "Example FASTA sequence using naïve LCG", 300)
