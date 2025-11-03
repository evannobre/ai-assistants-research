#!/usr/bin/env python3
"""
mandelbrot_pbm.py
Produces a binary PBM (P4) to stdout for the rectangle [-1.5 - i, 0.5 + i].
Usage: python mandelbrot_pbm.py [N]  (default N = 16000)
"""

import sys

def mandelbrot_pbm(N, max_iter=50):
    # region bounds
    real_min, real_max = -1.5, 0.5
    imag_min, imag_max = -1.0, 1.0

    # precompute increments
    if N <= 1:
        dx = dy = 0.0
    else:
        dx = (real_max - real_min) / (N - 1)
        dy = (imag_max - imag_min) / (N - 1)

    out = sys.stdout.buffer
    # PBM header (binary)
    out.write(f"P4\n{N} {N}\n".encode('ascii'))

    # For each row
    for py in range(N):
        cy = imag_max - py * dy  # top -> bottom
        row_bytes = bytearray()
        byte = 0
        bits_filled = 0  # accumulate bits MSB-first

        # For each column
        cx = real_min
        for px in range(N):
            zx = zy = 0.0
            zx2 = zy2 = 0.0
            escaped = False

            # iterate
            for _ in range(max_iter):
                zy = 2.0 * zx * zy + cy
                zx = zx2 - zy2 + cx
                zx2 = zx * zx
                zy2 = zy * zy
                if zx2 + zy2 > 4.0:
                    escaped = True
                    break

            # PBM: 1 = black (inside), 0 = white (escaped)
            bit = 0 if escaped else 1

            # pack MSB-first
            byte = (byte << 1) | bit
            bits_filled += 1

            if bits_filled == 8:
                row_bytes.append(byte & 0xFF)
                byte = 0
                bits_filled = 0

            cx += dx

        # pad last partial byte (if any) by shifting left to fill 8 bits
        if bits_filled != 0:
            byte = byte << (8 - bits_filled)
            row_bytes.append(byte & 0xFF)

        out.write(row_bytes)

def main():
    if len(sys.argv) > 1:
        try:
            N = int(sys.argv[1])
        except ValueError:
            print("N must be an integer", file=sys.stderr)
            sys.exit(1)
    else:
        N = 16000

    # Tune max_iter if you want more detail (higher value) or faster (lower).
    # The classic benchmark uses 50; you can experiment.
    mandelbrot_pbm(N, max_iter=50)

if __name__ == "__main__":
    main()
