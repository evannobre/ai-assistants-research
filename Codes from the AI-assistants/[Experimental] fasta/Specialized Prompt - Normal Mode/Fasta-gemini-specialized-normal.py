import time
import os
import sys

class NaiveLCG:
    """
    A simple Linear Congruential Generator.
    X_{n+1} = (a * X_n + c) % m
    """
    def __init__(self, seed: int, a: int, c: int, m: int):
        if not (0 <= seed < m):
            raise ValueError("Seed must be non-negative and less than modulus m.")
        if not (0 <= a < m):
            raise ValueError("Multiplier 'a' must be non-negative and less than modulus m.")
        if not (0 <= c < m):
            raise ValueError("Increment 'c' must be non-negative and less than modulus m.")
        if m <= 0:
            raise ValueError("Modulus 'm' must be positive.")

        self.current_state = seed
        self.a = a
        self.c = c
        self.m = m

    def next(self) -> int:
        """Generates the next pseudo-random number in the sequence."""
        self.current_state = (self.a * self.current_state + self.c) % self.m
        return self.current_state

def nucleotide_mapper(lcg_value: int, max_lcg_value: int) -> str:
    """
    Maps an LCG generated value to a nucleotide (A, C, G, T).
    Distributes the nucleotides as evenly as possible across the LCG's range.
    """
    # Divide the LCG's range into 4 equal parts
    segment_size = max_lcg_value // 4
    if lcg_value < segment_size:
        return 'A'
    elif lcg_value < 2 * segment_size:
        return 'C'
    elif lcg_value < 3 * segment_size:
        return 'G'
    else:
        return 'T'

def fasta_sequence_generator(
    lcg: NaiveLCG,
    sequence_length: int,
    line_width: int = 80,
    chunk_size: int = 1024 * 1024 # 1 MB chunks for efficient writing
) -> str:
    """
    Generates a FASTA sequence, yielding it in chunks to save memory.
    """
    nucleotides = ['A', 'C', 'G', 'T']
    max_lcg_value = lcg.m - 1 # Maximum possible value from LCG

    # Yield header first
    yield ">simulated_sequence_lcg_length_{}\n".format(sequence_length)

    current_line = []
    generated_count = 0
    buffer = []

    while generated_count < sequence_length:
        lcg_val = lcg.next()
        nucleotide = nucleotide_mapper(lcg_val, max_lcg_value)
        current_line.append(nucleotide)
        generated_count += 1

        if len(current_line) == line_width:
            buffer.append("".join(current_line) + "\n")
            current_line = []

        if len(buffer) * line_width >= chunk_size:
            yield "".join(buffer)
            buffer = []

    # Yield any remaining nucleotides in the current line
    if current_line:
        buffer.append("".join(current_line) + "\n")

    # Yield any remaining buffer content
    if buffer:
        yield "".join(buffer)

def simulate_fasta_to_file(
    output_filepath: str,
    sequence_length: int,
    seed: int,
    lcg_a: int,
    lcg_c: int,
    lcg_m: int,
    line_width: int = 80,
    buffer_chunk_size_bytes: int = 4 * 1024 * 1024 # 4 MB write buffer
):
    """
    Simulates a FASTA sequence and writes it directly to a file,
    optimizing for memory and disk I/O.
    """
    start_time = time.time()
    print(f"Starting FASTA simulation to: {output_filepath}")
    print(f"Target sequence length: {sequence_length}")
    print(f"LCG parameters: seed={seed}, a={lcg_a}, c={lcg_c}, m={lcg_m}")

    lcg_instance = NaiveLCG(seed, lcg_a, lcg_c, lcg_m)

    try:
        with open(output_filepath, 'w') as f:
            # The generator yields parts of the FASTA string
            for chunk in fasta_sequence_generator(lcg_instance, sequence_length, line_width):
                f.write(chunk)
        print(f"Simulation complete. File written to {output_filepath}")
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time:.2f} seconds")

        # Basic verification (optional, can be slow for very large files)
        # file_size = os.path.getsize(output_filepath)
        # print(f"Generated file size: {file_size / (1024*1024):.2f} MB")

    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


