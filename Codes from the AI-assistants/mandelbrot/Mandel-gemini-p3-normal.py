import sys
from multiprocessing import Pool

def compute_row(y, n, limit=4.0, max_iter=50):
    """Computes one row of the Mandelbrot set."""
    row_bytes = bytearray()
    byte_acc = 0
    bit_num = 0
    
    # Map y-coordinate to the imaginary range [-1.0, 1.0]
    ci = 2.0 * y / n - 1.0
    
    for x in range(n):
        # Map x-coordinate to the real range [-1.5, 0.5]
        cr = 2.0 * x / n - 1.5
        zr, zi = 0.0, 0.0
        tr, ti = 0.0, 0.0
        
        # Core recurrence: z = z^2 + c
        for i in range(max_iter):
            zi = 2.0 * zr * zi + ci
            zr = tr - ti + cr
            tr = zr * zr
            ti = zi * zi
            if tr + ti > limit:
                break
        else:
            # Point is likely in the set
            byte_acc |= (1 << (7 - bit_num))
        
        bit_num += 1
        if bit_num == 8:
            row_bytes.append(byte_acc)
            byte_acc = 0
            bit_num = 0
            
    # Handle remaining bits if N is not a multiple of 8
    if bit_num != 0:
        row_bytes.append(byte_acc)
        
    return row_bytes

def main():
    # Get N from command line, default to 200 for testing
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    
    # PBM Header: P4 means binary bitmap
    sys.stdout.buffer.write(f'P4\n{n} {n}\n'.encode())

    # Use a process pool to calculate rows in parallel
    with Pool() as pool:
        # Map the work across available CPU cores
        rows = pool.starmap(compute_row, [(y, n) for y in range(n)])
        
        # Write results to stdout byte-by-byte
        for row in rows:
            sys.stdout.buffer.write(row)

if __name__ == '__main__':
    main()