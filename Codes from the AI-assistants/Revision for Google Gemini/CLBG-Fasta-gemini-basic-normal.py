Here is the implementation in Python. It heavily leverages native libraries (like the `bisect` module for binary search) while strictly following the naïve mathematical implementations and constraints you specified.

### Python Implementation

```python
import sys
import bisect

# Linear Congruential Generator Constants
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def gen_random(max_val):
    """
    Naïve Linear Congruential Generator.
    Calculates a random number each time without caching.
    """
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

def make_cumulative(alphabet):
    """
    Converts the expected probability of selecting each nucleotide 
    into cumulative probabilities.
    """
    cums = []
    chars = []
    cum = 0.0
    for char, prob in alphabet:
        cum += prob
        cums.append(cum)
        chars.append(char)
    return cums, chars

def repeat_fasta(id_desc, seq, n):
    """
    Generates DNA sequences by repeatedly copying from a given sequence.
    """
    print(f">{id_desc}")
    seq_len = len(seq)
    pos = 0
    while n > 0:
        line_len = min(60, n)
        line = []
        for _ in range(line_len):
            line.append(seq[pos])
            pos = (pos + 1) % seq_len
        print("".join(line))
        n -= line_len

def random_fasta(id_desc, cums, chars, n):
    """
    Generates DNA sequences by weighted random selection.
    Uses bisect (native library) for binary search against cumulative probabilities.
    """
    print(f">{id_desc}")
    while n > 0:
        line_len = min(60, n)
        line = []
        for _ in range(line_len):
            r = gen_random(1.0)
            idx = bisect.bisect_right(cums, r)
            line.append(chars[idx])
        print("".join(line))
        n -= line_len

def main():
    # Read the target n from command-line arguments, defaulting to 25,000,000
    n = 25000000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass

    # Sequence and Alphabets
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    iub = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]

    homosapiens = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]

    # Convert to cumulative probability distributions
    iub_cums, iub_chars = make_cumulative(iub)
    hs_cums, hs_chars = make_cumulative(homosapiens)

    # 1. Generate ALU sequence (n * 2)
    repeat_fasta("ONE Homo sapiens alu", alu, n * 2)
    
    # 2. Generate IUB sequence (n * 3)
    random_fasta("TWO IUB ambiguity codes", iub_cums, iub_chars, n * 3)
    
    # 3. Generate Homo Sapiens sequence (n * 5)
    random_fasta("THREE Homo sapiens frequency", hs_cums, hs_chars, n * 5)

if __name__ == "__main__":
    main()

```

### Execution

To test the performance with the requested sequence scale, you can run the program from your terminal, passing the parameter:

```bash
python fasta.py 25000000 > output.fasta

```