#!/usr/bin/env python3
# Save as mandelbrot_pbm.py
# Usage:
#   python3 mandelbrot_pbm.py out.pbm N max_iter [xmin xmax ymin ymax]
# Example:
#   python3 mandelbrot_pbm.py mandelbrot.pbm 1024 1000 -2.0 1.0 -1.5 1.5

import sys
import math

def main():
    if len(sys.argv) < 4:
        print("Usage: {} out.pbm N max_iter [xmin xmax ymin ymax]".format(sys.argv[0]), file=sys.stderr)
        return 1

    outname = sys.argv[1]
    N = int(sys.argv[2])
    max_iter = int(sys.argv[3])

    if len(sys.argv) >= 8:
        xmin = float(sys.argv[4]); xmax = float(sys.argv[5])
        ymin = float(sys.argv[6]); ymax = float(sys.argv[7])
    else:
        xmin, xmax, ymin, ymax = -2.0, 1.0, -1.5, 1.5

    with open(outname, "wb") as f:
        f.write(b"P4\n%d %d\n" % (N, N))
        bytes_per_row = (N + 7) // 8

        for py in range(N):
            row = bytearray(bytes_per_row)
            ci = ymin + py * (ymax - ymin) / (N - 1)
            for px in range(N):
                cr = xmin + px * (xmax - xmin) / (N - 1)
                zr = 0.0
                zi = 0.0
                iter = 0
                while iter < max_iter:
                    zr2 = zr*zr
                    zi2 = zi*zi
                    if zr2 + zi2 > 4.0:
                        break
                    tmp = zr2 - zi2 + cr
                    zi = 2.0*zr*zi + ci
                    zr = tmp
                    iter += 1
                if iter >= max_iter: # inside -> black
                    bidx = px // 8
                    bit = 7 - (px % 8)
                    row[bidx] |= (1 << bit)
            f.write(row)

    return 0

if __name__ == "__main__":
    sys.exit(main())
