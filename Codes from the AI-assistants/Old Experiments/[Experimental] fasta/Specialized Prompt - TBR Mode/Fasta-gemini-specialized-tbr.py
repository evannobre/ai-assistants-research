import sys
import os

class FastaSimulator:
    """
    A memory-efficient FASTA file simulator using a naïve Linear Congruential Generator.
    This implementation streams the output directly to a file to handle large sequences
    on systems with limited RAM.
    """

    def __init__(self, config):
        # --- LCG Parameters ---
        # Using common parameters from Numerical Recipes. For 64-bit, 2**64 is a good m.
        self.m = config.get('m', 2**32)
        self.a = config.get('a', 1664525)
        self.c = config.get('c', 1013904223)
        self.seed = config.get('seed', 42)
        
        # --- FASTA Simulation Parameters ---
        self.output_filepath = config['output_filepath']
        self.num_sequences = config['num_sequences']
        self.sequence_length = config['sequence_length']
        self.line_length = config.get('line_length', 80)
        self.alphabet = config.get('alphabet', ['A', 'C', 'G', 'T'])
        self.alphabet_size = len(self.alphabet)

        # Internal state for the LCG
        self._lcg_state = 0

    def _initialize_lcg(self):
        """Initializes or resets the LCG state."""
        self._lcg_state = self.seed

    def _generate_random_int(self):
        """Generates the next pseudo-random integer using the LCG equation."""
        self._lcg_state = (self.a * self._lcg_state + self.c) % self.m
        return self._lcg_state

    def run_simulation(self):
        """
        Executes the FASTA simulation and writes the output to a file.
        """
        print(f"Starting FASTA simulation...")
        print(f"Configuration: {self.num_sequences} sequences of length {self.sequence_length}.")
        print(f"Output will be written to: {self.output_filepath}")

        self._initialize_lcg()
        
        try:
            with open(self.output_filepath, 'w') as f:
                for i in range(1, self.num_sequences + 1):
                    # 1. Write FASTA header
                    f.write(f">sequence_{i} | generated with naive LCG\n")
                    
                    line_buffer = []
                    for _ in range(self.sequence_length):
                        # 2. Generate a random number and map to the alphabet
                        random_int = self._generate_random_int()
                        # Scale to [0, 1) then map to alphabet index
                        index = int((random_int / self.m) * self.alphabet_size)
                        char = self.alphabet[index]
                        
                        line_buffer.append(char)
                        
                        # 3. Write to file when the buffer is full
                        if len(line_buffer) == self.line_length:
                            f.write("".join(line_buffer) + "\n")
                            line_buffer.clear()
                    
                    # 4. Flush any remaining characters in the buffer
                    if line_buffer:
                        f.write("".join(line_buffer) + "\n")
            
            print("Simulation completed successfully.")

        except IOError as e:
            print(f"Error: Could not write to file {self.output_filepath}", file=sys.stderr)
            print(e, file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == '__main__':
    # --- Configuration ---
    # This configuration is safe for the specified hardware.
    # A 10M-base sequence is approx 10MB. 100 such sequences is 1GB.
    simulation_config = {
        "output_filepath": "./simulation_output.fasta",
        "num_sequences": 100,
        "sequence_length": 10_000_000,
        "line_length": 80,
        "alphabet": ['A', 'C', 'G', 'T'],
        "seed": 12345,
        # LCG params
        "m": 2**32,
        "a": 1664525,
        "c": 1013904223,
    }
    
    # Check if the output directory exists
    output_dir = os.path.dirname(simulation_config['output_filepath'])
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    simulator = FastaSimulator(simulation_config)
    simulator.run_simulation()