import sys

def generate_mandelbrot(N: int, max_iter: int = 255):
    # Standard bounds for the Mandelbrot set
    x_min, x_max = -2.0, 0.47
    y_min, y_max = -1.12, 1.12
    
    # Precompute structural constants to save CPU cycles inside the loop
    dx = (x_max - x_min) / (N - 1)
    dy = (y_max - y_min) / (N - 1)
    
    filename = "mandelbrot.pgm"
    
    # 'wb' opens the file in binary mode with OS-level buffering.
    # This prevents byte-by-byte SSD writes.
    with open(filename, 'wb') as f:
        # Write the Netpbm P5 header
        header = f"P5\n{N} {N}\n{max_iter}\n"
        f.write(header.encode('ascii'))
        
        # Process the image row by row
        for iy in range(N):
            # O(N) memory allocation: only one row exists in RAM at a time
            row = bytearray(N)
            cy = y_max - iy * dy
            
            for ix in range(N):
                cx = x_min + ix * dx
                zx, zy = 0.0, 0.0
                zx2, zy2 = 0.0, 0.0
                
                # The hot loop
                for i in range(max_iter):
                    # Escape condition: |z|^2 > 4
                    if zx2 + zy2 > 4.0:
                        row[ix] = i
                        break
                        
                    # z_{n+1} = z_n^2 + c
                    zy = 2.0 * zx * zy + cy
                    zx = zx2 - zy2 + cx
                    
                    # Cache squares for next iteration to reduce multiplications
                    zx2 = zx * zx
                    zy2 = zy * zy
                else:
                    # If the loop completes without breaking, the point is in the set
                    row[ix] = 0 
                    
            # Flush the computed row to the disk stream
            f.write(row)
            
    print(f"Successfully generated a {N}x{N} fractal at '{filename}'.")

if __name__ == "__main__":
    # Allows dynamic N-sizing via command line, defaulting to a 2000x2000 grid
    N_size = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    generate_mandelbrot(N_size)