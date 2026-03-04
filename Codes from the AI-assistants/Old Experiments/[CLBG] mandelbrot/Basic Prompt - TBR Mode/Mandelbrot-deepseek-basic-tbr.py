import sys
import array

def mandelbrot(N, filename):
    # Precompute constants
    x_min, x_max = -1.5, 0.5
    y_min, y_max = -1.0, 1.0
    x_step = (x_max - x_min) / (N - 1)
    y_step = (y_max - y_min) / (N - 1)
    
    max_iter = 1000
    
    with open(filename, 'wb') as f:
        # Write PBM header
        f.write(f"P4\n{N} {N}\n".encode())
        
        # Process image row by row
        for y in range(N):
            c_imag = y_min + y * y_step
            row_bytes = array.array('B')
            byte = 0
            bit_count = 0
            
            for x in range(N):
                c_real = x_min + x * x_step
                z_real, z_imag = 0.0, 0.0
                iter_count = 0
                
                # Quadratic recurrence
                while iter_count < max_iter:
                    z_real_sq = z_real * z_real
                    z_imag_sq = z_imag * z_imag
                    
                    if z_real_sq + z_imag_sq > 4.0:
                        break
                    
                    # z_{n+1} = z_n^2 + c
                    new_real = z_real_sq - z_imag_sq + c_real
                    new_imag = 2 * z_real * z_imag + c_imag
                    z_real, z_imag = new_real, new_imag
                    iter_count += 1
                
                # Pack bits into bytes
                byte <<= 1
                if iter_count == max_iter:
                    byte |= 1  # Inside set (black)
                
                bit_count += 1
                if bit_count == 8:
                    row_bytes.append(byte)
                    byte = 0
                    bit_count = 0
            
            # Handle partial byte at end of row
            if bit_count > 0:
                byte <<= (8 - bit_count)
                row_bytes.append(byte)
            
            row_bytes.tofile(f)

if __name__ == "__main__":
    N = 16000
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
    
    mandelbrot(N, "mandelbrot.pbm")