import sys
import os

# --- Constants for the specified Mandelbrot domain ---
# Domain: [-1.5 - i, 0.5 + i]
R_MIN = -1.5
R_MAX = 0.5
I_MIN = -1.0
I_MAX = 1.0

# Maximum number of iterations (the color depth). Higher values give better detail.
MAX_ITER = 50 
# The squared escape radius (r^2 = 2^2 = 4). We use squared values to avoid slow square root calculations.
ESCAPE_RADIUS_SQ = 4.0

def mandelbrot_check(Cr, Ci, max_iter):
    """
    Performs the quadratic recurrence z_{n+1} = z_n^2 + C check.
    
    Args:
        Cr (float): Real component of the complex constant C.
        Ci (float): Imaginary component of the complex constant C.
        max_iter (int): Maximum iterations before assuming convergence.
        
    Returns:
        bool: True if the point C escapes (is NOT in the set), False otherwise (is in the set).
    """
    Zr, Zi = 0.0, 0.0
    
    # We unroll the complex multiplication (Zr + i*Zi)^2 + (Cr + i*Ci)
    # (A + iB)^2 = A^2 - B^2 + i(2AB)
    # New Zr = Zr^2 - Zi^2 + Cr
    # New Zi = 2 * Zr * Zi + Ci
    
    for _ in range(max_iter):
        # Calculate the next iteration's squared magnitude (r^2)
        Zr_sq = Zr * Zr
        Zi_sq = Zi * Zi
        magnitude_sq = Zr_sq + Zi_sq
        
        if magnitude_sq > ESCAPE_RADIUS_SQ:
            # The point C escapes (diverges)
            return True
        
        # Calculate the next Z value
        # Store old Zr because it is needed for New Zi calculation
        Zr_next = Zr_sq - Zi_sq + Cr
        Zi = 2.0 * Zr * Zi + Ci
        Zr = Zr_next
        
    # If the loop completes, the point C is considered to be in the set.
    return False

def generate_mandelbrot_pbm(N):
    """
    Generates the N x N Mandelbrot set bitmap in PBM P4 (packed binary) format.
    
    Args:
        N (int): The size of the square bitmap (N rows, N columns).
    """
    
    print(f"Generating Mandelbrot set for N={N}...")
    
    # Calculate the step size for real and imaginary axes
    R_STEP = (R_MAX - R_MIN) / N
    I_STEP = (I_MAX - I_MIN) / N
    
    # PBM Header (P4 format, width N, height N)
    # We write to stdout, as is common for PBM benchmark utilities.
    sys.stdout.buffer.write(f"P4\n{N} {N}\n".encode('ascii'))
    
    # Pixel counter for packing 8 pixels into one byte
    pixel_bit_count = 0
    # The byte currently being constructed
    current_byte = 0
    
    # Iterate over the grid (row by row, column by column)
    for y in range(N):
        Ci = I_MIN + y * I_STEP
        
        for x in range(N):
            Cr = R_MIN + x * R_STEP
            
            # 1. Determine if C escapes
            escaped = mandelbrot_check(Cr, Ci, MAX_ITER)
            
            # 2. Convert result to a single bit (1=black, 0=white)
            # In PBM P4: 1 is black (in the set), 0 is white (escaped)
            # This is inverted from the boolean result.
            pixel_value = 0 if escaped else 1

            # 3. Pack the bit into the current byte
            # Shift the existing byte 1 place left (making space for the new bit)
            # OR the new bit (0 or 1) into the least significant position
            current_byte = (current_byte << 1) | pixel_value
            pixel_bit_count += 1
            
            # 4. Write the byte when 8 bits are collected
            if pixel_bit_count == 8:
                sys.stdout.buffer.write(bytes([current_byte]))
                pixel_bit_count = 0
                current_byte = 0
        
        # 5. Flush any remaining bits at the end of the row
        # This handles cases where N is not divisible by 8.
        if pixel_bit_count > 0:
            # Pad the remaining bits with zeros (i.e., white pixels)
            current_byte = current_byte << (8 - pixel_bit_count)
            sys.stdout.buffer.write(bytes([current_byte]))
            pixel_bit_count = 0
            current_byte = 0

def main():
    """
    Main function to parse the command line argument N.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {os.path.basename(sys.argv[0])} <N>", file=sys.stderr)
        print("Example: python3 mandelbrot_pbm.py 16000 > mandelbrot.pbm", file=sys.stderr)
        sys.exit(1)
    
    try:
        N = int(sys.argv[1])
        if N <= 0:
            raise ValueError("N must be a positive integer.")
    except ValueError as e:
        print(f"Error: Invalid argument N. {e}", file=sys.stderr)
        sys.exit(1)
        
    generate_mandelbrot_pbm(N)

if __name__ == "__main__":
    main()
