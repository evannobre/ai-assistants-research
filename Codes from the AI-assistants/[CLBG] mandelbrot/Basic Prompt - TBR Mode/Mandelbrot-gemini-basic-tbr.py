# The Computer Language Benchmarks Game
# https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
#
# Contributed by Tupteq
# Corrected by Peter Zotov
#
# Original C source code by Ton Voon, used with permission.

import sys

def main():
    """
    Generates a Mandelbrot set image and prints it to standard output.
    The image size is determined by a command-line argument.
    """
    try:
        n = int(sys.argv[1])
    except (IndexError, ValueError):
        n = 200 # Default size if no argument is provided

    # Define the complex plane coordinates to plot
    x_min, x_max = -1.5, 0.5
    y_min, y_max = -1.0, 1.0
    
    # Calculate the step size for each pixel
    dx = (x_max - x_min) / n
    dy = (y_max - y_min) / n
    
    # Set the maximum number of iterations
    max_iter = 50
    limit_sq = 4.0

    # Write the PBM header to standard output.
    # 'P4' is the magic number for a binary bitmap.
    # The next two numbers are width and height.
    sys.stdout.buffer.write(f"P4\n{n} {n}\n".encode())

    # Iterate over each row of the image (from top to bottom)
    for y_idx in range(n):
        # Create a bytearray to store one row of packed pixel data
        row_bits = bytearray( (n + 7) // 8 )
        
        # Calculate the imaginary component 'Ci' for this row
        ci = y_min + y_idx * dy
        
        # Iterate over each column of the image (from left to right)
        for x_idx in range(n):
            # Calculate the real component 'Cr' for this column
            cr = x_min + x_idx * dx
            
            # Initialize the complex number Z for the recurrence relation
            zr, zi = 0.0, 0.0
            
            # This bit will be set if the point is outside the set
            bit = 1 

            # Start the iteration process
            for _ in range(max_iter):
                # Calculate Z = Z^2 + C
                zr, zi = zr * zr - zi * zi + cr, 2.0 * zr * zi + ci
                
                # Check if the point has escaped (magnitude squared > 4)
                if zr * zr + zi * zi > limit_sq:
                    bit = 0 # Point is outside the set
                    break
            
            # Pack the bit into the correct byte in the row_bits array
            if bit:
                byte_index = x_idx // 8
                bit_index = 7 - (x_idx % 8)
                row_bits[byte_index] |= (1 << bit_index)

        # Write the packed row data to standard output
        sys.stdout.buffer.write(row_bits)

if __name__ == "__main__":
    main()
