import sys

class PiSpigot:
    """
    A generator class for digits of Pi using the Unbounded Spigot Algorithm.
    Adheres to the Linear Fractional Transformation (LFT) approach.
    """
    def __init__(self):
        # Initial state of the LFT matrix corresponding to the start of the series
        self.q = 1
        self.r = 0
        self.t = 1
        self.k = 1
        self.n = 3
        self.l = 3

    def extract(self, x):
        """
        Extracts the integer part of the LFT at point x.
        Mathematically equivalent to: (q * x + r) // t
        """
        return (self.q * x + self.r) // self.t

    def next_term(self):
        """
        Consumes the next term of the infinite series to refine the interval.
        Corresponds to multiplying the state matrix by:
        [ k,  4k+2 ]
        [ 0,  2k+1 ]
        """
        k = self.k
        k2 = 2 * k + 1
        
        # Matrix multiplication optimizations for specific Pi series
        self.r = self.q * (4 * k + 2) + self.r * k2
        self.t *= k2
        self.q *= k
        self.k += 1

    def produce(self, digit):
        """
        Produces a digit and narrows the interval.
        Corresponds to multiplying the state matrix by the inverse matrix for the digit:
        [ 10, -10*digit ]
        [ 0,  1         ]
        """
        self.q *= 10
        self.r = 10 * (self.r - digit * self.t)
        # t remains unchanged in this specific transformation

    def generate(self, count):
        """
        Yields the first 'count' digits of Pi.
        """
        i = 0
        while i < count:
            # Strictly following the prompt: Check extract(3) and extract(4)
            y = self.extract(3)
            
            # Optimization check: 
            # If the digit 'y' is consistent across the interval [3, 4], it is safe to print.
            if y == self.extract(4):
                yield y
                self.produce(y)
                i += 1
            else:
                self.next_term()

def main():
    # Parse command line argument for N
    n_digits = 100
    if len(sys.argv) > 1:
        try:
            n_digits = int(sys.argv[1])
        except ValueError:
            sys.stderr.write("Invalid argument. Using default N=100.\n")

    spigot = PiSpigot()
    
    # Formatting controls
    line_buffer = []
    total_count = 0

    for digit in spigot.generate(n_digits):
        line_buffer.append(str(digit))
        total_count += 1
        
        # Print 10 digits per line with running total
        if len(line_buffer) == 10:
            print(f"{''.join(line_buffer)}\t:{total_count}")
            line_buffer = []

    # Handle remaining digits (pad with spaces if necessary)
    if line_buffer:
        padding = " " * (10 - len(line_buffer))
        print(f"{''.join(line_buffer)}{padding}\t:{total_count}")

if __name__ == "__main__":
    main()