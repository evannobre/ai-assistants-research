def generate_mandelbrot_pbm(filename: str, N: int, max_iter: int = 100):
    """
    Generates an N-by-N Mandelbrot set as a Portable Bitmap (PBM) file.
    """
    # The standard region of the complex plane containing the Mandelbrot set
    re_min, re_max = -2.0, 0.5
    im_min, im_max = -1.25, 1.25
    
    # Calculate step sizes for mapping the N x N grid to the complex plane
    re_step = (re_max - re_min) / (N - 1)
    im_step = (im_max - im_min) / (N - 1)

    with open(filename, 'w') as f:
        # Write PBM Header
        f.write("P1\n")
        f.write(f"{N} {N}\n")
        
        # Iterate over every pixel
        for y in range(N):
            # Map y-coordinate to the imaginary axis
            im = im_min + y * im_step
            row_pixels = []
            
            for x in range(N):
                # Map x-coordinate to the real axis
                re = re_min + x * re_step
                
                # C is the coordinate in the complex plane
                c = complex(re, im)
                
                # z_0 = 0
                z = complex(0, 0)
                
                # Assume the point is inside the set until proven otherwise
                is_inside = True
                
                # Quadratic recurrence: z_(n+1) = z_n^2 + C
                for _ in range(max_iter):
                    z = z * z + c
                    
                    # If the magnitude of z exceeds 2, it escapes to infinity
                    if abs(z) > 2.0:
                        is_inside = False
                        break
                
                # 1 represents black (inside the set), 0 represents white (outside)
                row_pixels.append("1" if is_inside else "0")
            
            # Write the row to the file
            f.write(" ".join(row_pixels) + "\n")
            
    print(f"Successfully generated {filename} ({N}x{N})")

# Example Usage: Generate a 1000x1000 Mandelbrot image
if __name__ == "__main__":
    generate_mandelbrot_pbm("mandelbrot.pbm", N=1000, max_iter=100)