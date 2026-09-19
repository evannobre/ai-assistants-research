#!/usr/bin/env python3
import sys

def generate_mandelbrot_pbm(filename: str, N: int, max_iter: int):
    # Standard complex plane boundaries for the Mandelbrot set
    x_min, x_max = -2.0, 0.47
    y_min, y_max = -1.12, 1.12
    
    print(f"Generating an {N}x{N} Mandelbrot set to '{filename}'...")
    print(f"Memory efficient streaming enabled. Max iterations: {max_iter}")

    # Open file for writing text. We stream directly to the SSD.
    with open(filename, 'w') as f:
        # Write the PBM P1 header (Plaintext ASCII Binary Image)
        f.write(f"P1\n{N} {N}\n")
        
        for row in range(N):
            # Map the current row to the imaginary axis (y)
            y = y_min + (y_max - y_min) * (row / (N - 1))
            
            line_buffer = []
            for col in range(N):
                # Map the current column to the real axis (x)
                x = x_min + (x_max - x_min) * (col / (N - 1))
                
                c = complex(x, y)
                z = complex(0, 0)
                is_inside = "1" # Default to black (inside the set)
                
                # The quadratic recurrence loop
                for _ in range(max_iter):
                    z = z * z + c
                    # Escape condition: distance from origin > 2
                    if abs(z) > 2.0:
                        is_inside = "0" # White (escaped)
                        break
                        
                line_buffer.append(is_inside)
            
            # Write the completed row to disk, clearing it from RAM
            f.write(" ".join(line_buffer) + "\n")
            
            # Simple progress indicator
            if row % (N // 10 or 1) == 0:
                print(f"Progress: {(row / N) * 100:.0f}%")
                
    print("100% - Rendering complete!")

if __name__ == "__main__":
    # Parameters that comfortably fit your 256GB SSD
    # N=2000 creates a 2000x2000 image (~8MB file size)
    GRID_SIZE = 2000 
    ITERATIONS = 100
    OUTPUT_FILE = "mandelbrot.pbm"
    
    generate_mandelbrot_pbm(OUTPUT_FILE, GRID_SIZE, ITERATIONS)