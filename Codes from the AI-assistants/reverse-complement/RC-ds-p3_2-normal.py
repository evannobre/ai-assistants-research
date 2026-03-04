import sys
import io

class ReverseComplementOptimized:
    def __init__(self):
        # Create translation table for bytes.translate()
        self.trans_table = bytearray(256)
        for i in range(256):
            self.trans_table[i] = i
        
        # ASCII values for nucleotides
        # Uppercase
        self.trans_table[65] = 84   # A -> T
        self.trans_table[67] = 71   # C -> G
        self.trans_table[71] = 67   # G -> C
        self.trans_table[84] = 65   # T -> A
        self.trans_table[85] = 65   # U -> A
        
        # Ambiguous bases (uppercase)
        self.trans_table[77] = 75   # M -> K
        self.trans_table[82] = 89   # R -> Y
        self.trans_table[87] = 87   # W -> W
        self.trans_table[83] = 83   # S -> S
        self.trans_table[89] = 82   # Y -> R
        self.trans_table[75] = 77   # K -> M
        self.trans_table[86] = 66   # V -> B
        self.trans_table[72] = 68   # H -> D
        self.trans_table[68] = 72   # D -> H
        self.trans_table[66] = 86   # B -> V
        self.trans_table[78] = 78   # N -> N
        
        # Lowercase
        self.trans_table[97] = 116  # a -> t
        self.trans_table[99] = 103  # c -> g
        self.trans_table[103] = 99  # g -> c
        self.trans_table[116] = 97  # t -> a
        self.trans_table[117] = 97  # u -> a
        
        # Ambiguous bases (lowercase)
        self.trans_table[109] = 107  # m -> k
        self.trans_table[114] = 121  # r -> y
        self.trans_table[119] = 119  # w -> w
        self.trans_table[115] = 115  # s -> s
        self.trans_table[121] = 114  # y -> r
        self.trans_table[107] = 109  # k -> m
        self.trans_table[118] = 98   # v -> b
        self.trans_table[104] = 100  # h -> d
        self.trans_table[100] = 104  # d -> h
        self.trans_table[98] = 118   # b -> v
        self.trans_table[110] = 110  # n -> n
        
        self.trans_table = bytes(self.trans_table)
    
    def reverse_complement_bytes(self, sequence: bytes) -> bytes:
        """Return reverse complement using bytes for maximum speed."""
        # Translate then reverse
        complemented = sequence.translate(self.trans_table)
        return complemented[::-1]
    
    def process_fasta(self):
        """Process FASTA from stdin line by line with buffered I/O."""
        buffer = bytearray()
        current_header = None
        out_buffer = io.BytesIO()
        
        for line in sys.stdin.buffer:
            if line.startswith(b'>'):
                # Process previous sequence if exists
                if current_header is not None and buffer:
                    # Get reverse complement
                    rev_comp = self.reverse_complement_bytes(buffer)
                    
                    # Write header
                    out_buffer.write(current_header + b'\n')
                    
                    # Write sequence in FASTA format (60 chars per line)
                    seq_len = len(rev_comp)
                    for i in range(0, seq_len, 60):
                        out_buffer.write(rev_comp[i:i+60] + b'\n')
                
                # Start new sequence
                current_header = line.rstrip()
                buffer.clear()
            else:
                # Remove newline and accumulate
                line = line.rstrip()
                if line:
                    buffer.extend(line)
        
        # Process last sequence
        if current_header is not None and buffer:
            rev_comp = self.reverse_complement_bytes(buffer)
            out_buffer.write(current_header + b'\n')
            seq_len = len(rev_comp)
            for i in range(0, seq_len, 60):
                out_buffer.write(rev_comp[i:i+60] + b'\n')
        
        # Write all output
        sys.stdout.buffer.write(out_buffer.getvalue())

def main():
    rc = ReverseComplementOptimized()
    rc.process_fasta()

if __name__ == "__main__":
    main()