import cmath

def generate_mandelbrot(size, max_iter):
    # PBM Header: P4 is binary, P1 is plain text (easier for debugging)
    # Using P1 for simplicity and native compatibility
    filename = "mandelbrot.pbm"
    
    with open(filename, 'w') as f:
        f.write(f"P1\n{size} {size}\n")
        
        for row in range(size):
            line = []
            for col in range(size):
                # Map pixel to complex plane
                # Real: -2.0 to 0.5, Imaginary: -1.25 to 1.25
                c = complex(-2.0 + (col / size) * 2.5, 
                            -1.25 + (row / size) * 2.5)
                z = 0j
                is_inside = 1 # 1 is black in PBM P1
                
                for i in range(max_iter):
                    # The Quadratic Recurrence
                    z = z*z + c
                    if abs(z) > 2:
                        is_inside = 0 # Escaped
                        break
                
                line.append(str(is_inside))
            
            # Write row by row to keep RAM usage low
            f.write(" ".join(line) + "\n")

if __name__ == "__main__":
    N = 1000  # Resolution
    MAX_ITERATIONS = 100
    print(f"Generating {N}x{N} Mandelbrot set...")
    generate_mandelbrot(N, MAX_ITERATIONS)
    print("Done. Saved as mandelbrot.pbm")