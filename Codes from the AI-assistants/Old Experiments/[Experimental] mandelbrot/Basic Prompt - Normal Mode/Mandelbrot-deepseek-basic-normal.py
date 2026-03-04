import array
import math

def mandelbrot_iterations(c, max_iter):
    """
    Calculate the number of iterations for a complex point c
    Returns the number of iterations until escape or max_iter if in set
    """
    z = complex(0, 0)
    for i in range(max_iter):
        if abs(z) > 2.0:
            return i
        z = z * z + c
    return max_iter

def generate_mandelbrot_pbm(filename, width, height, x_min, x_max, y_min, y_max, max_iter):
    """
    Generate a PBM file of the Mandelbrot set
    """
    with open(filename, 'wb') as f:
        # Write PBM header
        header = f"P1\n{width} {height}\n"
        f.write(header.encode('ascii'))
        
        # Generate Mandelbrot data
        for y in range(height):
            row = array.array('B')
            im = y_min + (y_max - y_min) * y / (height - 1)
            
            for x in range(width):
                re = x_min + (x_max - x_min) * x / (width - 1)
                c = complex(re, im)
                
                iter_count = mandelbrot_iterations(c, max_iter)
                
                # 1 for points in Mandelbrot set, 0 for points outside
                pixel = 1 if iter_count == max_iter else 0
                row.append(pixel)
            
            # Write row as space-separated ASCII values
            row_str = ' '.join(map(str, row)) + '\n'
            f.write(row_str.encode('ascii'))

def main():
    width = 800
    height = 600
    max_iter = 1000
    
    # Define the region to plot
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.0, 1.0
    
    generate_mandelbrot_pbm("mandelbrot.pbm", width, height, 
                           x_min, x_max, y_min, y_max, max_iter)
    
    print("Mandelbrot set saved to mandelbrot.pbm")

if __name__ == "__main__":
    main()