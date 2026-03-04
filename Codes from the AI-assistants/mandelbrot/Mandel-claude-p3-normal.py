#!/usr/bin/env python3
"""
Mandelbrot Set Generator
Plots the Mandelbrot set in the range [-1.5-i, 0.5+i] to PBM format
Uses quadratic recurrence: z_0 = 0, z_{n+1} = z_n^2 + C
"""

import sys
import numpy as np


def mandelbrot(size):
    """
    Generate Mandelbrot set bitmap using vectorized NumPy operations.
    
    Args:
        size: N-by-N bitmap dimension
    
    Returns:
        byte array in PBM format
    """
    # Maximum iterations
    max_iter = 50
    
    # Create coordinate arrays for the complex plane
    # Range: real [-1.5, 0.5], imaginary [-1.0, 1.0]
    y_coords = np.linspace(-1.0, 1.0, size)
    x_coords = np.linspace(-1.5, 0.5, size)
    
    # Create complex grid C
    C = x_coords[np.newaxis, :] + 1j * y_coords[:, np.newaxis]
    
    # Initialize z_0 = 0
    Z = np.zeros_like(C, dtype=np.complex128)
    
    # Track which points have escaped (|z| > 2)
    M = np.zeros(C.shape, dtype=np.uint8)
    
    # Iterate z_{n+1} = z_n^2 + C
    for i in range(max_iter):
        # Calculate next iteration only for points that haven't escaped
        mask = np.abs(Z) <= 2.0
        Z[mask] = Z[mask]**2 + C[mask]
    
    # Set pixels: 1 if in set (|z| <= 2), 0 if escaped
    M = (np.abs(Z) <= 2.0).astype(np.uint8)
    
    return M


def write_pbm(bitmap, size):
    """
    Write bitmap to stdout in portable bitmap (PBM) format.
    
    Args:
        bitmap: numpy array of 0s and 1s
        size: dimension of square bitmap
    """
    # Write PBM header
    sys.stdout.write(f"P4\n{size} {size}\n")
    sys.stdout.flush()
    
    # Pack 8 pixels per byte
    output = []
    for row in bitmap:
        byte_row = []
        for i in range(0, size, 8):
            # Get up to 8 pixels
            pixels = row[i:i+8]
            # Pad if necessary
            if len(pixels) < 8:
                pixels = np.pad(pixels, (0, 8 - len(pixels)), constant_values=0)
            
            # Pack into byte (MSB first)
            byte_val = 0
            for j, pixel in enumerate(pixels):
                if pixel:
                    byte_val |= (1 << (7 - j))
            
            byte_row.append(byte_val)
        
        output.extend(byte_row)
    
    # Write binary data
    sys.stdout.buffer.write(bytearray(output))
    sys.stdout.buffer.flush()


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python mandelbrot.py N", file=sys.stderr)
        print("  N: size of N-by-N bitmap", file=sys.stderr)
        sys.exit(1)
    
    try:
        size = int(sys.argv[1])
        if size <= 0:
            raise ValueError("Size must be positive")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate Mandelbrot set
    bitmap = mandelbrot(size)
    
    # Write to stdout in PBM format
    write_pbm(bitmap, size)


if __name__ == "__main__":
    main()
