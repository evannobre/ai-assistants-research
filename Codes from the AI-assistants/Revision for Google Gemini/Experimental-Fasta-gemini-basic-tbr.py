import sys
import itertools
import bisect

# 1. Naïve Linear Congruential Generator
def lcg_generator(seed=42):
    """Yields uniformly distributed floats [0.0, 1.0) using strict LCG rules."""
    IM = 139968
    IA = 3877
    IC = 29573
    last = seed
    
    while True:
        last = (last * IA + IC) % IM
        yield last / IM

# 2. Probability Distribution Builder
def build_cumulative_probs(prob_dict):
    """Uses itertools.accumulate to build cumulative probabilities natively."""
    chars = list(prob_dict.keys())
    probs = list(prob_dict.values())
    
    # itertools.accumulate handles the running total natively
    cum_probs = list(itertools.accumulate(probs))
    return chars, cum_probs

# 3. Repeating Sequence Generator (Sequence ONE)
def make_repeat_fasta(id_desc, n, alu_seq):
    """Uses itertools.cycle and islice to repeat a string infinitely."""
    sys.stdout.write(f">{id_desc}\n")
    
    # Create an infinite native C-iterator from the Alu sequence
    seq_iterator = itertools.cycle(alu_seq)
    
    width = 60
    for i in range(0, n, width):
        chunk_size = min(width, n - i)
        # islice extracts exactly 'chunk_size' elements without list comprehensions
        line = "".join(itertools.islice(seq_iterator, chunk_size))
        sys.stdout.write(f"{line}\n")

# 4. Random Sequence Generator (Sequences TWO and THREE)
def make_random_fasta(id_desc, n, chars, cum_probs, lcg_gen):
    """Uses bisect for fast native binary search of probability distributions."""
    sys.stdout.write(f">{id_desc}\n")
    width = 60
    
    for i in range(0, n, width):
        chunk_size = min(width, n - i)
        
        # bisect.bisect_right natively maps the random float to the correct character
        line = "".join(
            chars[bisect.bisect_right(cum_probs, next(lcg_gen))] 
            for _ in range(chunk_size)
        )
        sys.stdout.write(f"{line}\n")

def main(n=1000):
    # Benchmark specific Alu sequence
    ALU = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    # Dictionary insertion order is preserved in Python 3.7+
    IUB = {
        'a': 0.27, 'c': 0.12, 'g': 0.12, 't': 0.27,
        'B': 0.02, 'D': 0.02, 'H': 0.02, 'K': 0.02,
        'M': 0.02, 'N': 0.02, 'R': 0.02, 'S': 0.02,
        'V': 0.02, 'W': 0.02, 'Y': 0.02
    }

    HOMO_SAPIENS = {
        'a': 0.3029549426680,
        'c': 0.1979883004921,
        'g': 0.1975473066391,
        't': 0.3015094502008
    }

    # Initialize the generator state once so it persists across calls
    lcg_gen = lcg_generator(seed=42)

    # Sequence 1: Homo sapiens alu (Length: n * 2)
    make_repeat_fasta("ONE Homo sapiens alu", n * 2, ALU)

    # Sequence 2: IUB ambiguity codes (Length: n * 3)
    iub_chars, iub_cum = build_cumulative_probs(IUB)
    make_random_fasta("TWO IUB ambiguity codes", n * 3, iub_chars, iub_cum, lcg_gen)

    # Sequence 3: Homo sapiens frequency (Length: n * 5)
    hs_chars, hs_cum = build_cumulative_probs(HOMO_SAPIENS)
    make_random_fasta("THREE Homo sapiens frequency", n * 5, hs_chars, hs_cum, lcg_gen)

if __name__ == "__main__":
    # The benchmark passes `n` as a command line argument (defaulting to 1000 here)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    main(n)