import os
import sys
import argparse

def generate_translation_table():
    """
    Creates a translation table for DNA complements.
    Maps: A<->T, C<->G, N->N (and lowercase equivalents).
    """
    # Create a full byte table (0-255) mapped to itself initially
    tab = bytearray(range(256))
    
    # Define mapping pairs
    pairs = [
        (b'A', b'T'), (b'C', b'G'), (b'G', b'C'), (b'T', b'A'),
        (b'a', b't'), (b'c', b'g'), (b'g', b'c'), (b't', b'a'),
        (b'N', b'N'), (b'n', b'n')
    ]
    
    for src, dest in pairs:
        tab[src[0]] = dest[0]
        
    return bytes(tab)

def process_file_reverse(filepath, chunk_size=1024*1024):
    """
    Reads a file from end to start in chunks, translates, and prints.
    """
    trans_table = generate_translation_table()
    
    try:
        with open(filepath, 'rb') as f:
            # Move to end of file
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            position = file_size

            # Loop until we reach the start of the file
            while position > 0:
                # Calculate how much to read (chunk_size or whatever is left)
                read_size = min(chunk_size, position)
                position -= read_size
                
                # Move pointer to the start of the current chunk
                f.seek(position)
                
                # Read raw bytes
                chunk = f.read(read_size)
                
                # 1. Reverse the chunk
                # 2. Translate using the table
                # 3. Write to stdout
                # Note: We write binary directly to buffer to avoid decode/encode overhead
                sys.stdout.buffer.write(chunk[::-1].translate(trans_table))
                
    except FileNotFoundError:
        sys.stderr.write(f"Error: File '{filepath}' not found.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reverse Complement DNA Simulation")
    parser.add_argument("file", help="Path to the input DNA file")
    
    args = parser.parse_args()
    
    # Check if file exists before starting
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist.")
        sys.exit(1)

    process_file_reverse(args.file)