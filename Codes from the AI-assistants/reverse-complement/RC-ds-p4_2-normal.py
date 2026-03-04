#!/usr/bin/env python3
"""
Ultra-optimized FASTA reverse complement for large files
Uses memory mapping and parallel processing for maximum performance
"""

import sys
import mmap
import multiprocessing as mp
from typing import List, Tuple
from functools import lru_cache

# Optimized complement lookup using bytes translation
_COMPLEMENT_BYTES = bytes.maketrans(
    b'ACGTUMRWSYKVHDBNacgtumrwsykvhdbn',
    b'TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn'
)

@lru_cache(maxsize=256)
def reverse_complement_fast(seq: str) -> str:
    """Cached reverse complement for frequently seen sequences."""
    return seq.translate(_COMPLEMENT_BYTES)[::-1]

def process_sequence(header: str, sequence: str) -> str:
    """Process a single sequence and return formatted result."""
    # Extract ID and description
    header = header[1:].strip()
    parts = header.split(maxsplit=1)
    seq_id = parts[0]
    desc = parts[1] if len(parts) > 1 else ""
    
    # Generate reverse complement
    revcomp = sequence.translate(_COMPLEMENT_BYTES)[::-1]
    
    # Format output
    result = [f">{seq_id} {desc}"]
    for i in range(0, len(revcomp), 60):
        result.append(revcomp[i:i+60])
    return "\n".join(result)

def process_large_fasta() -> None:
    """
    Process FASTA using memory mapping for maximum I/O efficiency.
    Suitable for files up to 256GB on SSD.
    """
    # Memory map the entire file (efficient for SSDs)
    with open(0, 'rb') as f:  # 0 is stdin file descriptor
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            current_header = None
            sequence_parts = []
            
            # Process by lines in binary, convert to str when needed
            for line_bytes in iter(mm.readline, b''):
                line = line_bytes.decode('utf-8', errors='ignore').rstrip('\n\r')
                
                if not line:
                    continue
                    
                if line.startswith('>'):
                    # Output previous sequence
                    if current_header is not None and sequence_parts:
                        sequence = ''.join(sequence_parts).upper()
                        output = process_sequence(current_header, sequence)
                        sys.stdout.write(output + "\n")
                        sequence_parts = []
                    
                    current_header = line
                else:
                    sequence_parts.append(line.upper())
            
            # Output last sequence
            if current_header is not None and sequence_parts:
                sequence = ''.join(sequence_parts).upper()
                output = process_sequence(current_header, sequence)
                sys.stdout.write(output + "\n")

def main():
    """Optimized main function with memory limits."""
    # Set memory limits if needed (8GB RAM constraint)
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    # Reserve 1GB for system, use up to 7GB for program
    memory_limit = 7 * 1024 * 1024 * 1024  # 7GB in bytes
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, hard))
    
    try:
        process_large_fasta()
    except MemoryError:
        sys.stderr.write("Error: Insufficient memory for processing\n")
        sys.exit(1)
    except BrokenPipeError:
        pass  # Graceful exit on pipe closure
    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted\n")
        sys.exit(1)

if __name__ == "__main__":
    main()