import argparse
import sys
import numpy as np

def mandelbrot_iteration(c, max_iter=1000):
    """Calculate Mandelbrot iterations for a complex number."""
    z = 0j
    for n in range(max_iter):
        z = z * z + c
        if abs(z) > 2.0:
            return n
    return max_iter

def generate_mandelbrot(width, height, 
                        real_min=-2.0, real_max=1.0,
                        imag_min=-1.5, imag_max=1.5,
                        max_iter=1000):
    """Generate Mandelbrot set as a 2D array."""
    result = np.zeros((height, width), dtype=np.uint8)
    
    real_range = real_max - real_min
    imag_range = imag_max - imag_min
    
    for y in range(height):
        for x in range(width):
            real = real_min + (x * real_range) / (width - 1)
            imag = imag_min + (y * imag_range) / (height - 1)
            c = complex(real, imag)
            
            iterations = mandelbrot_iteration(c, max_iter)
            
            if iterations == max_iter:
                result[y, x] = 0  # Black for points in the set
            else:
                # Smooth coloring
                smooth_val = iterations + 1 - np.log(np.log(abs(c))) / np.log(2.0)
                result[y, x] = int(255 * (1.0 - smooth_val / max_iter))
    
    return result

def save_pbm(data, filename):
    """Save data as a PBM (Portable Bitmap) file."""
    height, width = data.shape
    
    with open(filename, 'wb') as f:
        # Write PBM header
        f.write(f'P5\n{width} {height}\n255\n'.encode())
        # Write binary data
        data.tofile(f)

def main():
    parser = argparse.ArgumentParser(description='Generate Mandelbrot set')
    parser.add_argument('-s', '--size', type=int, default=800,
                       help='Image size (N x N pixels)')
    parser.add_argument('-o', '--output', default='mandelbrot.pbm',
                       help='Output filename')
    parser.add_argument('-x', '--real-range', nargs=2, type=float,
                       default=[-2.0, 1.0], metavar=('MIN', 'MAX'),
                       help='Real axis range')
    parser.add_argument('-y', '--imag-range', nargs=2, type=float,
                       default=[-1.5, 1.5], metavar=('MIN', 'MAX'),
                       help='Imaginary axis range')
    parser.add_argument('-i', '--iterations', type=int, default=1000,
                       help='Maximum iterations')
    
    args = parser.parse_args()
    
    print(f"Generating Mandelbrot set...")
    print(f"Size: {args.size} x {args.size}")
    print(f"Region: Re[{args.real_range[0]}, {args.real_range[1]}], "
          f"Im[{args.imag_range[0]}, {args.imag_range[1]}]")
    
    data = generate_mandelbrot(
        args.size, args.size,
        args.real_range[0], args.real_range[1],
        args.imag_range[0], args.imag_range[1],
        args.iterations
    )
    
    save_pbm(data, args.output)
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()