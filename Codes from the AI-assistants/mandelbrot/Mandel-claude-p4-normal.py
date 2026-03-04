#!/usr/bin/env python3
"""
High-performance Mandelbrot Set generator
Follows backend best practices with memory efficiency and performance optimization
"""

import sys
import array
from multiprocessing import Pool, cpu_count


def mandelbrot_pixel(args):
    """
    Calculate if a point belongs to Mandelbrot set using quadratic recurrence.
    z_0 = 0, z_(n+1) = (z_n)^2 + C
    
    Args:
        args: tuple of (x, y, n, max_iter)
    
    Returns:
        1 if point is in set (dark), 0 if not (light)
    """
    x, y, n, max_iter = args
    
    # Map pixel coordinates to complex plane [-1.5-i, 0.5+i]
    # Real range: [-1.5, 0.5] = 2.0 width
    # Imaginary range: [-1.0, 1.0] = 2.0 height
    cr = (2.5 * x / n) - 2.0
    ci = (2.0 * y / n) - 1.0
    
    # Initialize z_0 = 0
    zr = 0.0
    zi = 0.0
    
    # Iterate z_(n+1) = (z_n)^2 + C
    for i in range(max_iter):
        # Calculate (zr + zi*i)^2 = (zr^2 - zi^2) + (2*zr*zi)*i
        zr_tmp = zr * zr - zi * zi + cr
        zi = 2.0 * zr * zi + ci
        zr = zr_tmp
        
        # Check if |z| > 2 (escape condition)
        if zr * zr + zi * zi > 4.0:
            return 0
    
    return 1


def mandelbrot_row(args):
    """
    Process an entire row for better memory efficiency.
    
    Args:
        args: tuple of (y, n, max_iter)
    
    Returns:
        bytes object containing the row's bitmap data
    """
    y, n, max_iter = args
    row_bits = []
    
    for x in range(n):
        bit = mandelbrot_pixel((x, y, n, max_iter))
        row_bits.append(bit)
    
    # Convert bits to bytes (8 pixels per byte, MSB first)
    row_bytes = array.array('B')
    for byte_idx in range((n + 7) // 8):
        byte_val = 0
        for bit_idx in range(8):
            pixel_idx = byte_idx * 8 + bit_idx
            if pixel_idx < n:
                byte_val = (byte_val << 1) | row_bits[pixel_idx]
            else:
                # Pad with zeros if n is not multiple of 8
                byte_val = byte_val << 1
        row_bytes.append(byte_val)
    
    return row_bytes.tobytes()


def generate_mandelbrot(n, max_iter=50, use_multiprocessing=True):
    """
    Generate Mandelbrot set bitmap.
    
    Args:
        n: Size of N-by-N bitmap
        max_iter: Maximum iterations for escape check
        use_multiprocessing: Use all CPU cores for parallel processing
    
    Returns:
        bytes object containing complete PBM data
    """
    # PBM header: P4 (binary bitmap), width, height
    header = f"P4\n{n} {n}\n".encode('ascii')
    
    if use_multiprocessing and n >= 1000:
        # Use multiprocessing for large images
        num_processes = cpu_count()
        with Pool(processes=num_processes) as pool:
            # Process rows in parallel
            row_args = [(y, n, max_iter) for y in range(n)]
            row_results = pool.map(mandelbrot_row, row_args)
        
        # Combine all rows
        bitmap_data = b''.join(row_results)
    else:
        # Single-threaded for small images
        bitmap_data = b''.join(
            mandelbrot_row((y, n, max_iter)) for y in range(n)
        )
    
    return header + bitmap_data


def main():
    """
    Main entry point with argument validation and error handling.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <size>", file=sys.stderr)
        print(f"Example: {sys.argv[0]} 16000", file=sys.stderr)
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError("Size must be positive")
        
        # Memory check: estimate required memory
        # Bitmap size: (n * n / 8) bytes + overhead
        estimated_mb = (n * n / 8) / (1024 * 1024)
        if estimated_mb > 4096:  # Leave 4GB for system
            print(f"Warning: Estimated {estimated_mb:.1f}MB may exceed available memory", 
                  file=sys.stderr)
        
    except ValueError as e:
        print(f"Error: Invalid size argument - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate and write to stdout (binary mode)
    pbm_data = generate_mandelbrot(n)
    sys.stdout.buffer.write(pbm_data)


if __name__ == "__main__":
    main()