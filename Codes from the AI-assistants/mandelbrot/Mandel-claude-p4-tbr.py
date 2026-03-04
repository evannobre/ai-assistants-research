#!/usr/bin/env python3
"""
Mandelbrot Set Generator - Optimized Back-end Implementation
Implements quadratic recurrence: z_(n+1) = z_n² + C
Output: Portable Bitmap Format (PBM P4)
"""

import sys
import numpy as np
from typing import BinaryIO


class MandelbrotGenerator:
    """
    High-performance Mandelbrot set generator using vectorized operations.
    
    Algorithm:
    - z_0 = 0
    - z_(n+1) = (z_n)^2 + C
    - Point is in set if |z_n| ≤ 2 after max_iterations
    """
    
    # Constants
    MAX_ITERATIONS = 50
    ESCAPE_RADIUS_SQ = 4.0  # 2^2 for |z| ≤ 2 check
    
    # Complex plane bounds: [-1.5-i, 0.5+i]
    REAL_MIN = -1.5
    REAL_MAX = 0.5
    IMAG_MIN = -1.0
    IMAG_MAX = 1.0
    
    def __init__(self, size: int):
        """
        Initialize generator with bitmap size.
        
        Args:
            size: N×N bitmap dimensions
        """
        self.size = size
        self.bytes_per_row = (size + 7) // 8  # Ceiling division for bit-packing
    
    def generate_coordinate_arrays(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Generate coordinate arrays for the complex plane.
        
        Returns:
            Tuple of (real_coords, imag_coords) as 1D arrays
        """
        # Linspace is more accurate than arange for floating point
        real = np.linspace(self.REAL_MIN, self.REAL_MAX, self.size, dtype=np.float64)
        imag = np.linspace(self.IMAG_MIN, self.IMAG_MAX, self.size, dtype=np.float64)
        return real, imag
    
    def compute_row(self, imag_val: float, real_coords: np.ndarray) -> np.ndarray:
        """
        Compute one row of the Mandelbrot set using vectorized operations.
        
        Args:
            imag_val: Imaginary component for this row
            real_coords: Array of real coordinates
            
        Returns:
            Boolean array where True = in set, False = escaped
        """
        # Initialize C = real + imag*i for entire row
        C = real_coords + 1j * imag_val
        
        # z_0 = 0 for all points
        z = np.zeros_like(C, dtype=np.complex128)
        
        # Track which points are still in the set
        in_set = np.ones(self.size, dtype=bool)
        
        # Iterate the recurrence relation
        for _ in range(self.MAX_ITERATIONS):
            # Only compute for points still in set (optimization)
            if not in_set.any():
                break
            
            # z_(n+1) = z_n² + C (vectorized)
            z[in_set] = z[in_set] * z[in_set] + C[in_set]
            
            # Check escape condition: |z|² > 4
            # Use real²+imag² to avoid sqrt (performance optimization)
            magnitude_sq = z.real * z.real + z.imag * z.imag
            in_set &= magnitude_sq <= self.ESCAPE_RADIUS_SQ
        
        return in_set
    
    def pack_bits(self, row_data: np.ndarray) -> bytes:
        """
        Pack boolean array into bytes (8 pixels per byte, MSB first).
        
        PBM format: 1 = black (in set), 0 = white (escaped)
        
        Args:
            row_data: Boolean array of size N
            
        Returns:
            Packed bytes
        """
        # Pad to multiple of 8
        padded_size = self.bytes_per_row * 8
        if len(row_data) < padded_size:
            row_data = np.pad(row_data, (0, padded_size - len(row_data)), 
                            constant_values=False)
        
        # Reshape into groups of 8 bits
        bits = row_data.reshape(-1, 8)
        
        # Pack 8 bits into bytes using bit shifting
        # MSB first: bit 0 → position 7, bit 1 → position 6, etc.
        weights = np.array([128, 64, 32, 16, 8, 4, 2, 1], dtype=np.uint8)
        packed = np.dot(bits.astype(np.uint8), weights)
        
        return packed.tobytes()
    
    def write_pbm_header(self, output: BinaryIO) -> None:
        """
        Write PBM P4 (binary) format header.
        
        Format:
        P4
        width height
        <binary data>
        """
        header = f"P4\n{self.size} {self.size}\n"
        output.write(header.encode('ascii'))
    
    def generate(self, output: BinaryIO) -> None:
        """
        Generate complete Mandelbrot set and write to output stream.
        
        Uses streaming approach to minimize memory usage for large N.
        
        Args:
            output: Binary output stream
        """
        # Write header
        self.write_pbm_header(output)
        
        # Generate coordinate arrays once
        real_coords, imag_coords = self.generate_coordinate_arrays()
        
        # Process row by row (streaming for memory efficiency)
        for imag_val in imag_coords:
            row_data = self.compute_row(imag_val, real_coords)
            packed_row = self.pack_bits(row_data)
            output.write(packed_row)


def main():
    """
    Entry point: Parse arguments and generate Mandelbrot set.
    
    Usage: python mandelbrot.py N > output.pbm
    """
    if len(sys.argv) != 2:
        print("Usage: python mandelbrot.py N", file=sys.stderr)
        print("Generates N×N Mandelbrot set in PBM format to stdout", file=sys.stderr)
        sys.exit(1)
    
    try:
        size = int(sys.argv[1])
        if size <= 0:
            raise ValueError("Size must be positive")
    except ValueError as e:
        print(f"Error: Invalid size argument - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Memory estimation (for validation)
    estimated_mb = (size * size) / (8 * 1024 * 1024)
    if estimated_mb > 250:  # Leave margin for overhead
        print(f"Warning: Output size ~{estimated_mb:.1f}MB may exceed available memory", 
              file=sys.stderr)
    
    # Generate to stdout (binary mode)
    generator = MandelbrotGenerator(size)
    
    # Use binary stdout for proper PBM output
    output = sys.stdout.buffer
    generator.generate(output)


if __name__ == "__main__":
    main()
