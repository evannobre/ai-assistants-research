#!/usr/bin/env python3
"""
mandelbrot_pbm.py

Generate an N-by-N PBM (portable bitmap, P4 binary) of the Mandelbrot set using
only Python's standard library. The program streams rows to disk (low memory)
and uses multiprocessing to utilize multiple CPU cores.

Usage:
    python3 mandelbrot_pbm.py --size 4096 --max-iter 1000 --out mandelbrot.pbm

Defaults are sensible for a typical desktop (center = -0.5+0j, scale=1.5).

Notes:
 - PBM P4 format: header "P4\n{width} {height}\n" followed by packed bits.
   Each bit corresponds to a pixel: 1 = black, 0 = white. We choose black for
   points that remain bounded (did not escape within max_iter).
 - Memory: rows are computed and written in-order; the program does not store
   the entire image in RAM. Memory usage ~ O(N) per worker for per-row buffers.
 - Performance: complexity O(N^2 * max_iter). Use more processes for faster
   compute, but avoid exceeding CPU count.

Author: Generated for Ubuntu 24.04.4 64-bit, target machine 8 GB RAM.
"""

from __future__ import annotations
import argparse
import math
import multiprocessing as mp
import sys
from typing import Iterable, Tuple


def mandelbrot_row_bytes(y: int, width: int, height: int, x_center: float,
                         y_center: float, scale: float, max_iter: int) -> bytes:
    """Compute one PBM row (packed bytes) for row index y.

    Returns a bytes object containing ceil(width/8) bytes.
    """
    # Map pixel coordinates to complex plane
    # Horizontal step (real), vertical step (imag)
    half = scale
    x_min = x_center - half
    x_max = x_center + half
    y_min = y_center - half
    y_max = y_center + half

    dx = (x_max - x_min) / (width - 1) if width > 1 else 0.0
    dy = (y_max - y_min) / (height - 1) if height > 1 else 0.0

    c_im = y_max - y * dy  # top row is y=0 -> imag=y_max

    packed = bytearray((width + 7) // 8)
    bit_index = 0
    byte_index = 0
    current_byte = 0

    for x in range(width):
        c_re = x_min + x * dx

        z_re = 0.0
        z_im = 0.0
        z_re2 = 0.0
        z_im2 = 0.0

        iter_count = 0
        # escape-time loop
        while iter_count < max_iter and (z_re2 + z_im2) <= 4.0:
            # z = z^2 + c ; (a+bi)^2 = (a^2 - b^2) + 2ab i
            z_im = 2.0 * z_re * z_im + c_im
            z_re = z_re2 - z_im2 + c_re
            z_re2 = z_re * z_re
            z_im2 = z_im * z_im
            iter_count += 1

        # Decide pixel color: 1 = black (inside / did not escape), 0 = white (escaped)
        inside = (iter_count >= max_iter)
        bit = 1 if inside else 0

        # Pack bit: PBM stores the most-significant bit first in each byte
        current_byte = (current_byte << 1) | bit
        bit_index += 1

        if bit_index == 8:
            packed[byte_index] = current_byte
            byte_index += 1
            bit_index = 0
            current_byte = 0

    # If final byte is not full, left-align remaining bits (pad least significant bits with zeros)
    if bit_index != 0:
        # shift the partial byte to the left so that we have MSB-first
        current_byte = current_byte << (8 - bit_index)
        packed[byte_index] = current_byte

    return bytes(packed)


def worker_task(args: Tuple[int, int, int, float, float, float, int]) -> bytes:
    y, width, height, x_center, y_center, scale, max_iter = args
    return mandelbrot_row_bytes(y, width, height, x_center, y_center, scale, max_iter)


def generate_pbm(width: int, height: int, x_center: float, y_center: float,
                 scale: float, max_iter: int, out_path: str, processes: int | None = None) -> None:
    header = f"P4\n{width} {height}\n".encode("ascii")

    # Create argument tuples for each row, keeping order
    row_args = ((y, width, height, x_center, y_center, scale, max_iter) for y in range(height))

    # Use multiprocessing.Pool.imap to preserve row order and stream to disk
    proc_count = processes or max(1, mp.cpu_count() - 1)
    proc_count = max(1, proc_count)

    with open(out_path, "wb") as f:
        f.write(header)

        if proc_count == 1:
            # Run single-threaded (useful for debugging / low-core machines)
            for args in row_args:
                row_bytes = worker_task(args)
                f.write(row_bytes)
        else:
            with mp.Pool(proc_count) as pool:
                for row_bytes in pool.imap(worker_task, row_args, chunksize=1):
                    f.write(row_bytes)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Mandelbrot PBM (P4 binary) using standard library.")
    p.add_argument("--size", "-s", type=int, default=1024, help="width and height in pixels (N).")
    p.add_argument("--out", "-o", type=str, default="mandelbrot.pbm", help="output PBM filename")
    p.add_argument("--max-iter", type=int, default=1000, help="maximum iterations for escape-time test")
    p.add_argument("--center", type=float, nargs=2, metavar=("X","Y"), default=[-0.5, 0.0],
                   help="center of the view in complex plane (real imag)")
    p.add_argument("--scale", type=float, default=1.5, help="half-width of the view (span = 2*scale)")
    p.add_argument("--processes", "-p", type=int, default=None, help="number of worker processes (default: cpu_count()-1)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    n = args.size
    out = args.out
    max_iter = args.max_iter
    x_center, y_center = args.center
    scale = args.scale
    processes = args.processes

    if n <= 0:
        print("Error: size must be positive", file=sys.stderr)
        sys.exit(2)

    print(f"Generating {n}x{n} PBM -> {out}")
    print(f"center=({x_center},{y_center}), scale={scale}, max_iter={max_iter}, processes={processes or 'auto'}")

    generate_pbm(n, n, x_center, y_center, scale, max_iter, out, processes)

    print("Done.")


if __name__ == '__main__':
    main()
