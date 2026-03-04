import array
import sys

def mandelbrot_set(width, height, max_iter=256):
    """Generate Mandelbrot set as a 2D list of iteration counts"""
    result = [[0] * width for _ in range(height)]
    
    for y in range(height):
        # Map y coordinate to imaginary part (-1.25 to 1.25)
        im = (y - height / 2) / (height * 0.4)
        
        for x in range(width):
            # Map x coordinate to real part (-2 to 1)
            re = (x - width * 2 / 3) / (width * 0.4)
            
            # Quadratic recurrence: z₀ = 0, zₙ₊₁ = zₙ² + c
            z_real, z_imag = 0.0, 0.0
            c_real, c_imag = re, im
            
            for i in range(max_iter):
                # Calculate z² + c
                z_real_sq = z_real * z_real
                z_imag_sq = z_imag * z_imag
                
                # Check escape condition
                if z_real_sq + z_imag_sq > 4.0:
                    result[y][x] = i
                    break
                
                # Update z: z = z² + c
                z_real_new = z_real_sq - z_imag_sq + c_real
                z_imag = 2 * z_real * z_imag + c_imag
                z_real = z_real_new
                
                if i == max_iter - 1:
                    result[y][x] = max_iter
    
    return result

def save_pbm(filename, data, width, height):
    """Save data as PBM (Portable Bitmap) file"""
    with open(filename, 'wb') as f:
        # Write PBM header (P4 for binary PBM)
        f.write(f"P4\n{width} {height}\n".encode())
        
        # Convert to binary (1 bit per pixel)
        for y in range(height):
            byte = 0
            bit_pos = 7
            
            for x in range(width):
                # 1 for inside (max_iter), 0 for outside
                pixel = 1 if data[y][x] == 256 else 0
                byte |= (pixel << bit_pos)
                
                if bit_pos == 0:
                    f.write(bytes([byte]))
                    byte = 0
                    bit_pos = 7
                else:
                    bit_pos -= 1
            
            # Write last byte if needed
            if bit_pos != 7:
                f.write(bytes([byte]))

def main():
    width, height = 800, 600
    max_iter = 256
    
    print("Generating Mandelbrot set...")
    mandelbrot_data = mandelbrot_set(width, height, max_iter)
    
    print("Saving to mandelbrot.pbm...")
    save_pbm("mandelbrot.pbm", mandelbrot_data, width, height)
    
    print(f"Done! Image saved as mandelbrot.pbm ({width}x{height})")

if __name__ == "__main__":
    main()