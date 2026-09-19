def generate_mandelbrot(N: int, max_iter: int, filename: str):
    # Standard coordinate bounds for the Mandelbrot set
    re_min, re_max = -2.0, 0.5
    im_min, im_max = -1.25, 1.25

    print(f"Generating {N}x{N} Mandelbrot set into '{filename}'...")

    with open(filename, 'w') as f:
        # 1. Write the PGM Header
        # "P2" defines an ASCII grayscale image format
        f.write("P2\n")
        f.write(f"# Mandelbrot Set N={N}\n")
        f.write(f"{N} {N}\n")
        # Maximum color value
        f.write(f"{max_iter}\n")

        # 2. Iterate over every pixel
        for y in range(N):
            # Map the Y pixel to the imaginary axis (top-down)
            im = im_max - (im_max - im_min) * y / (N - 1)
            
            for x in range(N):
                # Map the X pixel to the real axis (left-right)
                re = re_min + (re_max - re_min) * x / (N - 1)
                
                # Built-in complex number type in Python
                c = complex(re, im)
                z = 0j
                
                # 3. Calculate the recurrence equation
                for i in range(max_iter):
                    # If the magnitude exceeds 2, it escapes
                    if abs(z) > 2.0:
                        break
                    z = z*z + c
                else:
                    # If the loop finishes without breaking, it's in the set
                    i = max_iter
                
                # 4. Determine pixel intensity
                # Points inside the set (i == max_iter) become 0 (black).
                # Escaped points get lighter based on how fast they escaped.
                intensity = 0 if i == max_iter else max_iter - i
                
                # 5. Write the pixel data
                f.write(f"{intensity} ")
            
            # Newline after each row
            f.write("\n")
            
    print("Generation complete!")

# Run the simulation for a 1000x1000 image
if __name__ == "__main__":
    generate_mandelbrot(N=1000, max_iter=255, filename="mandelbrot.pgm")