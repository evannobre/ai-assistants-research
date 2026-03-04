import sys

def reverse_complement():
    # Translation table for all IUPAC codes
    # Maps each character to its complement
    trans = bytes.maketrans(
        b"ACGTUMRWSYKVHDBNacgtumrwsykvhdbn",
        b"TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn"
    )
    
    seq = bytearray()
    
    def process_sequence(header, data):
        if header:
            sys.stdout.buffer.write(header + b"\n")
        if data:
            # 1. Reverse the sequence
            data.reverse()
            # 2. Complement using the optimized translate method
            data = data.translate(trans)
            
            # 3. Output with 60 chars per line
            for i in range(0, len(data), 60):
                sys.stdout.buffer.write(data[i:i+60] + b"\n")

    current_header = None
    
    for line in sys.stdin.buffer:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith(b">"):
            if current_header:
                process_sequence(current_header, seq)
                seq = bytearray()
            current_header = line
        else:
            seq.extend(line)
            
    # Process the final sequence in the file
    process_sequence(current_header, seq)

if __name__ == "__main__":
    reverse_complement()