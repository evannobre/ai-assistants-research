def mandelbrot_pbm(n, max_iter=100):
    # PBM Header: P1 means Plain Monochrome, then width, height
    output = [f"P1\n{n} {n}"]
    
    # Define the complex plane boundaries
    x_min, x_max = -2.0, 0.5
    y_min, y_max = -1.25, 1.25

    for j in range(n):
        row = []
        for i in range(n):
            # Map pixel to complex coordinate c
            real = x_min + (i / n) * (x_max - x_min)
            imag = y_min + (j / n) * (y_max - y_min)
            c = complex(real, imag)
            
            z = 0j
            is_inside = 1 # Assume inside (black)
            
            for _ in range(max_iter):
                if abs(z) > 2:
                    is_inside = 0 # Escaped (white)
                    break
                z = z*z + c
            
            row.append(str(is_inside))
        output.append(" ".join(row))

    # Save to file
    with open("mandelbrot.pbm", "w") as f:
        f.write("\n".join(output))

# Run for a 500x500 image
mandelbrot_pbm(500)