# mandelbrot_generator.py

import sys

def generate_mandelbrot(N=1000, max_iter=100):
    """
    Generates a Mandelbrot set and saves it as a PBM image file.

    Args:
        N (int): The width and height of the image in pixels.
        max_iter (int): The maximum number of iterations for each point.
    """
    # Define the region of the complex plane to render
    RE_START = -2
    RE_END = 1
    IM_START = -1.5
    IM_END = 1.5

    # PBM file header
    # P1 means it's an ASCII bitmap
    # The next line is width and height
    header = f'P1\n{N} {N}\n'
    
    # A list to hold all pixel data as strings '0' or '1'
    pixel_data = []

    # Loop through each pixel row (y-coordinate)
    for py in range(N):
        # Map the pixel y-coordinate to the imaginary part of C
        c_imag = IM_START + (py / N) * (IM_END - IM_START)
        
        # Loop through each pixel column (x-coordinate)
        for px in range(N):
            # Map the pixel x-coordinate to the real part of C
            c_real = RE_START + (px / N) * (RE_END - RE_START)
            
            # The complex number C for the current pixel
            c = complex(c_real, c_imag)
            
            # The starting z value is always 0
            z = 0
            
            iteration = 0
            # The core Mandelbrot iteration
            # We check magnitude squared to avoid a costly square root operation.
            # |z|^2 <= 4 is equivalent to |z| <= 2.
            while z.real**2 + z.imag**2 <= 4 and iteration < max_iter:
                z = z**2 + c
                iteration += 1

            # If the loop finished because we reached max_iter, the point is in the set (black)
            # Otherwise, it escaped (white)
            if iteration == max_iter:
                pixel_data.append('1') # 1 is black in PBM
            else:
                pixel_data.append('0') # 0 is white in PBM
        
        # Add a newline for readability in the output file (optional but good practice)
        pixel_data.append('\n')
        
        # Simple progress indicator
        print(f"Generating... {((py+1)/N)*100:.2f}% complete", end='\r')

    # Write to the PBM file
    try:
        with open('mandelbrot.pbm', 'w') as f:
            f.write(header)
            f.write(' '.join(pixel_data))
        print("\nSuccessfully created mandelbrot.pbm")
    except IOError as e:
        print(f"\nError writing to file: {e}")

if __name__ == '__main__':
    # You can optionally pass the size as a command-line argument
    image_size = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    generate_mandelbrot(N=image_size)