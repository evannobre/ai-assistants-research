import itertools
import bisect
import sys

class NaiveLCG:
    """Naïve linear congruential generator: X_{n+1} = (a*X_n + c) mod m."""
    __slots__ = ("a","c","m","state")
    def __init__(self, seed=42,
                 a=1664525, c=1013904223, m=2**32):
        self.a, self.c, self.m = a, c, m
        self.state = seed

    def random(self):
        """Return a float in [0,1)."""
        self.state = (self.a * self.state + self.c) % self.m
        # divide as float
        return self.state / self.m

def make_cdf(symbols, freqs):
    """Build a cumulative distribution array for binary search."""
    cum = list(itertools.accumulate(freqs))
    return cum, symbols

def random_fasta(out_stream, name, length,
                 rng, symbols, cumdist, width=60):
    """Write a single FASTA sequence of given length."""
    # Header
    print(f">{name}", file=out_stream)
    # Generate and buffer
    line = []
    for _ in range(length):
        u = rng.random()
        idx = bisect.bisect_left(cumdist, u)
        line.append(symbols[idx])
        if len(line) == width:
            print("".join(line), file=out_stream)
            line.clear()
    # last partial line
    if line:
        print("".join(line), file=out_stream)

def main():
    # Example nucleotide frequencies
    symbols = ["A", "C", "G", "T"]
    freqs   = [0.27, 0.12, 0.12, 0.27]
    # Ensure they sum to 1.0
    # Build CDF
    cumdist, syms = make_cdf(symbols, freqs)

    # Instantiate RNG
    rng = NaiveLCG(seed=12345)

    # Write two example FASTA sequences to stdout
    random_fasta(sys.stdout, "rand1", 1_000_000, rng, syms, cumdist)
    random_fasta(sys.stdout, "rand2", 500_000,  rng, syms, cumdist)

if __name__ == "__main__":
    main()
