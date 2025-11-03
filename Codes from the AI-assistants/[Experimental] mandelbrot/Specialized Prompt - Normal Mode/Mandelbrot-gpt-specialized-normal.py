#!/usr/bin/env python3
"""
mandelbrot_pbm.py
Generate an N x N Mandelbrot set in binary PBM (P4) format using only Python stdlib.
Usage example:
    python3 mandelbrot_pbm.py --size 4096 --max-iter 1000 --out mandelbrot_4096.pbm
"""

import argparse
import math
from multiprocessing import Pool, cpu_count
from functools import partial

def parse_args():
    p = argparse.ArgumentParser(description="Render Mandelbrot to binary PBM (P4).")
    p.add_argument("--size", "-N", type=int, default=2048, help="Image size (N x N).")
    p.add_argument("--max-iter", "-m", type=int, default=1000, help="Max iterations.")
    p.add_argument("--xmin", type=float, default=-2.0, help="Min x (real).")
    p.add_argument("--xmax", type=float, default=1.0, help="Max x (real).")
    p.add_argument("--ymin", type=float, default=-1.5, help="Min y (imag).")
    p.add_argument("--ymax", type=float, default=1.5, help="Max y (imag).")
    p.add_argument("--out", "-o", type=str, default="mandelbrot.pbm", help="Output filename.")
    p.add_argument("--workers", "-w", type=int, default=cpu_count(), help="Number of worker processes.")
    return p.parse_args()

def in_period2_bulb(cx, cy):
    """Fast check: period-2 bulb centered at (-1,0) radius 1/4:
       if (x+1)^2 + y^2 <= (1/4)^2 then inside (will not escape)."""
    dx = cx + 1.0
    return (dx*dx + cy*cy) <= (0.25*0.25)

def compute_row(y_idx, N, xmin, xmax, ymin, ymax, max_iter):
    """
    Compute one row of PBM binary-packed bytes (MSB-first).
    Return (y_idx, bytes_row) so rows can be written in order.
    Pixel bit value: 1 => black (inside set), 0 => white (escaped).
    """
    row_bits = []
    y = ymin + (y_idx + 0.5) * (ymax - ymin) / N
    # Precompute real coord per column increment
    dx = (xmax - xmin) / N
    b = 0  # current byte accumulator
    bits_filled = 0
    out_bytes = bytearray()

    for x_idx in range(N):
        cx = xmin + (x_idx + 0.5) * dx
        # quick in-bulb test (cheap)
        if in_period2_bulb(cx, y):
            inside = True
        else:
            zx = 0.0
            zy = 0.0
            zx2 = 0.0
            zy2 = 0.0
            inside = True
            for _ in range(max_iter):
                # z = z^2 + c  -> (zx + i zy)^2 = (zx^2 - zy^2) + i*(2*zx*zy)
                zy = 2.0 * zx * zy + y
                zx = zx2 - zy2 + cx
                zx2 = zx * zx
                zy2 = zy * zy
                if zx2 + zy2 > 4.0:
                    inside = False
                    break

        bit = 1 if inside else 0
        # pack MSB-first
        b = (b << 1) | bit
        bits_filled += 1
        if bits_filled == 8:
            out_bytes.append(b)
            b = 0
            bits_filled = 0

    if bits_filled != 0:
        # shift remaining bits to MSB positions and pad the rest with zeros
        b = b << (8 - bits_filled)
        out_bytes.append(b)

    return (y_idx, bytes(out_bytes))

def row_generator(N, xmin, xmax, ymin, ymax, max_iter, workers):
    """Yield rows (in order) as bytes using a process pool streaming (imap)."""
    with Pool(processes=workers) as pool:
        func = partial(compute_row, N=N, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, max_iter=max_iter)
        # imap yields results in order, streaming (does not accumulate all results)
        for result in pool.imap(func, range(N), chunksize=1):
            yield result  # (y_idx, bytes_row)

def main():
    args = parse_args()
    N = args.size
    max_iter = args.max_iter
    xmin, xmax, ymin, ymax = args.xmin, args.xmax, args.ymin, args.ymax

    # PBM P4 header:
    # P4\n<width> <height>\n<binary data...>
    header = f"P4\n{N} {N}\n".encode("ascii")

    # Write file and stream rows as they are computed
    with open(args.out, "wb") as f:
        f.write(header)
        # Consume row_generator which yields (y_idx, row_bytes) in order
        for y_idx, row_bytes in row_generator(N, xmin, xmax, ymin, ymax, max_iter, args.workers):
            f.write(row_bytes)

    print(f"Wrote {args.out} ({N}x{N}), max_iter={max_iter}, workers={args.workers}")

if __name__ == "__main__":
    main()