# --- Example Usage and Considerations for your system ---

if __name__ == "__main__":
    # LCG parameters:
    # These are common parameters for a "good" LCG, often used in older systems.
    # For a full period (m), c must be relatively prime to m, a-1 must be divisible
    # by all prime factors of m, and a-1 must be a multiple of 4 if m is a multiple of 4.
    # Here, we use parameters that fit a 32-bit range, which is sufficient for many
    # simulations and keeps integer operations fast.
    # Knuth suggests a=1664525, c=1013904223, m=2**32 for a full-period LCG.
    LCG_SEED = int(time.time() * 1000) % (2**32) # Dynamic seed for different runs
    LCG_A = 1664525
    LCG_C = 1013904223
    LCG_M = 2**32 # Modulus for 32-bit unsigned integers

    # For a 64-bit system, you could use a larger modulus for a longer period,
    # but 2**32 provides a sufficiently long sequence for many simulations (period of 2^32).
    # If a truly massive sequence is needed, LCG_M = 2**64 would be appropriate,
    # but Python's arbitrary-precision integers handle this seamlessly.
    # LCG_M = 2**64
    # LCG_A = 6364136223846793005
    # LCG_C = 1442695040888963407


    # Simulation parameters:
    # 1 GB of sequence data roughly translates to 1 billion bases.
    # Adjust `sequence_length` based on your simulation needs and disk space.
    # A 30 GB SSD can hold quite a lot, but be mindful of total usage.
    # 1 GB FASTA sequence (10^9 characters) will take ~1 GB on disk.
    # For a FASTA file with 80 chars per line + newline, it's about 1.0125 GB per 10^9 bases.
    # So, 10 billion bases is roughly 10 GB.
    # Let's aim for a sequence that fits comfortably within 30GB.
    # Example: 5 billion bases = 5 GB approx.
    # Max practical length given 30GB SSD: ~25-28 billion bases, leaving space for OS/other files.
    TARGET_SEQUENCE_LENGTH = 5 * (10**9)  # 5 billion bases, ~5 GB FASTA file
    OUTPUT_FILENAME = "simulated_fasta_lcg.fasta"
    FASTA_LINE_WIDTH = 80 # Standard FASTA line width

    # The `buffer_chunk_size_bytes` controls how much data is buffered in memory
    # before being written to disk. A larger buffer might reduce disk I/O calls
    # but uses more RAM. 4MB is a reasonable balance.
    # 16 GB vRAM is plenty for this buffering strategy.
    BUFFER_CHUNK_SIZE_BYTES = 4 * 1024 * 1024 # 4 MB

    print("\nSystem specifications considered:")
    print(f"  OS: Ubuntu 24.04.2 LTS 64-bit")
    print(f"  SSD: 30 GB (will write to {os.path.abspath(OUTPUT_FILENAME)})")
    print(f"  vRAM: 16 GB (using streaming and buffering to stay well within limits)")
    print("-" * 50)

    simulate_fasta_to_file(
        OUTPUT_FILENAME,
        TARGET_SEQUENCE_LENGTH,
        LCG_SEED,
        LCG_A,
        LCG_C,
        LCG_M,
        FASTA_LINE_WIDTH,
        BUFFER_CHUNK_SIZE_BYTES
    )

    print("\nAlgorithm Notes:")
    print("- Uses Python's native integer arithmetic and file I/O.")
    print("- Employs generators to avoid holding the entire sequence in memory.")
    print("- Buffers data to disk in chunks for efficient I/O operations.")
    print("- LCG parameters are chosen for a reasonable period within a 32-bit range.")
    print("- The 'randomness' of a naive LCG is limited; for high-quality simulations,")
    print("  more sophisticated PRNGs (like Mersenne Twister, used by Python's `random` module)")
    print("  would be preferred, but this adheres to the 'naive LCG' constraint.")
    print("- The nucleotide distribution is uniform (25% for each) based on LCG output.")
    print("- No external libraries (like `numpy`, `Biopython`) are used to meet the 'native libraries' requirement.")