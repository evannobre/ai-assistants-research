import sys

def generate_mandelbrot(n, max_iter=255, filename="mandelbrot.pgm"):
    """
    Generates a Mandelbrot set visualization in PGM (Portable Gray Map) format.
    
    Args:
        n (int): The width and height of the image (N x N).
        max_iter (int): Maximum number of iterations before assuming the point is in the set.
        filename (str): The output filename.
    """
    
    # 1. Define the Complex Plane bounds
    # The Mandelbrot set usually sits within Real: [-2.0, 1.0] and Imag: [-1.5, 1.5]
    min_re, max_re = -2.0, 1.0
    min_im, max_im = -1.5, 1.5
    
    # Calculate scale factors to map pixels to the complex plane
    re_factor = (max_re - min_re) / (n - 1)
    im_factor = (max_im - min_im) / (n - 1)

    print(f"Generating {n}x{n} Mandelbrot set to '{filename}'...")

    try:
        with open(filename, 'w') as f:
            # 2. Write the PGM Header
            # P2 indicates ASCII Grayscale
            # The next line is Width Height
            # The last number is the maximum pixel value (brightness)
            header = f"P2\n{n} {n}\n{max_iter}\n"
            f.write(header)

            # 3. Iterate over the grid
            for y in range(n):
                for x in range(n):
                    
                    # Map pixel coordinate (x, y) to Complex Number C
                    # Note: We invert y to orient the imaginary axis correctly (top is positive)
                    c_im = max_im - (y * im_factor)
                    c_re = min_re + (x * re_factor)
                    
                    # Native Python complex number
                    c = complex(c_re, c_im)
                    z = 0j
                    
                    # 4. The Recurrence Loop (z_n+1 = z_n^2 + C)
                    iteration = 0
                    while abs(z) <= 2.0 and iteration < max_iter:
                        z = z*z + c
                        iteration += 1
                    
                    # 5. Write pixel value
                    # If it finished all iterations, it's inside the set (Black: 0)
                    # If it escaped, use iteration count as brightness (White/Grey)
                    if iteration == max_iter:
                         # Inside the set -> Black
                        f.write("0 ")
                    else:
                        # Outside the set -> Brighter based on escape speed
                        f.write(f"{iteration} ")
                
                f.write("\n") # Newline at end of image row
                
        print("Done! Image saved successfully.")
        
    except IOError as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    # You can change N here to increase resolution (e.g., 1024)
    N = 512 
    generate_mandelbrot(N)