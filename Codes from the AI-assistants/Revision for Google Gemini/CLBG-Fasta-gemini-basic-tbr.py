import sys
import bisect

# --- Naïve Linear Congruential Generator (LCG) Variables ---
IM = 139968
IA = 3877
IC = 29573
SEED = 42

def get_random(max_val):
    """
    Calculates a random number each time a nucleotide is selected.
    Strictly follows: Seed = (Seed * IA + IC) modulo IM
                      return Max * Seed / IM
    Does NOT cache the random number sequence.
    """
    global SEED
    SEED = (SEED * IA + IC) % IM
    return max_val * SEED / IM

def make_cumulative(alphabet_probs):
    """
    Converts expected probabilities into cumulative probabilities.
    Returns separate lists for cumulative probabilities and corresponding characters
    to allow the use of the native `bisect` library for binary searching.
    """
    cumulative = 0.0
    c_probs = []
    chars = []
    for char, prob in alphabet_probs:
        cumulative += prob
        c_probs.append(cumulative)
        chars.append(char)
    return c_probs, chars

def make_repeat_fasta(seq_id, desc, s, n):
    """
    Generates a DNA sequence by repeatedly copying from a given sequence (alu).
    """
    sys.stdout.write(f">{seq_id} {desc}\n")
    s_len = len(s)
    pos = 0
    
    # Pre-allocate buffer for faster standard I/O
    while n > 0:
        line_len = min(n, 60)
        if pos + line_len <= s_len:
            sys.stdout.write(s[pos:pos+line_len] + "\n")
            pos += line_len
            if pos == s_len:
                pos = 0
        else:
            # Wrap around the sequence
            sys.stdout.write(s[pos:] + s[:line_len - (s_len - pos)] + "\n")
            pos = line_len - (s_len - pos)
        n -= line_len

def make_random_fasta(seq_id, desc, c_probs, chars, n):
    """
    Generates DNA sequences by weighted random selection using binary search.
    Does NOT use a scaling factor to optimize lookup.
    """
    sys.stdout.write(f">{seq_id} {desc}\n")
    
    while n > 0:
        line_len = min(n, 60)
        line_chars = []
        for _ in range(line_len):
            r = get_random(1.0)
            # Use native C-optimized library to perform Binary Search on cumulative probabilities
            idx = bisect.bisect(c_probs, r)
            line_chars.append(chars[idx])
            
        line_chars.append('\n')
        sys.stdout.write("".join(line_chars))
        n -= line_len

def main():
    # Read the command-line argument `N` (default to 1000 if not provided)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    # 1. ALU Sequence
    alu = (
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"
    )

    # 2. IUB Alphabet
    iub_probs = [
        ('a', 0.27), ('c', 0.12), ('g', 0.12), ('t', 0.27),
        ('B', 0.02), ('D', 0.02), ('H', 0.02), ('K', 0.02),
        ('M', 0.02), ('N', 0.02), ('R', 0.02), ('S', 0.02),
        ('V', 0.02), ('W', 0.02), ('Y', 0.02)
    ]
    iub_c_probs, iub_chars = make_cumulative(iub_probs)

    # 3. Homo Sapiens Alphabet
    homosapiens_probs = [
        ('a', 0.3029549426680),
        ('c', 0.1979883004921),
        ('g', 0.1975473066391),
        ('t', 0.3015094502008)
    ]
    homosapiens_c_probs, homosapiens_chars = make_cumulative(homosapiens_probs)

    # Execute generation per benchmark requirements
    make_repeat_fasta("ONE", "Homo sapiens alu", alu, n * 2)
    make_random_fasta("TWO", "IUB ambiguity codes", iub_c_probs, iub_chars, n * 3)
    make_random_fasta("THREE", "Homo sapiens frequency", homosapiens_c_probs, homosapiens_chars, n * 5)

if __name__ == "__main__":
    main()