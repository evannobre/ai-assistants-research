#!/usr/bin/env python3
"""
Mandelbrot Set Generator
Plots the Mandelbrot set for the region [-1.5-i, 0.5+i] on an N-by-N bitmap
Outputs in portable bitmap format (PBM)
Usage: python mandelbrot.py N > output.pbm
"""

import sys
import numpy as np

def mandelbrot(N, max_iter=50):
    """
    Calculate Mandelbrot set using the quadratic recurrence:
    z_0 = 0
    z_(n+1) = z_n^2 + C
    
    Args:
        N: Size of the N-by-N bitmap
        max_iter: Maximum iterations to test for divergence
    
    Returns:
        Binary bitmap as bytes
    """
    # Define the complex plane region [-1.5-i, 0.5+i]
    x_min, x_max = -1.5, 0.5
    y_min, y_max = -1.0, 1.0
    
    # Create coordinate arrays
    x = np.linspace(x_min, x_max, N)
    y = np.linspace(y_min, y_max, N)
    
    # Create complex grid C
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    
    # Initialize z_0 = 0
    Z = np.zeros_like(C, dtype=np.complex128)
    
    # Track which points are in the set (haven't diverged)
    M = np.ones(C.shape, dtype=bool)
    
    # Iterate the recurrence relation
    for i in range(max_iter):
        # Only update points that haven't diverged
        Z[M] = Z[M]**2 + C[M]
        
        # Mark points that have diverged (|z| > 2)
        M[np.abs(Z) > 2] = False
    
    # Convert to bitmap: True (in set) = 1 (black), False (escaped) = 0 (white)
    bitmap = M.astype(np.uint8)
    
    return bitmap

def write_pbm(bitmap):
    """
    Write bitmap in portable bitmap format (PBM) to stdout
    Format: P4 (binary PBM)
    """
    N = bitmap.shape[0]
    
    # Write PBM header
    sys.stdout.buffer.write(f"P4\n{N} {N}\n".encode('ascii'))
    
    # Pack bits into bytes (8 pixels per byte)
    for row in bitmap:
        # Pack 8 bits into each byte
        packed_row = np.packbits(row)
        sys.stdout.buffer.write(packed_row.tobytes())

def main():
    if len(sys.argv) != 2:
        print("Usage: python mandelbrot.py N", file=sys.stderr)
        print("  N: size of the N-by-N bitmap", file=sys.stderr)
        print("Example: python mandelbrot.py 16000 > output.pbm", file=sys.stderr)
        sys.exit(1)
    
    try:
        N = int(sys.argv[1])
        if N <= 0:
            raise ValueError("N must be positive")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate Mandelbrot set
    bitmap = mandelbrot(N)
    
    # Write to stdout in PBM format
    write_pbm(bitmap)

if __name__ == "__main__":
    main()
