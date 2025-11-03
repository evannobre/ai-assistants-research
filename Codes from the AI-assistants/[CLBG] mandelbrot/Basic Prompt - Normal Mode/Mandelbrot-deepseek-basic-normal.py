import sys
import math

def mandelbrot(size, max_iter=1000):
    """Generate Mandelbrot set and output as PBM"""
    sys.stdout.buffer.write(f"P4\n{size} {size}\n".encode())
    
    y_step = 2.0 / size
    x_step = 2.0 / size
    bytes_per_row = (size + 7) // 8
    
    for y in range(size):
        c_im = -1.0 + y * y_step
        byte = 0
        bit_pos = 0
        
        for x in range(size):
            c_re = -1.5 + x * x_step
            c = complex(c_re, c_im)
            
            # Optimization: check main cardioid and period-2 bulb
            q = (c.real - 0.25) ** 2 + c.imag ** 2
            if q * (q + (c.real - 0.25)) <= 0.25 * c.imag ** 2 or \
               (c.real + 1) ** 2 + c.imag ** 2 <= 0.0625:
                iter_count = max_iter
            else:
                # Standard iteration
                z = complex(0, 0)
                iter_count = 0
                while iter_count < max_iter and z.real * z.real + z.imag * z.imag <= 4.0:
                    z = z * z + c
                    iter_count += 1
            
            # Set bit if in Mandelbrot set
            if iter_count == max_iter:
                byte |= (1 << (7 - bit_pos))
            
            bit_pos += 1
            if bit_pos == 8 or x == size - 1:
                sys.stdout.buffer.write(bytes([byte]))
                byte = 0
                bit_pos = 0

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    mandelbrot(size)