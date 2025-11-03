#!/usr/bin/env python3
"""
Mandelbrot Set Generator
Implements: z_0 = 0, z_(n+1) = z_n^2 + C
Outputs: Portable Bitmap Format (PBM)
Region: [-1.5-i, 0.5+i]
"""

import sys
import numpy as np


def mandelbrot(size):
    """
    Generate Mandelbrot set for an N×N bitmap.
    
    Args:
        size: The size of the N×N output image
    
    Returns:
        A byte array representing the PBM image
    """
    # Define the complex plane region: [-1.5-i, 0.5+i]
    # Real axis: -1.5 to 0.5 (width = 2.0)
    # Imaginary axis: -1.0 to 1.0 (height = 2.0)
    
    # Create coordinate arrays
    real = np.linspace(-1.5, 0.5, size)
    imag = np.linspace(1.0, -1.0, size)  # Top to bottom
    
    # Create complex grid
    C = real[np.newaxis, :] + 1j * imag[:, np.newaxis]
    
    # Initialize z array (z_0 = 0)
    Z = np.zeros_like(C, dtype=np.complex128)
    
    # Result bitmap (1 = in set, 0 = not in set)
    M = np.ones(C.shape, dtype=np.uint8)
    
    # Maximum iterations
    max_iter = 50
    
    # Iterate the Mandelbrot equation
    for i in range(max_iter):
        # Mask for points that haven't escaped yet
        mask = M.astype(bool)
        
        # z_(n+1) = z_n^2 + C
        Z[mask] = Z[mask]**2 + C[mask]
        
        # Mark points that have escaped (|z| > 2)
        M[mask] = np.abs(Z[mask]) <= 2.0
    
    return M


def to_pbm(bitmap):
    """
    Convert bitmap to PBM format (P4 - binary).
    
    Args:
        bitmap: 2D numpy array of 1s and 0s
    
    Returns:
        Bytes representing the PBM file
    """
    height, width = bitmap.shape
    
    # PBM header
    header = f"P4\n{width} {height}\n".encode('ascii')
    
    # Pack bits into bytes (8 pixels per byte)
    # PBM format: 1 = black (in set), 0 = white (not in set)
    rows = []
    for row in bitmap:
        # Pad row to multiple of 8
        padded_length = ((width + 7) // 8) * 8
        padded_row = np.zeros(padded_length, dtype=np.uint8)
        padded_row[:width] = row
        
        # Pack 8 bits into each byte
        packed = np.packbits(padded_row)
        rows.append(packed.tobytes())
    
    return header + b''.join(rows)


def main():
    """Main entry point."""
    # Get size from command line argument
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <size>", file=sys.stderr)
        print(f"Example: {sys.argv[0]} 16000", file=sys.stderr)
        sys.exit(1)
    
    try:
        size = int(sys.argv[1])
        if size <= 0:
            raise ValueError("Size must be positive")
    except ValueError as e:
        print(f"Error: Invalid size argument - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate Mandelbrot set
    bitmap = mandelbrot(size)
    
    # Convert to PBM format
    pbm_data = to_pbm(bitmap)
    
    # Write to stdout (byte-by-byte)
    sys.stdout.buffer.write(pbm_data)


if __name__ == "__main__":
    main()