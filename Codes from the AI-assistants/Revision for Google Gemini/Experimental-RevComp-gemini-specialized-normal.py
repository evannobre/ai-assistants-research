#!/usr/bin/env python3
"""
Reverse Complement Simulator
Optimized for O(1) Memory footprint via Two-Pass Backward Disk Seek
"""

import sys
import os
import argparse

def process_fasta_optimized(input_path: str, output_path: str, block_size: int = 65536, line_len: int = 80):
    # 1. Byte-level Translation Table (Includes standard IUPAC ambiguity codes)
    # Unmapped characters remain untouched by default.
    intab  = b"ACGTRYSWKMBDHVNacgtryswkmbdhvn"
    outtab = b"TGCAYRWSMKVHDBNtgcayrwsmkvhdbn"
    trans_table = bytes.maketrans(intab, outtab)

    records = []
    
    # 2. Pass 1: Indexing offsets (O(1) Memory)
    try:
        with open(input_path, 'rb') as f:
            header = None
            seq_start = 0
            
            while True:
                offset_before = f.tell()
                line = f.readline()
                
                # End of file
                if not line:
                    if header is not None:
                        records.append((header, seq_start, offset_before))
                    break
                
                # Start of a new FASTA record
                if line.startswith(b'>'):
                    if header is not None:
                        records.append((header, seq_start, offset_before))
                    header = line.strip()
                    seq_start = f.tell()
                    
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # 3. Pass 2: Backwards Block Reading
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        for header, seq_start, seq_end in records:
            f_out.write(header + b'\n')
            
            p = seq_end
            buffer = bytearray()
            
            # Walk backwards from the end of the sequence to its start
            while p > seq_start:
                read_size = min(block_size, p - seq_start)
                p -= read_size
                f_in.seek(p)
                
                chunk = f_in.read(read_size)
                
                # Strip OS-specific newlines seamlessly
                chunk = chunk.replace(b'\n', b'').replace(b'\r', b'')
                
                # Reverse the byte sequence [::-1] and apply the complement translation
                rc_chunk = chunk[::-1].translate(trans_table)
                buffer.extend(rc_chunk)
                
                # Flush to disk in standard FASTA line lengths to maintain formatting
                while len(buffer) >= line_len:
                    f_out.write(buffer[:line_len] + b'\n')
                    # Efficient in-place bytearray mutation prevents memory bloat
                    del buffer[:line_len] 
                    
            # Write any remainder characters
            if buffer:
                f_out.write(buffer + b'\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute the reverse complement of a DNA FASTA file with O(1) memory."
    )
    parser.add_argument("input", help="Path to the input FASTA file")
    parser.add_argument("-o", "--output", default="output.fasta", help="Path to the output FASTA file")
    parser.add_argument("-b", "--block-size", type=int, default=65536, help="Disk read block size in bytes (default: 64KB)")
    parser.add_argument("-l", "--line-length", type=int, default=80, help="Output FASTA line length (default: 80)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
        
    process_fasta_optimized(args.input, args.output, args.block_size, args.line_length)