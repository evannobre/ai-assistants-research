#!/usr/bin/env python3
"""
mandelbrot_pbm.py
Generate an N x N PBM (P4) image of the Mandelbrot set using only Python stdlib.

Usage:
    python mandelbrot_pbm.py output.pbm N [max_iter] [x_min x_max y_min y_max]

Example:
    python mandelbrot_pbm.py mandelbrot.pbm 1024 256 -2.0 1.0 -1.5 1.5
"""

import sys
from math import isfinite

def mandelbrot_pbm(filename, N,
                   max_iter=200,
                   x_min=-2.0, x_max=1.0,
                   y_min=-1.5, y_max=1.5):
    if N <= 0:
        raise ValueError("N must be positive")

    # Ensure aspect ratio: if user supplied ranges mismatch, you may want to correct.
    # Here we assume caller gave appropriate ranges or defaults do.
    row_bytes = (N + 7) // 8  # bytes per row (pad to full byte)
    header = f"P4\n{N} {N}\n".encode("ascii")

    with open(filename, "wb") as f:
        f.write(header)

        for py in range(N):
            # map pixel y -> complex plane imaginary coordinate
            y = y_max - (py * (y_max - y_min) / (N - 1))  # top row -> y_max
            row = bytearray(row_bytes)

            for px in range(N):
                x = x_min + px * (x_max - x_min) / (N - 1)
                # escape-time iteration for z_{n+1} = z_n^2 + c
                zr = 0.0
                zi = 0.0
                zr2 = 0.0
                zi2 = 0.0

                escaped = False
                for i in range(max_iter):
                    # z = (zr + i*zi), z^2 = (zr^2 - zi^2) + i*(2*zr*zi)
                    zi = 2.0 * zr * zi + y
                    zr = zr2 - zi2 + x
                    zr2 = zr * zr
                    zi2 = zi * zi

                    if (zr2 + zi2) > 4.0:
                        escaped = True
                        break

                    # defensive check for NaN/Inf
                    if not (isfinite(zr) and isfinite(zi)):
                        escaped = True
                        break

                # PBM: 1 = black, 0 = white. We'll make 'inside' black (did NOT escape).
                bit_index = px % 8
                byte_index = px // 8
                mask = 1 << (7 - bit_index)  # MSB-first within each byte

                if not escaped:
                    # inside -> set bit to 1 (black)
                    row[byte_index] |= mask
                # else: outside -> leave bit 0 (white)

            f.write(row)

def parse_args_and_run():
    if len(sys.argv) < 3:
        print("Usage: python mandelbrot_pbm.py output.pbm N [max_iter] [x_min x_max y_min y_max]")
        sys.exit(1)

    out = sys.argv[1]
    N = int(sys.argv[2])
    max_iter = int(sys.argv[3]) if len(sys.argv) >= 4 else 200

    if len(sys.argv) >= 8:
        x_min = float(sys.argv[4]); x_max = float(sys.argv[5])
        y_min = float(sys.argv[6]); y_max = float(sys.argv[7])
    else:
        # defaults that give classic view (preserve square region)
        x_min, x_max, y_min, y_max = -2.0, 1.0, -1.5, 1.5

    mandelbrot_pbm(out, N, max_iter, x_min, x_max, y_min, y_max)
    print(f"Wrote {out} ({N}x{N}, max_iter={max_iter})")

if __name__ == "__main__":
    parse_args_and_run()
