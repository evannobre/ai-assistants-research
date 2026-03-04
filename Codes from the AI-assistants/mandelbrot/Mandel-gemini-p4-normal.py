import sys
from multiprocessing import Pool

def calculate_row(y, n, max_iter=50):
    """Calculates a single row of the Mandelbrot set."""
    row_bytes = bytearray(n // 8)
    # Map y-coordinate to the complex plane
    cy = 2.0 * y / n - 1.0
    
    for x in range(n):
        # Map x-coordinate to the complex plane
        cx = 2.0 * x / n - 1.5
        
        # Initial values for the quadratic recurrence
        # z = z^2 + c -> (x + iy)^2 + (cx + icy)
        zx, zy = 0.0, 0.0
        is_inside = 1
        
        for _ in range(max_iter):
            zx2 = zx * zx
            zy2 = zy * zy
            if zx2 + zy2 > 4.0:
                is_inside = 0
                break
            zy = 2.0 * zx * zy + cy
            zx = zx2 - zy2 + cx
            
        if is_inside:
            # Set the bit (PBM: 1 is black/inside, 0 is white/outside)
            row_bytes[x >> 3] |= (128 >> (x & 7))
            
    return row_bytes

def main():
    # Use command line argument or default to 16000
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16000
    
    # PBM Header: P4 (binary), width, height
    sys.stdout.buffer.write(f"P4\n{n} {n}\n".encode())

    # Utilize Pool for parallel execution across CPU cores
    # This respects the 8GB RAM by processing in chunks
    with Pool() as pool:
        # We process rows and write them to stdout immediately
        for row_data in pool.starmap(calculate_row, [(y, n) for y in range(n)]):
            sys.stdout.buffer.write(row_data)

if __name__ == "__main__":
    main()