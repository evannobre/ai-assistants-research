def generate_mandelbrot_pbm(N, max_iter, filename="mandelbrot.pbm"):
    """
    Generate a Mandelbrot set and save as PBM format
    """
    # Define the complex plane region
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5
    
    x_step = (x_max - x_min) / (N - 1)
    y_step = (y_max - y_min) / (N - 1)
    
    with open(filename, 'w') as f:
        # Write PBM header
        f.write(f"P1\n{N} {N}\n")
        
        for i in range(N):
            row = []
            for j in range(N):
                # Convert pixel coordinates to complex number
                c = complex(x_min + j * x_step, y_min + i * y_step)
                
                # Mandelbrot iteration
                z = 0j
                for iteration in range(max_iter):
                    z = z * z + c
                    if abs(z) > 2.0:
                        break
                
                # 1 for in set (black), 0 for out of set (white)
                pixel = 1 if iteration == max_iter - 1 else 0
                row.append(str(pixel))
            
            f.write(" ".join(row) + "\n")
    
    print(f"Mandelbrot set saved to {filename}")

# Usage
if __name__ == "__main__":
    generate_mandelbrot_pbm(800, 1000)